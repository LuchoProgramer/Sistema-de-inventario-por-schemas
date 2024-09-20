from django.db import models
from django.core.exceptions import ValidationError

class ConteoDiario(models.Model):
    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE)  # Relación como cadena de texto
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    fecha_conteo = models.DateField(auto_now_add=True)
    producto = models.ForeignKey('inventarios.Producto', on_delete=models.CASCADE)  # Si hay problema con Producto
    cantidad_contada = models.IntegerField()

    def __str__(self):
        return f"Conteo de {self.producto.nombre} en {self.sucursal.nombre} - {self.cantidad_contada} unidades"

    def clean(self):
        if self.cantidad_contada < 0:
            raise ValidationError('La cantidad contada no puede ser negativa.')
        if not self.sucursal:
            raise ValidationError('La sucursal no puede estar vacía.')

    def diferencia_stock(self):
        return self.cantidad_contada - self.producto.stock  # Comparar con el stock actual
