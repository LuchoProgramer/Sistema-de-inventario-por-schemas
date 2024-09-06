from django.urls import path
from . import views

app_name = 'inventarios'

urlpatterns = [
    path('seleccionar-sucursal/', views.seleccionar_sucursal, name='seleccionar_sucursal'),
    path('ver/<int:sucursal_id>/', views.ver_inventario, name='ver_inventario'),
    path('agregar/', views.agregar_producto_inventario, name='agregar_producto_inventario'),
    path('ajustar/<int:producto_id>/<int:sucursal_id>/', views.ajustar_inventario, name='ajustar_inventario'),
    path('compras/agregar/', views.agregar_compra, name='agregar_compra'),
    path('compras/ver/', views.ver_compras, name='ver_compras'),
]