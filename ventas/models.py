from django.db import models
from inventarios.models import Producto, Inventario, MovimientoInventario
from sucursales.models import Sucursal
from django.contrib.auth.models import User  # Asumiendo que los empleados están basados en el modelo User

class Venta(models.Model):
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    empleado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Relación con el empleado
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # Total de la venta
    metodo_pago = models.CharField(max_length=50, choices=[('Efectivo', 'Efectivo'), ('Tarjeta', 'Tarjeta'), ('Transferencia', 'Transferencia')])
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calcular el total de la venta
        self.total_venta = self.cantidad * self.precio_unitario

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
        return f"Venta de {self.producto.nombre} en {self.sucursal.nombre} - {self.cantidad} unidades - Total: {self.total_venta}"


#Nota de Venta Factura
class NotaVenta(models.Model):
    TIPO_DOCUMENTO = [
        ('NOTA', 'Nota de Venta'),
        ('FACTURA', 'Factura'),
    ]

    numero_documento = models.CharField(max_length=20, unique=True)
    tipo_documento = models.CharField(max_length=7, choices=TIPO_DOCUMENTO)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    cliente_nombre = models.CharField(max_length=200, null=True, blank=True, default='Consumidor Final')
    cliente_ci_ruc = models.CharField(max_length=13, null=True, blank=True)
    cliente_direccion = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calcular el monto total de la venta antes de guardar
        if self.pk:
            self.monto_total = sum(venta.total_venta for venta in self.ventas.all())

        # Validar que los campos requeridos estén completos si es una factura
        if self.tipo_documento == 'FACTURA':
            if not self.cliente_nombre or not self.cliente_ci_ruc or not self.cliente_direccion:
                raise ValueError("Los campos del cliente son obligatorios para una factura.")
        else:
            # Para notas de venta, se asegura que el cliente sea "Consumidor Final" si no se dan detalles
            if not self.cliente_nombre:
                self.cliente_nombre = "Consumidor Final"

        super(NotaVenta, self).save(*args, **kwargs)

        # Actualizar el monto total después de guardar
        if not self.pk:
            self.monto_total = sum(venta.total_venta for venta in self.ventas.all())
            super(NotaVenta, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo_documento} {self.numero_documento} - Total: {self.monto_total}"



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

    def verificar_montos(self):
        # Importar aquí para evitar el ciclo de importación
        from ventas.models import Venta
        
        # Implementación para verificar que los montos registrados coinciden con las ventas.
        ventas = Venta.objects.filter(fecha__date=self.fecha_cierre.date(), sucursal=self.sucursal, empleado=self.empleado)
        total_ventas_efectivo = sum(venta.total_venta for venta in ventas.filter(metodo_pago='Efectivo'))
        total_ventas_tarjeta = sum(venta.total_venta for venta in ventas.filter(metodo_pago='Tarjeta'))
        total_ventas_transferencia = sum(venta.total_venta for venta in ventas.filter(metodo_pago='Transferencia'))

        errores = []
        if total_ventas_efectivo != self.efectivo_total:
            errores.append(f"Discrepancia en efectivo: {total_ventas_efectivo} esperado, {self.efectivo_total} registrado.")
        if total_ventas_tarjeta != self.tarjeta_total:
            errores.append(f"Discrepancia en tarjeta: {total_ventas_tarjeta} esperado, {self.tarjeta_total} registrado.")
        if total_ventas_transferencia != self.transferencia_total:
            errores.append(f"Discrepancia en transferencias: {total_ventas_transferencia} esperado, {self.transferencia_total} registrado.")

        return errores or "Los montos coinciden."

    def __str__(self):
        return f"Cierre de Caja - {self.fecha_cierre} - Empleado: {self.empleado.username} - Total Neto: {self.calcular_total_neto()}"
