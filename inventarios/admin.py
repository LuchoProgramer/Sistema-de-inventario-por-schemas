from django.contrib import admin
from .models import Producto, Categoria, Inventario, Compra, Transferencia, MovimientoInventario

class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'mostrar_precio_presentacion', 'unidad_medida']
    list_filter = ['categoria']
    search_fields = ['nombre', 'categoria__nombre']

    def mostrar_precio_presentacion(self, obj):
        # Obtener la primera presentación del producto y mostrar su precio
        presentacion = obj.presentaciones.first()
        if presentacion:
            return presentacion.precio
        return "Sin presentación"

    mostrar_precio_presentacion.short_description = 'Precio Presentación'

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']

# Registro de los modelos en el admin
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Inventario)
admin.site.register(Compra)
admin.site.register(Transferencia)
admin.site.register(MovimientoInventario)
