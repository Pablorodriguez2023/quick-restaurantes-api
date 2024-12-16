from django.db import models
from django.utils import timezone
from restaurants.models import Restaurant

# Create your models here.

class MenuItem(models.Model):
    """
    Modelo para los elementos del menú
    """
    CATEGORY_CHOICES = [
        ('APPETIZER', 'Appetizer'),
        ('MAIN_COURSE', 'Main Course'),
        ('DESSERT', 'Dessert'),
        ('BEVERAGE', 'Beverage'),
    ]
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',  # Referencia al modelo Restaurant de la app restaurants
        on_delete=models.CASCADE,  # Si el restaurante se elimina, también se eliminan los elementos del menú asociados
        related_name='menu_items'  # Nombre del conjunto inverso para acceder a los elementos de menú desde Restaurant
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    preparation_time = models.IntegerField()
    available = models.BooleanField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image_url = models.CharField(max_length=255)

    class Meta:
        db_table = 'menu_items'
        verbose_name = 'Elemento del menú'
        verbose_name_plural = 'Elementos del menú'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
