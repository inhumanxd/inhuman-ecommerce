from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('add-to-cart/<slug>/', views.add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name="remove-from-cart"),
    path('remove-single-item-from-cart/<slug>/', views.remove_single_item_from_cart, name="remove-single-item-from-cart"),
    path('add-single-item-in-cart/<slug>/', views.add_single_item_in_cart, name="add-single-item-in-cart"),
    path('cart', views.CartView.as_view(), name="cart"),
    path('search', views.Search, name="search"),
    path('order_confirmation', views.OrderConfirmation, name="order-confirmation"),
]
