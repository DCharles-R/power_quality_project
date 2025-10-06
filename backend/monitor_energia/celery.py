# monitor_energia/celery.py

import os
from celery import Celery

# Establece la variable de entorno para la configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitor_energia.settings')

# Crea una instancia de Celery
app = Celery('monitor_energia')

# Carga la configuración de Celery desde el objeto de configuración de Django.
# El nombre de la configuración debe comenzar con CELERY, por ejemplo, CELERY_BROKER_URL.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubre automáticamente las tareas en todos tus archivos tasks.py
# de las aplicaciones de Django listadas en INSTALLED_APPS.
app.autodiscover_tasks()

# Tarea de depuración (opcional, para probar que Celery funciona)
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')