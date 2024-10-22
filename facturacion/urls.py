from django.urls import path
from . import views

app_name = 'facturacion'

urlpatterns = [
    # URLs existentes
    path('generar_cotizacion/', views.generar_cotizacion, name='generar_cotizacion'),
    path('generar_factura/', views.generar_factura, name='generar_factura'),
    path('ver_pdf_factura/<str:numero_autorizacion>/', views.ver_pdf_factura, name='ver_pdf_factura'),

    # URLs para gestión de impuestos
    path('impuestos/', views.lista_impuestos, name='lista_impuestos'),  # Listar todos los impuestos
    path('impuestos/nuevo/', views.crear_impuesto, name='crear_impuesto'),  # Crear un nuevo impuesto
    path('impuestos/<int:impuesto_id>/editar/', views.actualizar_impuesto, name='actualizar_impuesto'),  # Editar un impuesto existente
    path('impuestos/<int:impuesto_id>/eliminar/', views.eliminar_impuesto, name='eliminar_impuesto'), 
    path('crear_cliente_ajax/', views.crear_cliente_ajax, name='crear_cliente_ajax'),
]
