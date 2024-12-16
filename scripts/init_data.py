import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_pedidos.settings')
django.setup()

from django.contrib.auth import get_user_model
from restaurants.models import Restaurant
from menu.models import MenuItem
from orders.models import Order, OrderItem

User = get_user_model()

def create_users():
    """Crear usuarios de prueba"""
    print("Creando usuarios...")
    
    # Admin
    User.objects.create_superuser(
        'admin@example.com',
        'admin123',
        first_name='Admin',
        last_name='User',
        phone='1234567890',
        default_address='Admin Address',
        typology='ADMIN'
    )
    
    # Clientes
    for i in range(10):
        User.objects.create_user(
            f'customer{i}@example.com',
            f'pass{i}123',
            first_name=f'Customer{i}',
            last_name='User',
            phone=f'123456789{i}',
            default_address=f'Address {i}',
            typology='CUSTOMER'
        )

def create_restaurants():
    """Crear restaurantes de prueba"""
    print("Creando restaurantes...")
    
    categories = ['ITALIAN', 'MEXICAN', 'CHINESE', 'JAPANESE', 'AMERICAN']
    
    for i in range(10):
        Restaurant.objects.create(
            name=f'Restaurant {i}',
            address=f'Restaurant Address {i}',
            phone=f'987654321{i}',
            category=random.choice(categories),
            rating=round(random.uniform(3.5, 5.0), 1),
            status='OPEN',
            active=True
        )

def create_menu_items():
    """Crear elementos de menú de prueba"""
    print("Creando elementos de menú...")
    
    restaurants = Restaurant.objects.all()
    
    for restaurant in restaurants:
        for i in range(5):
            MenuItem.objects.create(
                restaurant=restaurant,
                name=f'Item {i} - {restaurant.name}',
                description=f'Description for item {i}',
                price=Decimal(random.uniform(10.0, 50.0)).quantize(Decimal('0.01')),
                category='MAIN_COURSE',
                available=True
            )

def create_orders():
    """Crear órdenes de prueba"""
    print("Creando órdenes...")
    
    customers = User.objects.filter(typology='CUSTOMER')
    menu_items = MenuItem.objects.all()
    
    for customer in customers:
        for _ in range(random.randint(1, 3)):
            # Crear orden
            order = Order.objects.create(
                customer=customer,
                restaurant=random.choice(menu_items).restaurant,
                delivery_address=customer.default_address,
                total_amount=Decimal('0.00'),
                status='PENDING',
                estimated_delivery_time=datetime.now() + timedelta(minutes=30)
            )
            
            # Agregar items aleatorios
            total = Decimal('0.00')
            for _ in range(random.randint(1, 4)):
                item = random.choice(menu_items)
                quantity = random.randint(1, 3)
                
                OrderItem.objects.create(
                    order=order,
                    menu_item=item,
                    quantity=quantity,
                    unit_price=item.price
                )
                
                total += item.price * quantity
            
            # Actualizar total
            order.total_amount = total
            order.save()

def main():
    """Función principal"""
    print("Iniciando carga de datos...")
    
    create_users()
    create_restaurants()
    create_menu_items()
    create_orders()
    
    print("Carga de datos completada!")

if __name__ == '__main__':
    main()
