# ventas/urls.py

from django.urls import path
from .views import registrar_venta, inicio_turno, agregar_al_carrito, ver_carrito, finalizar_venta, cerrar_turno

app_name = 'ventas'  # Define el namespace

urlpatterns = [
    path('registrar/', registrar_venta, name='registrar_venta'),
    path('inicio_turno/', inicio_turno, name='inicio_turno'),
    path('agregar/<int:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', ver_carrito, name='ver_carrito'),
    path('finalizar/', finalizar_venta, name='finalizar_venta'),
    path('cerrar_turno/', cerrar_turno, name='cerrar_turno'),
]