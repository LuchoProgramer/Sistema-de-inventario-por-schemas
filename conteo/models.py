from django.db import models
from django.contrib.auth.models import User
from inventarios.models import Producto
from django.core.exceptions import ValidationError

class ConteoDiario(models.Model):
    sucursal = models.CharField(max_length=100)  # Sucursal como texto
    empleado = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_conteo = models.DateField(auto_now_add=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_contada = models.IntegerField()

    def __str__(self):
        return f"Conteo de {self.producto.nombre} en {self.sucursal} - {self.cantidad_contada} unidades"

    def clean(self):
        if self.cantidad_contada < 0:
            raise ValidationError('La cantidad contada no puede ser negativa.')
        if not self.sucursal:
            raise ValidationError('La sucursal no puede estar vacía.')
