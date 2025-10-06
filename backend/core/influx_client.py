# core/influx_client.py

import os
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from django.conf import settings

class InfluxService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(InfluxService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'): # Solo inicializa una vez
            self.url = settings.INFLUXDB_V2_URL
            self.token = settings.INFLUXDB_V2_TOKEN
            self.org = settings.INFLUXDB_V2_ORG
            self.bucket = settings.INFLUXDB_V2_BUCKET
            self._client = None
            self._query_api = None
            self._write_api = None
            self._initialized = True # Marca como inicializado

    @property
    def client(self):
        if self._client is None:
            self._client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        return self._client

    @property
    def query_api(self):
        if self._query_api is None:
            self._query_api = self.client.query_api()
        return self._query_api

    @property
    def write_api(self):
        if self._write_api is None:
            # Use SYNCHRONOUS para asegurar que las escrituras se completen antes de continuar
            self._write_api = self.client.write_api(write_options=WriteOptions(batch_size=500, flush_interval=10_000, write_type=SYNCHRONOUS))
        return self._write_api

    def get_signal_data(self, event_id: str, measurement: str):
        """
        Recupera los 5120 puntos de una señal de InfluxDB dado un event_id.
        Asume que los puntos están bajo un 'measurement' y 'event_id' tag.
        Retorna una lista de tuplas (timestamp, value).
        """
        query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: 0) // Consulta desde el inicio para asegurarnos de capturar todo
            |> filter(fn: (r) => r._measurement == "{measurement}")
            |> filter(fn: (r) => r.event_id == "{event_id}")
            |> sort(columns: ["_time"])
            |> yield(name: "mean")
        '''
        tables = self.query_api.query(query, org=self.org)

        data = []
        for table in tables:
            for record in table.records:
                data.append((record.get_time(), record.get_value()))

        # Asegurar que los datos estén ordenados por tiempo y que sean 5120 puntos
        # Si hay más, tomar los primeros 5120 o ajustar lógica según necesidad
        data = sorted(data, key=lambda x: x[0])
        if len(data) > 5120:
            data = data[:5120] # Tomar solo los primeros 5120 puntos si hay más
        elif len(data) < 5120:
             print(f"Advertencia: El event_id {event_id} tiene menos de 5120 puntos ({len(data)}).")
             # Manejar el caso de datos incompletos si es necesario, ej. rellenar con ceros o descartar

        return data

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._query_api = None
            self._write_api = None


# Instancia Singleton para usar en toda la aplicación
influx_service = InfluxService()