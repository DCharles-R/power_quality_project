# core/management/commands/procesar_evento.py

from django.core.management.base import BaseCommand, CommandError
from core.services import procesar_evento_completo

class Command(BaseCommand):
    help = 'Procesa un evento de señal desde InfluxDB y lo guarda en PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=str, help='El ID del evento a procesar')

    def handle(self, *args, **options):
        event_id = options['event_id']
        self.stdout.write(self.style.NOTICE(f"Iniciando el comando para procesar el evento: {event_id}"))
        
        try:
            muestra_procesada = procesar_evento_completo(event_id)
            if muestra_procesada:
                self.stdout.write(self.style.SUCCESS(
                    f'Evento {event_id} procesado exitosamente. Creada Muestra con ID: {muestra_procesada.id}'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'El procesamiento del evento {event_id} no se completó. Revisa los logs.'
                ))
        except Exception as e:
            raise CommandError(f'Ocurrió un error inesperado: {e}')