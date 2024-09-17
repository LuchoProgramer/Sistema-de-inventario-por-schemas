from django.db import models
from empleados.models import RegistroTurno
from sucursales.models import Sucursal

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
