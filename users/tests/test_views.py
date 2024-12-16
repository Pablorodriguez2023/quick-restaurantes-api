from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from users.serializers import CustomSerializer

CustomUser = get_user_model()

class CustomViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.custom_user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone='1234567890',
            default_address='Test Address',
            typology='CUSTOMER'
        )
        self.client.force_authenticate(user=self.custom_user)
        
        self.valid_payload = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '0987654321',
            'default_address': 'New Address',
            'typology': 'CUSTOMER'
        }
        
    def test_get_all_users(self):
        """Test retrieving all users"""
        response = self.client.get(reverse('custom-list'))
        users = CustomUser.objects.all()
        serializer = CustomSerializer(users, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)
        
    def test_create_valid_user(self):
        """Test creating a new user with valid payload"""
        response = self.client.post(
            reverse('custom-list'),
            data=self.valid_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_change_password(self):
        """Test changing user password"""
        url = reverse('custom-change-password', kwargs={'pk': self.custom_user.pk})
        payload = {
            'current_password': 'testpass123',
            'new_password': 'newpass123'
        }
        response = self.client.post(url, data=payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_bulk_upload_users(self):
        """Test bulk upload of users"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        import pandas as pd
        import io
        
        # Crear archivo CSV de prueba
        data = {
            'first_name': ['Test1', 'Test2'],
            'last_name': ['User1', 'User2'],
            'email': ['test1@example.com', 'test2@example.com'],
            'phone': ['1111111111', '2222222222'],
            'default_address': ['Address1', 'Address2'],
            'typology': ['CUSTOMER', 'CUSTOMER']
        }
        df = pd.DataFrame(data)
        csv_file = io.StringIO()
        df.to_csv(csv_file, index=False)
        csv_file.seek(0)
        
        file = SimpleUploadedFile(
            "users.csv",
            csv_file.getvalue().encode(),
            content_type="text/csv"
        )
        
        response = self.client.post(
            reverse('custom-bulk-upload'),
            {'file': file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('task_id', response.data)
