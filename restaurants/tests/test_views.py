from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant
from restaurants.serializers import RestaurantSerializer

User = get_user_model()

class RestaurantViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='Test Address',
            phone='1234567890',
            category='ITALIAN',
            rating=4.5,
            status='OPEN',
            active=True
        )
        
        self.valid_payload = {
            'name': 'New Restaurant',
            'address': 'New Address',
            'phone': '0987654321',
            'category': 'MEXICAN',
            'rating': 4.0,
            'status': 'OPEN',
            'active': True
        }
        
    def test_get_all_restaurants(self):
        """Test retrieving all restaurants"""
        response = self.client.get(reverse('restaurant-list'))
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)
        
    def test_create_valid_restaurant(self):
        """Test creating a new restaurant with valid payload"""
        response = self.client.post(
            reverse('restaurant-list'),
            data=self.valid_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_retrieve_valid_restaurant(self):
        """Test retrieving a valid restaurant"""
        response = self.client.get(
            reverse('restaurant-detail', kwargs={'pk': self.restaurant.pk})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_update_restaurant(self):
        """Test updating an existing restaurant"""
        response = self.client.put(
            reverse('restaurant-detail', kwargs={'pk': self.restaurant.pk}),
            data=self.valid_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_delete_restaurant(self):
        """Test deleting a restaurant"""
        response = self.client.delete(
            reverse('restaurant-detail', kwargs={'pk': self.restaurant.pk})
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
