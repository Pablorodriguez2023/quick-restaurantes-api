from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'restaurant', 'status', 'total_amount', 'created_at')
    search_fields = ('id', 'customer__email', 'restaurant__name')
    list_filter = ('status', 'restaurant')
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'unit_price', 'subtotal')
    search_fields = ('order__id', 'menu_item__name')
    list_filter = ('menu_item__category',)
