# monitor_energia/__init__.py

# Esto asegurará que la aplicación Celery se cargue cuando se inicie Django.
from .celery import app as celery_app

__all__ = ('celery_app',)