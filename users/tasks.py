from celery import shared_task
from typing import Dict, List
import pandas as pd
from django.db import transaction
from .models import CustomUser

@shared_task
def bulk_create_users(file_path: str) -> Dict[str, int]:
    """
    Crea usuarios de forma masiva desde un archivo CSV/XLSX.
    
    Args:
        file_path: Ruta al archivo de usuarios
        
    Returns:
        Dict con el conteo de usuarios creados y errores
    """
    try:
        # Leer archivo según su extensión
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Validar número máximo de registros
        if len(df) > 20:
            raise ValueError("El archivo contiene más de 20 registros")

        # Validar columnas requeridas
        required_columns = ['first_name', 'last_name', 'email', 'phone', 'default_address', 'typology']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Faltan las columnas: {', '.join(missing_columns)}")

        users_created = 0
        errors = []

        with transaction.atomic():
            for _, row in df.iterrows():
                try:
                    CustomUser.objects.create(
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        email=row['email'],
                        phone=row['phone'],
                        default_address=row['default_address'],
                        typology=row['typology'],
                        username=row['email']  # Usar email como username
                    )
                    users_created += 1
                except Exception as e:
                    errors.append(f"Error en fila {_ + 2}: {str(e)}")

        return {
            'users_created': users_created,
            'errors': len(errors),
            'error_details': errors
        }

    except Exception as e:
        return {
            'users_created': 0,
            'errors': 1,
            'error_details': [str(e)]
        }
    finally:
        # Limpiar el archivo temporal
        import os
        if os.path.exists(file_path):
            os.remove(file_path)
