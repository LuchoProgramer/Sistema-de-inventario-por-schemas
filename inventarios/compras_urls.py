from django.urls import path
from . import compras_views

app_name = 'compras'

urlpatterns = [
    path('', compras_views.lista_compras, name='lista_compras'),
    path('crear/', compras_views.crear_compra_con_productos, name='crear_compra_con_productos'),
    path('<int:compra_id>/', compras_views.detalle_compra, name='detalle_compra'),
    path('subir-xml/', compras_views.procesar_compra_xml, name='procesar_compra_xml'),
]