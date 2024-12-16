from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword123')
