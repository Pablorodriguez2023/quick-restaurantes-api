import os
from celery import Celery
from django.conf import settings

# Establecer el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_pedidos.settings')

app = Celery('gestion_pedidos')

# Usar configuración de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar tareas de todas las aplicaciones registradas
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Manejo básico de excepciones de Celery
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
