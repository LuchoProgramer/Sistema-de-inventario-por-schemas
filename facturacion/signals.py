from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Factura
from ventas.models import Venta

@receiver(post_save, sender=Factura)
def crear_venta_desde_factura(sender, instance, created, **kwargs):
    # Verificar que instance es de tipo Factura
    if isinstance(instance, Factura):
        # Verificar si la factura tiene detalles
        if instance.detalles.exists():
            if created:
                # Recorrer todos los detalles de la factura al crearla
                for detalle in instance.detalles.all():
                    Venta.objects.create(
                        turno=instance.registroturno,
                        empleado=instance.empleado,
                        producto=detalle.producto,
                        cantidad=detalle.cantidad,
                        precio_unitario=detalle.precio_unitario,
                        total_venta=detalle.total,
                        sucursal=instance.sucursal,
                        factura=instance  # Relacionar la venta con la factura
                    )
            else:
                # Actualizar todas las ventas correspondientes a la factura
                for detalle in instance.detalles.all():
                    venta = Venta.objects.filter(factura=instance, producto=detalle.producto).first()
                    if venta:
                        venta.cantidad = detalle.cantidad
                        venta.precio_unitario = detalle.precio_unitario
                        venta.total_venta = detalle.total
                        venta.save()
        else:
            # Manejar el caso en que no haya detalles en la factura
            print("Error: La factura no tiene detalles asociados.")
    else:
        # Manejar el caso en que instance no sea del modelo Factura
        print("Error: El objeto instance no es una factura válida.")
