from django.test import TestCase
from django.utils.timezone import now, timedelta
from django.urls import reverse
from rest_framework import status
from users.models import CustomUser
from restaurants.models import Restaurant
from .models import Order, OrderItem
from menu.models import MenuItem

class OrderModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone='1234567890',
            default_address='Test Address',
            typology='CUSTOMER'
        )
        self.restaurant = Restaurant.objects.create(name='Test Restaurant', owner=self.user)
        self.menu_item = MenuItem.objects.create(
            name='Pizza',
            description='Deliciosa pizza',
            price=10.00,
            restaurant=self.restaurant,
            available=True,
            preparation_time=15,  
            category='MAIN_COURSE'
        )

    def test_create_order(self):
        order = Order.objects.create(
            customer=self.user,
            restaurant=self.restaurant,
            total_amount=20.0,
            estimated_delivery_time=now() + timedelta(hours=1)
        )
        OrderItem.objects.create(order=order, menu_item=self.menu_item, quantity=2, unit_price=10.0)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_amount, 20.0)
