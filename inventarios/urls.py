from django.urls import path
from . import views

app_name = 'inventarios'

urlpatterns = [
    path('seleccionar-sucursal/', views.seleccionar_sucursal, name='seleccionar_sucursal'),
    path('ver/<int:sucursal_id>/', views.ver_inventario, name='ver_inventario'),
    path('agregar/', views.agregar_producto_inventario, name='agregar_producto_inventario'), #ojo esto esta repetido 
    path('ajustar/<int:producto_id>/<int:sucursal_id>/', views.ajustar_inventario, name='ajustar_inventario'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('categorias/agregar/', views.agregar_categoria, name='agregar_categoria'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/<int:categoria_id>/productos/', views.productos_por_categoria, name='productos_por_categoria'),
    path('productos/<int:producto_id>/ver/', views.ver_producto, name='ver_producto'),
    path('productos/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('transferencias/', views.lista_transferencias, name='lista_transferencias'),
    path('transferencias/crear/', views.crear_transferencia, name='crear_transferencia'),
    path('movimientos/', views.lista_movimientos_inventario, name='lista_movimientos_inventario'),
    path('cargar-productos/', views.cargar_productos, name='cargar_productos'),
    path('agregar-inventario-manual/', views.agregar_inventario_manual, name='agregar_inventario_manual'),
    path('cargar-inventario-excel/', views.cargar_inventario_excel, name='cargar_inventario_excel'),
    path('producto/<int:producto_id>/presentaciones/', views.agregar_presentaciones_multiples, name='agregar_presentaciones_multiples'),
    path('presentacion/eliminar/<int:presentacion_id>/', views.eliminar_presentacion, name='eliminar_presentacion'),

]