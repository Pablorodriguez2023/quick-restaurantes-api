from rest_framework import serializers
from django.utils import timezone
from .models import Order, OrderItem
from menu.serializers import MenuItemSerializer
from users.serializers import CustomSerializer
from restaurants.serializers import RestaurantSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializador para los elementos de un pedido.
    """
    menu_item_details = MenuItemSerializer(source='menu_item', read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            'id', 'order', 'menu_item', 'menu_item_details', 'quantity',
            'unit_price', 'subtotal', 'created_at', 'updated_at'
        )
        read_only_fields = ('subtotal', 'unit_price', 'created_at', 'updated_at')

    def validate_quantity(self, value):
        """
        Valida que la cantidad sea mayor a 0.
        """
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a cero.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializador para los pedidos.
    """
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    customer_details = CustomSerializer(source='customer', read_only=True)
    restaurant_details = RestaurantSerializer(source='restaurant', read_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'customer', 'customer_details', 'restaurant', 'restaurant_details',
            'status', 'total_amount', 'delivery_address', 'special_instructions',
            'estimated_delivery_time', 'notes', 'created_at', 'updated_at', 'order_items'
        )
        read_only_fields = ('total_amount', 'created_at', 'updated_at', 'order_items')

    def validate_estimated_delivery_time(self, value):
        """
        Valida que la fecha estimada de entrega sea futura.
        """
        if value <= timezone.now():
            raise serializers.ValidationError("La fecha de entrega estimada debe ser futura.")
        return value
