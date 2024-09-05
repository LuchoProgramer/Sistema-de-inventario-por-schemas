from django.urls import path
from . import views
from .views import generar_comprobante_pago, error_view

app_name = 'facturacion'

urlpatterns = [
    path('generar_cotizacion/', views.generar_cotizacion, name='generar_cotizacion'),
    path('generar_factura/', views.generar_factura, name='generar_factura'),
    path('generar-comprobante-pago/', generar_comprobante_pago, name='generar_comprobante_pago'),
    path('error/', error_view, name='error'),
    path('factura_exitosa/', views.factura_exitosa, name='factura_exitosa'),
    path('ver_pdf_factura/<str:numero_autorizacion>/', views.ver_pdf_factura, name='ver_pdf_factura'),
]
