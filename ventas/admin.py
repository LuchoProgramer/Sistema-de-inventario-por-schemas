from django.contrib import admin
from .models import Venta, NotaVenta, CierreCaja

class VentaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'sucursal', 'empleado', 'cantidad', 'precio_unitario', 'total_venta', 'metodo_pago', 'fecha']
    list_filter = ['fecha', 'sucursal', 'empleado', 'metodo_pago']
    search_fields = ['producto__nombre', 'sucursal__nombre', 'empleado__username']

class NotaVentaAdmin(admin.ModelAdmin):
    list_display = ['numero_documento', 'tipo_documento', 'fecha_emision', 'monto_total', 'cliente_nombre', 'cliente_ci_ruc', 'cliente_direccion']
    list_filter = ['tipo_documento', 'fecha_emision']
    search_fields = ['numero_documento', 'cliente_nombre', 'cliente_ci_ruc']

class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'sucursal', 'efectivo_total', 'tarjeta_total', 'transferencia_total', 'salidas_caja', 'fecha_cierre']
    list_filter = ['fecha_cierre', 'sucursal', 'empleado']
    search_fields = ['empleado__username', 'sucursal__nombre']

admin.site.register(Venta, VentaAdmin)
admin.site.register(NotaVenta, NotaVentaAdmin)
admin.site.register(CierreCaja, CierreCajaAdmin)
