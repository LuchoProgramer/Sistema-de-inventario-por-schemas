from django.urls import path
from . import views

app_name = 'facturacion'

urlpatterns = [
    path('generar_cotizacion/', views.generar_cotizacion, name='generar_cotizacion'),
    path('generar_factura/', views.generar_factura, name='generar_factura'),
    path('ver_pdf_factura/<str:numero_autorizacion>/', views.ver_pdf_factura, name='ver_pdf_factura'),
]
