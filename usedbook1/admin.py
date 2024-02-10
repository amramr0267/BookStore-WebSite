from django.contrib import admin
from .models import Book, Cart, CartItem, Transaction
# Register your models here.



# Register multiple models using an iterable (tuple)
admin.site.register((Book, Cart, CartItem, Transaction))
