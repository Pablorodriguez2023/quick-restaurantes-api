import pandas as pd
from typing import Tuple
import bcrypt
from django.conf import settings
import hashlib
import base64

def count_file_records(file_path: str) -> Tuple[int, str]:
    """
    Cuenta el número de registros en un archivo CSV o XLSX.
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        Tuple con el número de registros y el tipo de archivo
    """
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        return len(df), 'csv'
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
        return len(df), 'xlsx'
    else:
        raise ValueError("Formato de archivo no soportado")

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def hash_sensitive_data(data: str) -> str:
    """
    Hashea datos sensibles usando SHA-256 con un salt único.
    """
    salt = getattr(settings, 'HASH_SALT', 'default-salt-value')
    salted = f"{data}{salt}".encode('utf-8')
    return base64.b64encode(hashlib.sha256(salted).digest()).decode('utf-8')

def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Enmascara datos sensibles mostrando solo los últimos caracteres.
    """
    if not data or len(data) <= visible_chars:
        return data
    return '*' * (len(data) - visible_chars) + data[-visible_chars:]
