from django.contrib import admin
from .models import Cliente, Factura, DetalleFactura, Pago, Impuesto, FacturaImpuesto

admin.site.register(Cliente)
admin.site.register(Factura)
admin.site.register(DetalleFactura)
admin.site.register(Pago)
admin.site.register(Impuesto)
admin.site.register(FacturaImpuesto)

