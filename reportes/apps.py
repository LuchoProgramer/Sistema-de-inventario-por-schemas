from django.apps import AppConfig

class ReportesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reportes'

    def ready(self):
        # Importar señales de forma más segura al inicio de la aplicación
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('signals')  # Asegúrate de importar las señales aquí
