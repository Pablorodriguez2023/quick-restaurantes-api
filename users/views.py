from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import FileResponse
import os
from typing import Any
from .models import CustomUser
from .serializers import CustomSerializer, ChangePasswordSerializer
from .tasks import bulk_create_users
from .utils import count_file_records
from core.pagination import CustomPageNumberPagination
from celery.result import AsyncResult

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    MAX_RECORDS = 20

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def change_password(self, request: Any, pk: int = None) -> Response:
        """
        Cambia la contraseña de un usuario autenticado.

        Args:
            request (Any): Objeto de solicitud.
            pk (int, opcional): ID del usuario.

        Returns:
            Response: Respuesta con éxito o error.
        """
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Verificar contraseña actual
            if not user.check_password(serializer.data.get('current_password')):
                return Response({'error': 'Contraseña actual incorrecta'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Cambiar contraseña
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'message': 'Contraseña actualizada correctamente'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request, *args, **kwargs):
        serializer = CustomSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request: Any) -> Response:
        """
        Procesa una carga masiva de usuarios desde un archivo.

        Args:
            request (Any): Solicitud con archivo cargado.

        Returns:
            Response: Respuesta indicando el estado de la carga.
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

            task = bulk_create_users.delay(full_path)
            return Response({
                'task_id': task.id,
                'message': 'Procesando archivo. Use el task_id para verificar el estado.'
            })

        except Exception as e:
            if os.path.exists(full_path):
                os.remove(full_path)
            return Response({'error': f'Error al procesar el archivo: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def download_template(self, request: Any) -> Response:
        """
        Descarga una plantilla para la carga masiva de usuarios.

        Args:
            request (Any): Solicitud GET.

        Returns:
            Response: Archivo de plantilla o error.
        """
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'users_template.xlsx')
        if not os.path.exists(template_path):
            return Response({'error': 'Plantilla no encontrada'}, 
                            status=status.HTTP_404_NOT_FOUND)

        try:
            response = FileResponse(open(template_path, 'rb'))
            response['Content-Disposition'] = 'attachment; filename="users_template.xlsx"'
            return response
        except FileNotFoundError:
            return Response({'error': 'Plantilla no encontrada'}, 
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
