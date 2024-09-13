from django.urls import path
from . import views

urlpatterns = [
    path('ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('ventas/empleado/', views.reporte_ventas_empleado, name='reporte_ventas_empleado'),
    path('ventas/sucursal/', views.reporte_ventas_sucursal, name='reporte_ventas_sucursal'),
]
