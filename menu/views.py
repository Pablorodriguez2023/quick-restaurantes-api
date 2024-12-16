from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from menu.models import MenuItem
from restaurants.models import Restaurant
from .serializers import MenuItemSerializer
from restaurants.tasks import bulk_create_menu_items
from restaurants.utils import count_file_records
import os
from celery.result import AsyncResult


class MenuItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar elementos del menú.
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'available', 'restaurant']
    search_fields = ['name', 'category']
    ordering_fields = ['price', 'created_at']
    ordering = ['restaurant', 'name']
    MAX_RECORDS = 200

    def get_queryset(self):
        """
        Filtra los elementos del menú según el usuario.
        - Los superusuarios ven todos los elementos.
        - Otros usuarios solo ven elementos relacionados con sus restaurantes.
        """
        user = self.request.user
        if user.is_superuser:
            return MenuItem.objects.all()
        return MenuItem.objects.filter(restaurant__owner=user)

    def perform_create(self, serializer):
        """
        Personaliza el comportamiento al crear un elemento del menú.
        Puedes agregar lógica adicional aquí si es necesario.
        """
        serializer.save()

    @action(detail=True, methods=['get'])
    def menu_items_for_restaurant(self, request, pk=None):
        """
        Acción personalizada para obtener elementos del menú de un restaurante.
        """
        restaurant = get_object_or_404(Restaurant, id=pk)
        menu_items = restaurant.menu_items.all()  # Utiliza el related_name definido en el modelo
        return render(request, 'menu/menu_items.html', {'restaurant': restaurant, 'menu_items': menu_items})

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """
        Carga masiva de items de menú desde un archivo CSV.
        """
        if 'file' not in request.FILES:
            return Response({'error': 'No se proporcionó ningún archivo'},
                          status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        if not file.name.endswith(('.csv', '.xlsx')):
            return Response({'error': 'Formato de archivo no soportado. Use CSV o XLSX'},
                          status=status.HTTP_400_BAD_REQUEST)

        path = default_storage.save(f'temp/{file.name}', ContentFile(file.read()))
        full_path = os.path.join(default_storage.location, path)

        try:
            record_count, _ = count_file_records(full_path)
            if record_count > self.MAX_RECORDS:
                if os.path.exists(full_path):
                    os.remove(full_path)
                return Response({
                    'error': f'El archivo contiene {record_count} registros. '
                            f'El máximo permitido es {self.MAX_RECORDS} registros.'
                }, status=status.HTTP_400_BAD_REQUEST)

            task = bulk_create_menu_items.delay(full_path)
            return Response({
                'task_id': task.id,
                'status': 'Procesando archivo...',
                'check_status_url': f'/api/menu/check_task_status/{task.id}/'
            })

        except Exception as e:
            if os.path.exists(full_path):
                os.remove(full_path)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='check_task_status/(?P<task_id>[^/.]+)')
    def check_task_status(self, request, task_id=None):
        """
        Verifica el estado de una tarea de carga masiva.
        """
        task = AsyncResult(task_id)
        if task.ready():
            if task.successful():
                result = task.result
                return Response({
                    'status': 'completed',
                    'created': result['created'],
                    'errors': result['errors']
                })
            else:
                return Response({
                    'status': 'failed',
                    'error': str(task.result)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'status': 'processing'
        })
