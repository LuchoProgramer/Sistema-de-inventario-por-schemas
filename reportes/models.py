from django.db import models
from empleados.models import RegistroTurno
from sucursales.models import Sucursal
from ventas.models import Venta
from django.db.models.signals import post_save
from django.dispatch import receiver

class Reporte(models.Model):
    turno = models.ForeignKey(RegistroTurno, on_delete=models.CASCADE, related_name='reportes', null=True, blank=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_facturas = models.IntegerField(default=0)
    total_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    otros_metodos_pago = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fecha = models.DateField()  # Eliminamos auto_now_add para mayor control
    
    def __str__(self):
        return f'Reporte de {self.sucursal} en el turno {self.turno}'

    class Meta:
        ordering = ['fecha']

@receiver(post_save, sender=Venta)
def actualizar_reporte_ventas(sender, instance, created, **kwargs):
    if created:
        # Obtener la fecha de la venta
        fecha_venta = instance.fecha.date()

        # Buscar o crear un reporte para este turno, sucursal y fecha de la venta
        reporte, creado = Reporte.objects.get_or_create(
            turno=instance.turno,
            sucursal=instance.sucursal,
            fecha=fecha_venta
        )

        # Actualizar el total de ventas y el número de facturas
        reporte.total_ventas += instance.total_venta
        reporte.total_facturas += 1
        reporte.save()
