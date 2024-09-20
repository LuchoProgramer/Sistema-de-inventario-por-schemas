from django.contrib import admin
from .models import Venta, CierreCaja

class VentaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'sucursal', 'empleado', 'cantidad', 'precio_unitario', 'total_venta', 'fecha']
    list_filter = ['fecha', 'sucursal', 'empleado']
    search_fields = ['producto__nombre', 'sucursal__nombre', 'empleado__nombre']  # Cambiado de username a nombre

class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'sucursal', 'efectivo_total', 'tarjeta_total', 'transferencia_total', 'salidas_caja', 'fecha_cierre']
    list_filter = ['fecha_cierre', 'sucursal', 'empleado']
    search_fields = ['empleado__nombre', 'sucursal__nombre']  # Cambiado de username a nombre

admin.site.register(Venta, VentaAdmin)
admin.site.register(CierreCaja, CierreCajaAdmin)

