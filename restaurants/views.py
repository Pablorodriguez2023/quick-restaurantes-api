from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Restaurant
from .serializers import RestaurantSerializer
from .filters import RestaurantFilter
from .tasks import (
    generate_restaurant_report, 
    generate_sales_report,
    bulk_create_restaurants,
    bulk_create_menu_items
)
from .utils import count_file_records
import os
from django.conf import settings
from django.http import FileResponse
from celery.result import AsyncResult

class RestaurantViewSet(viewsets.ModelViewSet):
    """
    Vista para gestionar restaurantes.
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RestaurantFilter
    search_fields = ['name', 'category', 'status']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
    MAX_RECORDS = 100

    def get_queryset(self):
        """
        Filtra los restaurantes activos para usuarios normales.
        """
        user = self.request.user
        if user.is_superuser:
            return Restaurant.objects.all()
        return Restaurant.objects.filter(active=True)

    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """
        Genera un reporte general de restaurantes.
        """
        task = generate_restaurant_report.delay()
        return Response({
            'task_id': task.id,
            'status': 'El reporte se está generando',
            'check_status_url': f'/api/restaurants/check_task_status/{task.id}/'
        })

    @action(detail=False, methods=['post'])
    def generate_sales_report(self, request):
        """
        Genera un reporte de ventas por restaurante.
        """
        month = request.data.get('month')
        year = request.data.get('year')
        
        if year and not (1900 <= int(year) <= 2100):
            return Response(
                {'error': 'Año inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if month and not (1 <= int(month) <= 12):
            return Response(
                {'error': 'Mes inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task = generate_sales_report.delay(month, year)
        return Response({
            'task_id': task.id,
            'status': 'El reporte de ventas se está generando',
            'check_status_url': f'/api/restaurants/check_task_status/{task.id}/'
        })

    @action(detail=False, methods=['get'])
    def download_report(self, request):
        """
        Descarga el último reporte generado.
        """
        report_dir = os.path.join(settings.BASE_DIR, 'reports')
        if not os.path.exists(report_dir):
            return Response(
                {'error': 'No hay reportes disponibles'},
                status=status.HTTP_404_NOT_FOUND
            )

        files = os.listdir(report_dir)
        if not files:
            return Response(
                {'error': 'No hay reportes disponibles'},
                status=status.HTTP_404_NOT_FOUND
            )

        latest_file = max([os.path.join(report_dir, f) for f in files], key=os.path.getctime)
        return FileResponse(
            open(latest_file, 'rb'),
            as_attachment=True,
            filename=os.path.basename(latest_file)
        )

    @action(detail=False, methods=['get'], url_path='check_task_status/(?P<task_id>[^/.]+)')
    def check_task_status(self, request, task_id):
        """
        Verifica el estado de una tarea de generación de reporte.
        """
        task_result = AsyncResult(task_id)
        
        if task_result.successful():
            return Response({
                'status': 'completed',
                'download_url': '/api/restaurants/download_report/'
            })
        elif task_result.failed():
            return Response({
                'status': 'failed',
                'error': str(task_result.result)
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'status': 'processing'
            })

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """
        Carga masiva de restaurantes desde un archivo CSV.
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

            task = bulk_create_restaurants.delay(full_path)
            return Response({
                'task_id': task.id,
                'status': 'Procesando archivo...',
                'check_status_url': f'/api/restaurants/check_task_status/{task.id}/'
            })

        except Exception as e:
            if os.path.exists(full_path):
                os.remove(full_path)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
