from django.apps import AppConfig

class ReportesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reportes'

    def ready(self):
        pass  # Se ha eliminado el registro de las señales aquí
