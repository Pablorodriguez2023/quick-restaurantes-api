from celery import shared_task
from django.db import connection, transaction
from django.conf import settings
import csv
import os
import pandas as pd
from datetime import datetime
from typing import Optional
from .models import Restaurant
from menu.models import MenuItem

@shared_task(name='restaurants.tasks.generate_restaurant_report')
def generate_restaurant_report():
    query = """
        SELECT 
            r.id,
            r.name,
            r.category,
            r.rating,
            r.status,
            COUNT(DISTINCT o.id) as total_orders,
            COALESCE(SUM(o.total_amount), 0) as total_revenue
        FROM restaurants r
        LEFT JOIN orders o ON o.restaurant_id = r.id
        WHERE r.active = true
        GROUP BY r.id, r.name, r.category, r.rating, r.status
        ORDER BY total_revenue DESC;
    """

    # Crear directorio para reportes si no existe
    report_dir = os.path.join(settings.BASE_DIR, 'reports')
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    # Nombre del archivo con timestamp
    filename = f'restaurant_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    filepath = os.path.join(report_dir, filename)

    # Ejecutar query y escribir resultados a CSV
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow([
                'ID',
                'Nombre',
                'Categoría',
                'Calificación',
                'Estado',
                'Total Pedidos',
                'Ingresos Totales'
            ])
            writer.writerows(rows)

    return filepath

@shared_task(name='restaurants.tasks.generate_sales_report')
def generate_sales_report(month: Optional[int] = None, year: Optional[int] = None) -> str:
    """
    Genera un reporte de ventas por restaurante.
    
    Args:
        month: Mes para filtrar (1-12)
        year: Año para filtrar
        
    Returns:
        str: Ruta del archivo generado
    """
    query = """
        SELECT 
            r.id,
            r.name,
            COUNT(o.id) as total_orders,
            COALESCE(SUM(o.total_amount), 0) as total_sales
        FROM restaurants r
        LEFT JOIN orders o ON o.restaurant_id = r.id
        WHERE 1=1
    """
    params = []
    
    if month and year:
        query += " AND EXTRACT(MONTH FROM o.created_at) = %s AND EXTRACT(YEAR FROM o.created_at) = %s"
        params.extend([month, year])
    
    query += " GROUP BY r.id, r.name ORDER BY total_sales DESC"

    # Crear directorio para reportes si no existe
    report_dir = os.path.join(settings.BASE_DIR, 'reports')
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    # Nombre del archivo con timestamp
    filename = f'sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    filepath = os.path.join(report_dir, filename)

    # Ejecutar query y escribir resultados a CSV
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['ID', 'Nombre', 'Total Pedidos', 'Total Ventas'])
            writer.writerows(rows)

    return filepath

@shared_task(name='restaurants.tasks.delete_report')
def delete_report(filepath: str) -> None:
    """
    Elimina un archivo de reporte después de su descarga.
    
    Args:
        filepath: Ruta al archivo a eliminar
    """
    if os.path.exists(filepath):
        os.remove(filepath)

@shared_task(name='restaurants.tasks.bulk_create_restaurants')
def bulk_create_restaurants(file_path: str) -> dict:
    """
    Crea restaurantes masivamente desde un archivo CSV.
    
    El archivo CSV debe tener las siguientes columnas:
    name,address,phone,category,opening_time,closing_time,rating,status
    """
    try:
        df = pd.read_csv(file_path)
        created_count = 0
        errors = []

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    Restaurant.objects.create(
                        name=row['name'],
                        address=row['address'],
                        phone=row['phone'],
                        category=row['category'],
                        opening_time=row['opening_time'],
                        closing_time=row['closing_time'],
                        rating=row['rating'],
                        status=row['status']
                    )
                    created_count += 1
                except Exception as e:
                    errors.append(f"Error en fila {index + 1}: {str(e)}")

        # Limpiar archivo temporal
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            'created': created_count,
            'errors': errors
        }

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise Exception(f"Error procesando archivo: {str(e)}")

@shared_task(name='restaurants.tasks.bulk_create_menu_items')
def bulk_create_menu_items(file_path: str) -> dict:
    """
    Crea items de menú masivamente desde un archivo CSV.
    
    El archivo CSV debe tener las siguientes columnas:
    name,description,price,category,restaurant_id,is_available
    """
    try:
        df = pd.read_csv(file_path)
        created_count = 0
        errors = []

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    MenuItem.objects.create(
                        name=row['name'],
                        description=row['description'],
                        price=row['price'],
                        category=row['category'],
                        restaurant_id=row['restaurant_id'],
                        is_available=row['is_available']
                    )
                    created_count += 1
                except Exception as e:
                    errors.append(f"Error en fila {index + 1}: {str(e)}")

        # Limpiar archivo temporal
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            'created': created_count,
            'errors': errors
        }

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise Exception(f"Error procesando archivo: {str(e)}")
