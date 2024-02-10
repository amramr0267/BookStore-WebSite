from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search-books/', views.search_books, name='search_books'),
    path('add-to-cart/<book_id>/', views.add_to_cart, name='add-to-cart'),
    path('view-cart/', views.view_cart, name='view-cart'),
    path('delete-item-from-cart/', views.delete_item_from_cart, name='delete_item_from_cart'),
    path('update-cart-item/', views.update_cart_item, name='update_cart_item'),
    path('purchase-cart/', views.purchase_cart, name='purchase_cart'),
]
