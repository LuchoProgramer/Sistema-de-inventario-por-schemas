from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from ventas.models import Venta
from reportes.models import Reporte

@receiver(post_save, sender=Venta)
def actualizar_reporte_ventas(sender, instance, created, **kwargs):
    if created:
        print(f"Señal disparada para la venta con ID: {instance.id}")
        fecha_venta = instance.fecha.date()
        print(f"Fecha de la venta: {fecha_venta}")

        # Obtener o crear el reporte para la sucursal y fecha de la venta
        reporte, creado = Reporte.objects.get_or_create(
            turno=instance.turno,
            sucursal=instance.sucursal,
            fecha=fecha_venta
        )

        print(f"Reporte {'creado' if creado else 'actualizado'} para la fecha {fecha_venta} y sucursal {instance.sucursal.nombre}")

        # Inicializar los valores como Decimal
        total_efectivo = Decimal('0.00')
        total_otros_metodos = Decimal('0.00')

        # Recorrer los pagos asociados a la factura de la venta
        for pago in instance.factura.pagos.all():
            if pago.codigo_sri == '01':  # Efectivo
                total_efectivo += Decimal(pago.total)  # Convertir siempre a Decimal
            else:
                total_otros_metodos += Decimal(pago.total)  # Convertir siempre a Decimal

        print(f"Total efectivo: {total_efectivo}, Otros métodos de pago: {total_otros_metodos}")

        # Convertir los valores de reporte a Decimal antes de sumarlos
        reporte.total_efectivo = Decimal(reporte.total_efectivo) + total_efectivo
        reporte.otros_metodos_pago = Decimal(reporte.otros_metodos_pago) + total_otros_metodos
        reporte.total_facturas = int(reporte.total_facturas) + 1  # Asegurarse de que las facturas sean un entero
        reporte.save()

        print(f"Reporte actualizado: {reporte.id} - Total efectivo: {reporte.total_efectivo}, Total facturas: {reporte.total_facturas}")
