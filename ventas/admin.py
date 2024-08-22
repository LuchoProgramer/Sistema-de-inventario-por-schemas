from django.contrib import admin
from .models import Venta

class VentaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'sucursal', 'cantidad', 'precio_unitario', 'fecha']
    list_filter = ['fecha', 'sucursal']

admin.site.register(Venta, VentaAdmin)
