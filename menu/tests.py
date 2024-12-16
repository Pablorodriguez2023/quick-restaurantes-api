from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from menu.models import MenuItem
from restaurants.models import Restaurant
from django.contrib.auth import get_user_model

class MenuItemTests(TestCase):

    def setUp(self):
        # Crear un usuario primero
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # Asegurarse de que el usuario esté autenticado
        # Crear un restaurante usando el usuario
        self.restaurant = Restaurant.objects.create(name="Restaurante Test", owner=self.user)

    def test_create_menu_item(self):
        data = {
            "name": "Pizza",
            "description": "Deliciosa pizza",
            "price": "10.00",
            "restaurant": self.restaurant.id,
            "available": True,
            "preparation_time": 15,  # Agregar el tiempo de preparación
            "category": "MAIN_COURSE",
        }
        response = self.client.post('/api/menu/menu-items/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuItem.objects.count(), 1)
        self.assertEqual(MenuItem.objects.get().name, 'Pizza')
