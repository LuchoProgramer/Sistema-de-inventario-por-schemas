from django.contrib import admin
from .models import Producto, Categoria, Inventario, Compra, Transferencia, MovimientoInventario

class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio_compra', 'precio_venta', 'unidad_medida']
    list_filter = ['categoria']
    search_fields = ['nombre', 'categoria__nombre']

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Inventario)
admin.site.register(Compra)
admin.site.register(Transferencia)
admin.site.register(MovimientoInventario)
