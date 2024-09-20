from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establecer el módulo de configuración de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventario.settings')

app = Celery('inventario')

# Cargar la configuración desde el archivo settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks.py en las aplicaciones instaladas
app.autodiscover_tasks()
