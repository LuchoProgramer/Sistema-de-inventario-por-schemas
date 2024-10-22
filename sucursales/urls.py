from django.urls import path
from . import views

app_name = 'sucursales'

urlpatterns = [
    path('', views.lista_sucursales, name='lista_sucursales'),
    path('crear/', views.crear_sucursal, name='crear_sucursal'),
    path('<int:sucursal_id>/editar/', views.editar_sucursal, name='editar_sucursal'),
    path('<int:sucursal_id>/eliminar/', views.eliminar_sucursal, name='eliminar_sucursal'),
    path('razon_social/crear/', views.crear_razon_social, name='crear_razon_social'),
]
