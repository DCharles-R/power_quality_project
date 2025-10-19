from django.shortcuts import render
from django.http import HttpResponse # Para devolver la imagen
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # Para proteger las vistas
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Muestra, Espectrograma, Anotacion, Clasificacion, User
from .serializers import (
    MuestraSerializer, EspectrogramaSerializer, AnotacionSerializer, 
    ClasificacionSerializer, UserSerializer
)
from .influx_client import influx_service
from .tasks import procesar_evento_completo_task # Importa la tarea de Celery
from .filters import MuestraFilter
import io # Para manejar la imagen en memoria
import pickle
import numpy as np
import matplotlib.pyplot as plt
import logging

# Create your views here.
# core/views.py

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated] # Solo usuarios autenticados pueden ver usuarios

class MuestraViewSet(viewsets.ModelViewSet):
    # queryset = Muestra.objects.all().select_related('usuario_creacion')
    queryset = Muestra.objects.all().order_by('-timestamp_inicio') # Ordenar por fecha más reciente
    serializer_class = MuestraSerializer
    # permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filterset_fields = ['estado_procesamiento'] # Filtro exacto por estado
    filterset_class = MuestraFilter
    search_fields = ['event_id'] # Búsqueda parcial por event_id

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

    @action(detail=True, methods=['get'], url_path='signal-raw-data')
    def get_signal_raw_data(self, request, pk=None):
        """
        Endpoint para obtener los 5120 puntos de la señal cruda desde InfluxDB.
        """
        try:
            muestra = self.get_object()
            event_id = muestra.event_id

            # Usamos nuestro influx_service para obtener los datos
            # La función devuelve una lista de tuplas [(timestamp, value), ...]
            puntos_signal = influx_service.get_signal_data(event_id, 'voltage_waveform')

            if not puntos_signal:
                return Response({'detail': 'No se encontraron datos de la señal en InfluxDB.'}, status=status.HTTP_404_NOT_FOUND)

            # Preparamos los datos para el gráfico de Plotly (ejes x e y separados)
            timestamps, values = zip(*puntos_signal)

            # Convertir timestamps a un formato más manejable para el frontend (ej. milisegundos desde epoch)
            timestamps_ms = [ts.timestamp() * 1000 for ts in timestamps]

            return Response({
                'muestra_id': muestra.id,
                'event_id': event_id,
                'x_data': timestamps_ms, # Eje X (tiempo)
                'y_data': values,       # Eje Y (voltaje)
            })

        except Muestra.DoesNotExist:
            return Response({'detail': 'Muestra no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error al obtener datos de señal cruda para muestra {pk}: {e}", exc_info=True)
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], url_path='espectrograma-image') # Cambiamos el nombre para más claridad
    def get_espectrograma_image(self, request, pk=None):
        """
        Genera y devuelve una imagen PNG del espectrograma.
        """
        logger.info(f"Generando imagen de espectrograma para Muestra pk={pk}")
        try:
            muestra = self.get_object()
            espectrograma_obj = Espectrograma.objects.get(muestra=muestra)

            # Deserializar la matriz de NumPy
            matriz_espectrograma_complex = pickle.loads(espectrograma_obj.data_espectrograma)

            # Para visualizar, necesitamos la magnitud del número complejo
            matriz_magnitud = np.abs(matriz_espectrograma_complex)

            # Usar matplotlib para crear la imagen del heatmap
            fig, ax = plt.subplots(figsize=(10, 6)) # Ajusta el tamaño según necesites
            im = ax.imshow(matriz_magnitud, aspect='auto', origin='lower', cmap='jet')
            fig.colorbar(im, ax=ax)
            ax.set_title('Análisis Tiempo-Frecuencia')
            ax.set_xlabel('Muestras de Tiempo')
            ax.set_ylabel('Componentes de Frecuencia')

            # Guardar la figura en un buffer de memoria como PNG
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig) # Cerrar la figura para liberar memoria
            buf.seek(0)

            # Devolver la imagen en la respuesta HTTP
            return HttpResponse(buf.getvalue(), content_type='image/png')

        except (Muestra.DoesNotExist, Espectrograma.DoesNotExist):
            logger.warning(f"No se encontró Muestra o Espectrograma para pk={pk}")
            return HttpResponse(status=404)
        except Exception as e:
            logger.error(f"Error generando imagen de espectrograma para pk={pk}: {e}", exc_info=True)
            return HttpResponse(status=500)

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