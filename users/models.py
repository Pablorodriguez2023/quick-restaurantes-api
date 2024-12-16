from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from restaurants.models import Restaurant
from .utils import hash_sensitive_data, mask_sensitive_data

class CustomUser(AbstractUser):
    """
    Modelo personalizado de usuario con datos sensibles hasheados
    """
    TYPOLOGY_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CUSTOMER', 'Customer'),
        ('RESTAURANT', 'Restaurant'),
    ]
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    typology = models.CharField(max_length=20, choices=TYPOLOGY_CHOICES, default='CUSTOMER')
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=255, blank=True)  # Aumentado para almacenar el hash
    default_address = models.CharField(max_length=255, blank=True)
    hashed_phone = models.CharField(max_length=255, blank=True)  # Campo para almacenar el teléfono hasheado
    hashed_address = models.CharField(max_length=255, blank=True)  # Campo para almacenar la dirección hasheada

    class Meta:
        db_table = 'customers'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def save(self, *args, **kwargs):
        # Hashear datos sensibles antes de guardar
        if self.phone:
            self.hashed_phone = hash_sensitive_data(self.phone)
            self.phone = mask_sensitive_data(self.phone)
        
        if self.default_address:
            self.hashed_address = hash_sensitive_data(self.default_address)
            self.default_address = mask_sensitive_data(self.default_address, visible_chars=8)
        
        super().save(*args, **kwargs)

    def get_masked_phone(self):
        """Retorna el número de teléfono enmascarado"""
        return self.phone

    def get_masked_address(self):
        """Retorna la dirección enmascarada"""
        return self.default_address

    def verify_phone(self, phone: str) -> bool:
        """Verifica si un número de teléfono coincide con el hash almacenado"""
        return hash_sensitive_data(phone) == self.hashed_phone

    def verify_address(self, address: str) -> bool:
        """Verifica si una dirección coincide con el hash almacenado"""
        return hash_sensitive_data(address) == self.hashed_address
