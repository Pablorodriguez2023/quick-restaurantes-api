from django.db import models
from django.utils import timezone


class Restaurant(models.Model):
    """
    Modelo para los restaurantes.
    """
    CATEGORY_CHOICES = [
        ('ITALIAN', 'Italian'),
        ('MEXICAN', 'Mexican'),
        ('CHINESE', 'Chinese'),
        ('JAPANESE', 'Japanese'),
        ('AMERICAN', 'American'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('BUSY', 'Busy'),
    ]

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    owner = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='restaurants', null=True)


    class Meta:
        db_table = 'restaurants'
        verbose_name = 'Restaurante'
        verbose_name_plural = 'Restaurantes'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
