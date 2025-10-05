# core/services.py

import numpy as np
import pickle # Usaremos pickle para serializar el array de NumPy
from django.utils import timezone
from .influx_client import influx_service
from .models import Muestra, Espectrograma, Clasificacion
from .analysis.stockwell import mst_processing

def procesar_evento_completo(event_id: str):
    """
    Orquesta el pipeline completo:
    1. Extrae datos de InfluxDB.
    2. Crea la entrada en la tabla Muestra.
    3. Calcula la Transformada de Stockwell.
    4. Guarda el espectrograma.
    5. Crea una entrada de Clasificacion inicial.
    """
    print(f"Iniciando procesamiento para event_id: {event_id}...")

    # 1. Verificar si la muestra ya fue procesada en PostgreSQL
    if Muestra.objects.filter(event_id=event_id).exists():
        print(f"El event_id '{event_id}' ya ha sido procesado. Omitiendo.")
        return None

    # 2. Obtener datos de la señal desde InfluxDB
    try:
        # Asumimos que get_signal_data retorna [(timestamp, value), ...]
        puntos_signal = influx_service.get_signal_data(event_id, measurement='voltage_waveform')
        if not puntos_signal or len(puntos_signal) < 5120:
            print(f"No se encontraron suficientes datos para el event_id '{event_id}'.")
            return None
    except Exception as e:
        print(f"Error al obtener datos de InfluxDB para '{event_id}': {e}")
        return None

    # Separar timestamps y valores
    timestamps, valores = zip(*puntos_signal)
    
    # 3. Crear el objeto Muestra en PostgreSQL
    try:
        print("Creando registro de Muestra en PostgreSQL...")
        muestra = Muestra.objects.create(
            event_id=event_id,
            timestamp_inicio=timestamps[0],
            duracion_ms=int((timestamps[-1] - timestamps[0]).total_seconds() * 1000),
            frecuencia_muestreo_hz=30720, # O calcula esto dinámicamente si es necesario
            num_puntos=len(valores),
            estado_procesamiento='pendiente',
        )
    except Exception as e:
        print(f"Error al crear el objeto Muestra en PostgreSQL: {e}")
        return None

    # 4. Calcular la Transformada de Stockwell
    try:
        print("Calculando la Transformada de Stockwell...")
        matriz_espectrograma = mst_processing(valores)
        
        # Serializar la matriz de NumPy a bytes para guardarla en la DB
        espectrograma_bytes = pickle.dumps(matriz_espectrograma)

    except Exception as e:
        print(f"Error al calcular la Transformada de Stockwell: {e}")
        muestra.delete() # Limpiar la muestra creada si el ST falla
        return None

    # 5. Guardar el Espectrograma en PostgreSQL
    try:
        print("Guardando el espectrograma en PostgreSQL...")
        Espectrograma.objects.create(
            muestra=muestra,
            data_espectrograma=espectrograma_bytes,
            metadata_json={
                'shape': matriz_espectrograma.shape,
                'dtype': str(matriz_espectrograma.dtype)
            }
        )
    except Exception as e:
        print(f"Error al guardar el Espectrograma en PostgreSQL: {e}")
        muestra.delete() # Limpiar
        return None

    # 6. Crear una entrada de Clasificacion inicial
    Clasificacion.objects.create(muestra=muestra, estado_clasificacion='pendiente')

    # 7. Actualizar el estado de la muestra a 'procesado'
    muestra.estado_procesamiento = 'procesado'
    muestra.fecha_procesamiento = timezone.now()
    muestra.save()
    
    print(f"✅ Procesamiento del event_id '{event_id}' completado exitosamente.")
    return muestra