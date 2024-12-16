import pandas as pd
from typing import Tuple

def count_file_records(file_path: str) -> Tuple[int, str]:
    """
    Cuenta el número de registros en un archivo CSV o XLSX.
    """
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        return len(df), 'csv'
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
        return len(df), 'xlsx'
    else:
        raise ValueError('Formato de archivo no soportado')
