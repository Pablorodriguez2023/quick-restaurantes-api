from rest_framework import viewsets, permissions, filters, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    Vista para gestionar pedidos.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'restaurant', 'status']
    search_fields = ['delivery_address', 'special_instructions']
    ordering_fields = ['created_at', 'updated_at', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filtra los pedidos basados en el usuario autenticado.
        """
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(customer=user)

    def perform_create(self, serializer):
        """
        Asocia automáticamente el pedido al usuario autenticado.
        """
        serializer.save(customer=self.request.user)

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """
        Obtiene los elementos de un pedido específico.
        """
        order = self.get_object()
        items = order.order_items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    Vista para gestionar elementos de un pedido.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['order', 'menu_item']
    search_fields = ['menu_item__name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filtra los elementos del pedido según el usuario autenticado.
        """
        user = self.request.user
        if user.is_superuser:
            return OrderItem.objects.all()
        return OrderItem.objects.filter(order__customer=user)

    def perform_create(self, serializer):
        """
        Valida que el usuario esté asociado al pedido del OrderItem.
        """
        order = serializer.validated_data['order']
        if order.customer != self.request.user:
            raise serializers.ValidationError("No puedes añadir elementos a un pedido que no es tuyo.")
        serializer.save()
