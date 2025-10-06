from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # Para proteger las vistas
from .models import Muestra, Espectrograma, Anotacion, Clasificacion, User
from .serializers import (
    MuestraSerializer, EspectrogramaSerializer, AnotacionSerializer, 
    ClasificacionSerializer, UserSerializer
)
# from .services import procesar_evento_completo
from .tasks import procesar_evento_completo_task # Importa la tarea de Celery
import pickle
import numpy as np

# Create your views here.
# core/views.py

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated] # Solo usuarios autenticados pueden ver usuarios

class MuestraViewSet(viewsets.ModelViewSet):
    queryset = Muestra.objects.all().select_related('usuario_creacion')
    serializer_class = MuestraSerializer
    # permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='process')
    def process_event(self, request, pk=None):
        """
        Endpoint para disparar el procesamiento asíncrono de un evento por su ID de muestra (PK).
        """
        muestra = self.get_object()
        # event_id = muestra.event_id

        if muestra.estado_procesamiento == 'procesado':
            return Response({'detail': f'La muestra {muestra.id} ya ha sido procesada.'}, status=status.HTTP_200_OK)

        try:
            # Dispara la tarea de Celery de forma asíncrona
            task_result = procesar_evento_completo_task.delay(muestra.id) # .delay() envía la tarea al broker

            # Responde inmediatamente al frontend
            return Response({
                'detail': f'Tarea de procesamiento para event_id {muestra.id} enviada a la cola.',
                'task_id': task_result.id, # El ID de la tarea para consultar su estado
                'status_url': self.reverse_action('task-status', args=[task_result.id]) # Podemos añadir un endpoint para esto
            }, status=status.HTTP_202_ACCEPTED) # 202 Accepted indica que la petición fue aceptada para procesamiento
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Opcional: Agrega un endpoint para consultar el estado de una tarea
    @action(detail=False, methods=['get'], url_path='task-status/(?P<task_id>[^/.]+)')
    def task_status(self, request, task_id=None):
        from celery.result import AsyncResult
        task = AsyncResult(task_id)
        data = {
            'task_id': task.id,
            'status': task.status,
            'result': task.result
        }
        return Response(data)


class EspectrogramaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Espectrograma.objects.all().select_related('muestra')
    serializer_class = EspectrogramaSerializer
    # permission_classes = [IsAuthenticated]

class AnotacionViewSet(viewsets.ModelViewSet):
    queryset = Anotacion.objects.all().select_related('muestra', 'usuario_anotador')
    serializer_class = AnotacionSerializer
    # permission_classes = [IsAuthenticated]

class ClasificacionViewSet(viewsets.ModelViewSet):
    queryset = Clasificacion.objects.all().select_related('muestra', 'usuario_validador')
    serializer_class = ClasificacionSerializer
    # permission_classes = [IsAuthenticated]