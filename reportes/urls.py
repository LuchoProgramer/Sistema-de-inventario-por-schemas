from django.urls import path
from . import views

urlpatterns = [
    # URL para ver el listado de reportes
    path('reportes/', views.reporte_ventas, name='reporte_ventas'),
    
    # URL para ver el detalle de un reporte por su ID
    path('reportes/<int:id>/', views.detalle_reporte, name='detalle_reporte'),
    
    # Otras URLs relacionadas con facturas y ventas pueden ir aquí también
]
