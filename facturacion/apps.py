# facturacion/apps.py

from django.apps import AppConfig

class FacturacionConfig(AppConfig):
    name = 'facturacion'

    def ready(self):
        import facturacion.signals  # Importamos las señales cuando la app esté lista
