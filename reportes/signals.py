# reportes/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from ventas.models import Venta
from .models import Reporte
from decimal import Decimal

@receiver(post_save, sender=Venta)
def actualizar_reporte_ventas(sender, instance, created, **kwargs):
    if created:
        print(f"Señal disparada para la venta con ID: {instance.id}")
        fecha_venta = instance.fecha.date()

        # Obtener o crear el reporte para la sucursal y fecha de la venta
        reporte, creado = Reporte.objects.get_or_create(
            turno=instance.turno,
            sucursal=instance.sucursal,
            fecha=fecha_venta
        )

        # Inicializar los valores como Decimals
        total_efectivo = Decimal('0.00')
        total_otros_metodos = Decimal('0.00')

        # Recorrer los pagos asociados a la factura de la venta
        for pago in instance.factura.pagos.all():
            if pago.codigo_sri == '01':  # Sin utilización del sistema financiero (efectivo)
                total_efectivo += Decimal(pago.total)  # Convertir total a Decimal
            else:
                total_otros_metodos += Decimal(pago.total)  # Convertir total a Decimal

        # Convertir todos los valores en el reporte a Decimal antes de sumarlos
        reporte.total_efectivo = Decimal(str(reporte.total_efectivo)) + total_efectivo
        reporte.otros_metodos_pago = Decimal(str(reporte.otros_metodos_pago)) + total_otros_metodos
        reporte.total_facturas = int(reporte.total_facturas) + 1  # Asegurarse de que las facturas sean un entero
        reporte.save()

        print(f"Reporte actualizado: {reporte.id} - Total Ventas: {reporte.total_ventas} - Efectivo: {reporte.total_efectivo} - Otros Métodos: {reporte.otros_metodos_pago}")
