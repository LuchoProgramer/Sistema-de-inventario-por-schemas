# conteo/urls.py
from django.urls import path
from .views import enviar_conteo

urlpatterns = [
    path('enviar-conteo/', enviar_conteo, name='enviar_conteo'),
]
