from django.db import models
from django.utils import timezone
from django.conf import settings
from restaurants.models import Restaurant
from menu.models import MenuItem

# Correctamente referenciando las apps y modelos en formato de cadena
class Order(models.Model):
    """
    Modelo para los pedidos
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('IN_PREPARATION', 'In Preparation'),
        ('READY', 'Ready'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    # Referencia al modelo UserModel en la app users
    customer = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, related_name='orders')  # Corregido aquí
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_address = models.CharField(max_length=255)
    special_instructions = models.TextField()
    estimated_delivery_time = models.DateTimeField()
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido #{self.id}"

    def update_total_amount(self):
        """
        Actualiza el monto total del pedido basado en los elementos.
        """
        self.total_amount = sum(item.subtotal for item in self.items.all())
        self.save()


class OrderItem(models.Model):
    """
    Modelo para los elementos de un pedido.
    """
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    # Referencia al modelo Order en la app orders
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey('menu.MenuItem', on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        """
        Calcula el subtotal antes de guardar y actualiza el precio unitario.
        """
        if not self.unit_price:
            self.unit_price = self.menu_item.price
        super().save(*args, **kwargs)
        self.order.update_total_amount()

    @property
    def subtotal(self):
        """Calcula el subtotal como cantidad * precio unitario"""
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.order.id} - {self.menu_item.name} x{self.quantity}"
