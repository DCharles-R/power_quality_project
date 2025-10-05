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
from .services import procesar_evento_completo
import pickle
import numpy as np

# Create your views here.
# core/views.py

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] # Solo usuarios autenticados pueden ver usuarios

class MuestraViewSet(viewsets.ModelViewSet):
    queryset = Muestra.objects.all().select_related('usuario_creacion') # Optimizamos la carga del usuario relacionado
    serializer_class = MuestraSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='process')
    def process_event(self, request, pk=None):
        """
        Endpoint para disparar el procesamiento de un evento por su ID de muestra (PK).
        """
        muestra = self.get_object() # Obtiene la instancia de Muestra por su PK
        event_id = muestra.event_id

        if muestra.estado_procesamiento == 'procesado':
            return Response({'detail': f'La muestra {event_id} ya ha sido procesada.'}, status=status.HTTP_200_OK)

        try:
            # Dispara la función de procesamiento. Esto idealmente debería ser asíncrono.
            # Por ahora, se ejecuta en la misma petición HTTP.
            processed_muestra = procesar_evento_completo(event_id)
            if processed_muestra:
                serializer = self.get_serializer(processed_muestra)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'El procesamiento no se completó, revisa los logs.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], url_path='espectrograma-data')
    def get_espectrograma_data(self, request, pk=None):
        """
        Endpoint para obtener los datos binarios del espectrograma asociado a una muestra.
        """
        try:
            muestra = self.get_object()
            espectrograma = Espectrograma.objects.get(muestra=muestra)

            # Deserializar los bytes a una matriz de NumPy
            matriz_espectrograma = pickle.loads(espectrograma.data_espectrograma)

            # Puedes convertirlo a una lista o un formato JSON compatible
            # Para fines de demostración, lo enviamos como una lista de listas
            # o como un objeto que incluya metadatos y los datos como una lista

            # Ejemplo: Convertir a lista para JSON
            espectrograma_data_list = matriz_espectrograma.tolist()

            return Response({
                'muestra_id': muestra.id,
                'event_id': muestra.event_id,
                'shape': matriz_espectrograma.shape,
                'dtype': str(matriz_espectrograma.dtype),
                'data': espectrograma_data_list # Esto puede ser muy grande, considerar streaming o paginación
            })
        except Muestra.DoesNotExist:
            return Response({'detail': 'Muestra no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        except Espectrograma.DoesNotExist:
            return Response({'detail': 'Espectrograma no encontrado para esta muestra.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EspectrogramaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Espectrograma.objects.all().select_related('muestra')
    serializer_class = EspectrogramaSerializer
    permission_classes = [IsAuthenticated]

class AnotacionViewSet(viewsets.ModelViewSet):
    queryset = Anotacion.objects.all().select_related('muestra', 'usuario_anotador')
    serializer_class = AnotacionSerializer
    permission_classes = [IsAuthenticated]

class ClasificacionViewSet(viewsets.ModelViewSet):
    queryset = Clasificacion.objects.all().select_related('muestra', 'usuario_validador')
    serializer_class = ClasificacionSerializer
    permission_classes = [IsAuthenticated]