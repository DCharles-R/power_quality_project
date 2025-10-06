# core/tasks.py

import numpy as np
import pickle
from django.utils import timezone
from celery import shared_task

from .influx_client import influx_service
from .models import Muestra, Espectrograma, Clasificacion
from .analysis.stockwell import mst_processing

@shared_task
def procesar_evento_completo_task(muestra_id: int): # <<-- CAMBIO 1: Recibe muestra_id (entero)
    """
    Tarea de Celery que orquesta el pipeline completo:
    1. Busca la Muestra por su ID.
    2. Extrae datos de InfluxDB.
    3. Calcula la Transformada de Stockwell.
    4. Guarda el espectrograma.
    5. Crea una entrada de Clasificacion inicial.
    6. Actualiza la Muestra a 'procesado'.
    """
    try:
        # <<-- CAMBIO 2: Buscar la muestra por su ID al inicio
        muestra = Muestra.objects.get(id=muestra_id)
        event_id = muestra.event_id
        print(f"[{timezone.now()}] Iniciando procesamiento ASÍNCRONO para Muestra ID: {muestra.id} (Event ID: {event_id})...")

        # <<-- CAMBIO 3: La verificación ahora es sobre el estado de esta muestra específica
        if muestra.estado_procesamiento == 'procesado':
            print(f"[{timezone.now()}] La muestra con ID {muestra.id} ya está en estado 'procesado'. Omitiendo.")
            return None

    except Muestra.DoesNotExist:
        print(f"[{timezone.now()}] Error: No se encontró una muestra con el ID {muestra_id}.")
        return None


    # 2. Obtener datos de la señal desde InfluxDB
    try:
        puntos_signal = influx_service.get_signal_data(event_id, 'voltage_waveform')
        if not puntos_signal or len(puntos_signal) < 5120:
            print(f"[{timezone.now()}] No se encontraron suficientes datos para el event_id '{event_id}'.")
            muestra.estado_procesamiento = 'error' # Marcar como error
            muestra.save()
            return None
    except Exception as e:
        print(f"[{timezone.now()}] Error al obtener datos de InfluxDB para '{event_id}': {e}")
        muestra.estado_procesamiento = 'error' # Marcar como error
        muestra.save()
        return None

    # Separar timestamps y valores
    timestamps, valores = zip(*puntos_signal)

    # <<-- CAMBIO 4: ELIMINAR el bloque "Crear el objeto Muestra en PostgreSQL"
    # Ya no creamos la muestra, la estamos actualizando.

    # 4. Calcular la Transformada de Stockwell
    try:
        print(f"[{timezone.now()}] Calculando la Transformada de Stockwell...")
        matriz_espectrograma = mst_processing(valores)
        espectrograma_bytes = pickle.dumps(matriz_espectrograma)

    except Exception as e:
        print(f"[{timezone.now()}] Error al calcular la Transformada de Stockwell: {e}")
        muestra.estado_procesamiento = 'error' # Marcar como error
        muestra.save()
        return None

    # 5. Guardar el Espectrograma en PostgreSQL
    try:
        print(f"[{timezone.now()}] Guardando el espectrograma en PostgreSQL...")
        Espectrograma.objects.update_or_create( # Usar update_or_create para evitar duplicados si se re-ejecuta
            muestra=muestra,
            defaults={
                'data_espectrograma': espectrograma_bytes,
                'metadata_json': {
                    'shape': [matriz_espectrograma.shape[0], matriz_espectrograma.shape[1]],
                    'dtype': str(matriz_espectrograma.dtype)
                }
            }
        )
    except Exception as e:
        print(f"[{timezone.now()}] Error al guardar el Espectrograma en PostgreSQL: {e}")
        muestra.estado_procesamiento = 'error'
        muestra.save()
        return None

    # 6. Crear una entrada de Clasificacion inicial
    Clasificacion.objects.update_or_create( # Usar update_or_create
        muestra=muestra,
        defaults={'estado_clasificacion': 'pendiente'}
    )

    # 7. Actualizar el estado de la muestra a 'procesado'
    muestra.timestamp_inicio = timestamps[0]
    muestra.duracion_ms = int((timestamps[-1] - timestamps[0]).total_seconds() * 1000)
    muestra.num_puntos = len(valores)
    muestra.estado_procesamiento = 'procesado'
    muestra.fecha_procesamiento = timezone.now()
    muestra.save()

    print(f"[{timezone.now()}] ✅ Procesamiento ASÍNCRONO de la Muestra ID '{muestra.id}' completado exitosamente.")
    return {'status': 'success', 'muestra_id': muestra.id, 'event_id': event_id}