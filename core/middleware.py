import time
from django.db import connection
from django.conf import settings

class QueryCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        n_queries_start = len(connection.queries)
        
        response = self.get_response(request)
        
        if settings.DEBUG:  # Solo activar en desarrollo o pruebas
            total_time = time.time() - start_time
            n_queries_end = len(connection.queries)
            total_queries = n_queries_end - n_queries_start
            
            # Solo registrar si hay más de 100 queries
            if total_queries > 100:
                print(f"[WARNING] High query count detected: {total_queries} queries")

            response['X-Total-Time'] = f"{round(total_time * 1000, 2)}ms"
            response['X-Total-Queries'] = str(total_queries)
            
        return response
