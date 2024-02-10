from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib.auth.models import User , auth
from django.contrib.auth import logout
from django.contrib import messages
from .models import Book, Cart, CartItem, Transaction
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal
import json


# Create your views here.
def index(request):
    # Retrieve a random selection of books from the database
    random_books = Book.objects.order_by('?')[:5]  # Adjust the number as needed

    return render(request, 'index.html', {'random_books': random_books})


def search_books(request):
    query = request.GET.get('q')
    if query:
        search_results = Book.objects.filter(title__icontains=query)
    else:
        search_results = Book.objects.all()
    
    # Serialize the queryset into JSON format
    search_results_json = serializers.serialize('json', search_results)

    # Return JSON response with search results
    return JsonResponse({'search_results': search_results_json})


@require_POST
@csrf_exempt
def update_cart_item(request):
    if request.user.is_authenticated:
        # Get the item ID and new quantity from the AJAX request
        item_id = request.POST.get('item_id')
        new_quantity = int(request.POST.get('quantity'))

        # Query the cart item to update its quantity
        try:
            cart_item = CartItem.objects.get(pk=item_id)
            
            # Check if the requested quantity exceeds the stock quantity
            if new_quantity > cart_item.book.stock_quantity:
                return JsonResponse({'message': 'Requested quantity exceeds available stock'}, status=400)
            
            # Update the quantity and save the cart item
            cart_item.quantity = new_quantity
            cart_item.save()
            return JsonResponse({'message': 'Quantity updated successfully'})
        except CartItem.DoesNotExist:
            return JsonResponse({'message': 'Item not found'}, status=404)
    else:
        return JsonResponse({'message': 'Please log in to perform this action'}, status=401)


@login_required
@require_POST
@csrf_exempt
def add_to_cart(request, book_id):
    try:
        book = get_object_or_404(Book, pk=book_id)
        
        # Check if the book is in stock
        if book.stock_quantity <= 0:
            return JsonResponse({'message': 'Book is out of stock'}, status=400)

        user_cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if the book is already in the user's cart
        cart_item, item_created = CartItem.objects.get_or_create(book=book, cart=user_cart)
        
        # Check if the quantity being added exceeds the available stock quantity
        if not item_created and cart_item.quantity >= book.stock_quantity:
            return JsonResponse({'message': 'Exceeds available stock quantity'}, status=400)

        # If the cart item already exists, increment its quantity
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()

        # Add the cart item to the user's cart
        user_cart.items.add(cart_item)
        return JsonResponse({'message': 'Book added to cart successfully'})
    except Book.DoesNotExist:
        return JsonResponse({'message': 'Book not found'}, status=404)



def view_book_details(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
        book_details = {
            'title': book.title,
            'author': book.author,
            'price': str(book.price),
            'genre': book.genre,
            'condition': book.condition,
            'Stock Quantity': book.stock_quantity,
        }
        return JsonResponse({'book_details': book_details})
    except Book.DoesNotExist:
        return JsonResponse({'message': 'Book not found'}, status=404)

def view_cart(request):
    # Retrieve the user's cart and pass it to the template
    cart = Cart.objects.get(user=request.user)
    total_price = Decimal(0)
    
    # Calculate the total price based on the items in the cart
    for item in cart.items.all():
        total_price += item.book.price * item.quantity
    
    return render(request, 'view_cart.html', {'cart': cart, 'total_price': total_price})

@require_POST
@csrf_exempt
def delete_item_from_cart(request):
    if request.user.is_authenticated:
        # Get the item ID from the AJAX request
        item_id = request.POST.get('item_id')

        # Query the cart item to delete
        try:
            cart_item = CartItem.objects.get(pk=item_id)
            cart_item.delete()
            return JsonResponse({'message': 'Item deleted successfully'})
        except CartItem.DoesNotExist:
            return JsonResponse({'message': 'Item not found'}, status=404)
    else:
        return JsonResponse({'message': 'Please log in to perform this action'}, status=401)
    

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Used')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already used')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'User created successfully')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, 'register.html')

    
def login(request):
    if request.method == 'POST' :
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Username Or Password Are Wrong')
            return redirect('login')
        
    else:    
        return render(request, 'login.html')
    
def logout_view(request):
    logout(request)
    return redirect('login') 


def purchase_cart(request):
    if request.method == 'POST':
        # Retrieve the user's cart
        cart = Cart.objects.get(user=request.user)

        # Process the purchase, update stock quantity, record transaction, etc.
        try:
            # Perform the purchase transaction and update stock quantity here
            # For simplicity, assume the purchase is successful and update stock quantity

            # Example:
            for item in cart.items.all():
                book = item.book
                book.stock_quantity -= item.quantity
                book.save()

            # Record the transaction
            transaction = Transaction.objects.create(user=request.user, amount=calculate_total_price(cart))

            # Clear the cart after purchase
            cart.items.clear()

            return JsonResponse({'message': 'Purchase completed successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Failed to complete the purchase'}, status=500)

    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)

def calculate_total_price(cart):
    total_price = sum(item.book.price * item.quantity for item in cart.items.all())
    return total_price
