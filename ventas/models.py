from django.db import models
from inventarios.models import Producto, Inventario, MovimientoInventario
from sucursales.models import Sucursal

class Venta(models.Model):
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Actualizar el inventario en la sucursal
        inventario = Inventario.objects.get(sucursal=self.sucursal, producto=self.producto)
        if inventario.cantidad < self.cantidad:
            raise ValueError("No hay suficiente inventario para la venta.")
        
        inventario.cantidad -= self.cantidad
        inventario.save()

        # Registrar el movimiento de venta
        MovimientoInventario.objects.create(
            producto=self.producto,
            sucursal=self.sucursal,
            tipo_movimiento='VENTA',
            cantidad=-self.cantidad
        )

        super(Venta, self).save(*args, **kwargs)

    def __str__(self):
        return f"Venta de {self.producto.nombre} en {self.sucursal.nombre} - {self.cantidad} unidades"
