# conteo/models.py
from django.db import models
from django.contrib.auth.models import User
from inventarios.models import Producto, Sucursal

class ConteoDiario(models.Model):
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    empleado = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_conteo = models.DateField(auto_now_add=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_contada = models.IntegerField()

    def __str__(self):
        return f"Conteo de {self.producto.nombre} en {self.sucursal.nombre} - {self.cantidad_contada} unidades"
