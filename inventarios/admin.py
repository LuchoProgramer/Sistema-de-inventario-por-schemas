from django.contrib import admin
from .models import Producto, Inventario, Compra, Transferencia

admin.site.register(Producto)
admin.site.register(Inventario)
admin.site.register(Compra)
admin.site.register(Transferencia)