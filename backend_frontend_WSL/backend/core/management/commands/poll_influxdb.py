# core/management/commands/poll_influxdb.py

import logging
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Muestra
from core.influx_client import influx_service
from core.tasks import procesar_evento_completo_task

# Configurar un logger para este comando
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Busca nuevos eventos en InfluxDB, los crea en PostgreSQL y despacha tareas de procesamiento.'

    def add_arguments(self, parser):
        # Argumento opcional para definir el rango de tiempo en minutos
        parser.add_argument(
            '--minutes',
            type=int,
            default=5,
            help='El rango de tiempo en minutos para buscar nuevos eventos (por defecto: 5).',
        )

    def handle(self, *args, **options):
        time_range = options['minutes']
        self.stdout.write(self.style.NOTICE(f"[{timezone.now()}] Iniciando sondeo de InfluxDB para nuevos eventos en los últimos {time_range} minutos..."))

        # 1. Obtener event_ids recientes de InfluxDB
        recent_event_ids = influx_service.get_recent_event_ids(time_range_minutes=time_range)

        if not recent_event_ids:
            self.stdout.write(self.style.SUCCESS("No se encontraron nuevos eventos en InfluxDB en este período."))
            return

        # 2. Obtener los event_ids que YA existen en nuestra base de datos PostgreSQL
        existing_event_ids = set(Muestra.objects.filter(event_id__in=recent_event_ids).values_list('event_id', flat=True))
        logger.info(f"{len(existing_event_ids)} de los eventos recientes ya existen en la base de datos.")

        # 3. Determinar los event_ids que son verdaderamente nuevos
        new_event_ids = [event_id for event_id in recent_event_ids if event_id not in existing_event_ids]

        if not new_event_ids:
            self.stdout.write(self.style.SUCCESS("Todos los eventos recientes ya estaban registrados. No hay nada que hacer."))
            return

        self.stdout.write(self.style.NOTICE(f"Se encontraron {len(new_event_ids)} eventos nuevos para procesar: {new_event_ids}"))

        # 4. Crear Muestras y despachar tareas para los nuevos event_ids
        muestras_creadas_count = 0
        for event_id in new_event_ids:
            try:
                # Crear la Muestra en estado 'pendiente'
                # El timestamp_inicio se puede obtener del propio event_id
                ts_inicio_naive = timezone.datetime.fromtimestamp(int(event_id) / 1_000_000_000)
                ts_inicio_aware = timezone.make_aware(ts_inicio_naive, datetime.timezone.utc)

                nueva_muestra = Muestra.objects.create(
                    event_id=event_id,
                    timestamp_inicio=ts_inicio_aware,
                    estado_procesamiento='pendiente',
                    duracion_ms=166,
                    frecuencia_muestreo_hz=30720,
                    origen_hardware='NUCLEO-H7S3L8',
                    # Otros campos pueden dejarse en blanco para ser llenados por la tarea
                )
                muestras_creadas_count += 1
                logger.info(f"Creada Muestra con ID {nueva_muestra.id} para event_id {event_id}.")

                # Despachar la tarea de Celery para esta nueva muestra
                procesar_evento_completo_task.delay(nueva_muestra.id)
                logger.info(f"Tarea de procesamiento despachada para Muestra ID {nueva_muestra.id}.")

            except Exception as e:
                logger.error(f"No se pudo crear la Muestra o despachar la tarea para el event_id {event_id}: {e}", exc_info=True)

        self.stdout.write(self.style.SUCCESS(f"Proceso completado. Se crearon y despacharon {muestras_creadas_count} nuevas muestras."))