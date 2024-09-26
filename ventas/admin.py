from django.contrib import admin
from .models import Venta, CierreCaja

class VentaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'sucursal', 'usuario', 'cantidad', 'precio_unitario', 'total_venta', 'fecha']  # Cambiado empleado por usuario
    list_filter = ['fecha', 'sucursal', 'usuario']  # Cambiado empleado por usuario
    search_fields = ['producto__nombre', 'sucursal__nombre', 'usuario__username']  # Cambiado empleado por usuario y usando username

class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'sucursal', 'efectivo_total', 'tarjeta_total', 'transferencia_total', 'salidas_caja', 'fecha_cierre']  # Cambiado empleado por usuario
    list_filter = ['fecha_cierre', 'sucursal', 'usuario']  # Cambiado empleado por usuario
    search_fields = ['usuario__username', 'sucursal__nombre']  # Cambiado empleado por usuario y usando username

admin.site.register(Venta, VentaAdmin)
admin.site.register(CierreCaja, CierreCajaAdmin)

