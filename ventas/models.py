from django.db import models, transaction
from inventarios.models import Producto, Inventario, MovimientoInventario
from sucursales.models import Sucursal
from django.contrib.auth.models import User  # Asumiendo que los empleados están basados en el modelo User
from django.db.models import Sum
from django.core.exceptions import ValidationError
from decimal import Decimal


class Venta(models.Model):
    turno = models.ForeignKey('empleados.RegistroTurno', on_delete=models.CASCADE, related_name='ventas')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    empleado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Verificar que la cantidad sea un número positivo
        if self.cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor que cero.')

        # Verificar que el precio unitario sea un valor positivo
        if self.precio_unitario <= 0:
            raise ValidationError('El precio unitario debe ser mayor que cero.')

        # Asegurarse de que haya suficiente inventario
        try:
            inventario = Inventario.objects.get(sucursal=self.sucursal, producto=self.producto)
            if inventario.cantidad < self.cantidad:
                raise ValidationError(f"No hay suficiente inventario para la venta. Disponibilidad actual: {inventario.cantidad} unidades.")
        except Inventario.DoesNotExist:
            raise ValidationError("El inventario no existe para este producto y sucursal.")

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Validar los datos antes de guardar
        self.full_clean()  # Esto ejecuta el método clean automáticamente

        # Calcular el total de la venta con precisión de dos decimales
        self.total_venta = (self.cantidad * self.precio_unitario).quantize(Decimal('0.01'))

        # Obtener el inventario y verificar la disponibilidad
        inventario = Inventario.objects.select_for_update().get(sucursal=self.sucursal, producto=self.producto)
        inventario.cantidad -= self.cantidad
        if inventario.cantidad < 0:
            raise ValidationError("El inventario no puede ser negativo después de la venta.")
        inventario.save()

        # Registrar el movimiento de inventario
        MovimientoInventario.objects.create(
            producto=self.producto,
            sucursal=self.sucursal,
            tipo_movimiento='VENTA',
            cantidad=-self.cantidad
        )

        # Guardar la venta
        super(Venta, self).save(*args, **kwargs)

    def __str__(self):
        return f"Venta de {self.producto.nombre} en {self.sucursal.nombre} - {self.cantidad} unidades - Total: {self.total_venta}"


#Cierra de caja
class CierreCaja(models.Model):
    empleado = models.ForeignKey(User, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    efectivo_total = models.DecimalField(max_digits=10, decimal_places=2)
    tarjeta_total = models.DecimalField(max_digits=10, decimal_places=2)
    transferencia_total = models.DecimalField(max_digits=10, decimal_places=2)
    salidas_caja = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_cierre = models.DateTimeField(auto_now_add=True)

    def calcular_total_neto(self):
        return (self.efectivo_total + self.tarjeta_total + self.transferencia_total) - self.salidas_caja

    @transaction.atomic
    def verificar_montos(self):
        # Importar aquí para evitar el ciclo de importación
        from ventas.models import Venta

        # Filtrar las ventas para la fecha, sucursal y empleado específicos
        ventas = Venta.objects.filter(
            fecha__date=self.fecha_cierre.date(),
            sucursal=self.sucursal,
            empleado=self.empleado
        )

        # Realizar agregaciones para calcular los totales directamente en la base de datos
        totales = ventas.values('metodo_pago').annotate(total=Sum('total_venta'))

        # Obtener los totales por cada método de pago o asignar 0 si no existen
        total_ventas_efectivo = Decimal(next((item['total'] for item in totales if item['metodo_pago'] == 'Efectivo'), 0))
        total_ventas_tarjeta = Decimal(next((item['total'] for item in totales if item['metodo_pago'] == 'Tarjeta'), 0))
        total_ventas_transferencia = Decimal(next((item['total'] for item in totales if item['metodo_pago'] == 'Transferencia'), 0))

        errores = []
        if total_ventas_efectivo != self.efectivo_total:
            errores.append(f"Discrepancia en efectivo: {total_ventas_efectivo} esperado, {self.efectivo_total} registrado.")
        if total_ventas_tarjeta != self.tarjeta_total:
            errores.append(f"Discrepancia en tarjeta: {total_ventas_tarjeta} esperado, {self.tarjeta_total} registrado.")
        if total_ventas_transferencia != self.transferencia_total:
            errores.append(f"Discrepancia en transferencias: {total_ventas_transferencia} esperado, {self.transferencia_total} registrado.")

        return errores if errores else "Los montos coinciden."
    


class Carrito(models.Model):
    turno = models.ForeignKey('empleados.RegistroTurno', on_delete=models.CASCADE, related_name='carritos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    agregado_el = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validar que la cantidad sea positiva
        if self.cantidad <= 0:
            raise ValidationError('La cantidad del producto debe ser mayor que cero.')

        # Verificar que haya suficiente inventario del producto
        if self.producto.stock < self.cantidad:
            raise ValidationError(f'No hay suficiente stock para {self.producto.nombre}. Disponibles: {self.producto.stock}')

        super().clean()

    def subtotal(self):
        # Calcular subtotal con precisión de dos decimales
        return (self.producto.precio_venta * self.cantidad).quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (en {self.turno.sucursal.nombre})"