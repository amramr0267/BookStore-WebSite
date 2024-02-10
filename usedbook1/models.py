from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class Book(models.Model):
    book_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    genre = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)
    stock_quantity = models.IntegerField(default=0)  # Update this line
    

    def __str__(self):
        return self.title

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('CartItem')

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # Define a ForeignKey relationship with Book
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"
    
User = get_user_model()

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction of {self.amount} by {self.user.username}"