from django.contrib import admin
from .models import Order, Item, OrderItem

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)