from django.db import models, transaction
from inventarios.models import Producto, Inventario, MovimientoInventario
from sucursales.models import Sucursal
from django.contrib.auth.models import User  # Asumiendo que los empleados están basados en el modelo User
from django.db.models import Sum
from django.core.exceptions import ValidationError
from decimal import Decimal
from facturacion.models import Pago

class Venta(models.Model):
    # Definición de los campos
    turno = models.ForeignKey('RegistroTurnos.RegistroTurno', on_delete=models.CASCADE, related_name='ventas')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    factura = models.ForeignKey('facturacion.Factura', on_delete=models.CASCADE, related_name='ventas', null=False, blank=False)
    fecha = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(
        max_length=2, 
        choices=Pago.METODOS_PAGO_SRI, 
        default='01', 
        help_text="Método de pago utilizado para la venta"
    )

    def clean(self):
        # Validaciones personalizadas
        if self.cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor que cero.')
        if self.precio_unitario <= 0:
            raise ValidationError('El precio unitario debe ser mayor que cero.')
        # Eliminar la verificación de inventario ya que se maneja en `crear_factura()`

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Validar antes de guardar
        try:
            self.full_clean()  # Ejecutar validaciones sin la lógica de inventario
        except ValidationError as e:
            print(f"Error de validación: {str(e)}")
            raise e

        # Calcular el total de la venta con precisión
        self.total_venta = (self.cantidad * self.precio_unitario).quantize(Decimal('0.01'))

        # Eliminar la lógica de actualización de inventario en `save()` ya que se realiza en `crear_factura()`

        # Guardar la venta
        super(Venta, self).save(*args, **kwargs)
        print(f"Venta guardada exitosamente con ID: {self.id}")

        # Crear el movimiento de reporte después de la venta
        from django.apps import apps
        MovimientoReporte = apps.get_model('reportes', 'MovimientoReporte')  # Obtener el modelo de MovimientoReporte
        Pago = apps.get_model('facturacion', 'Pago')  # Obtener el modelo Pago

        print("Creando Movimiento de Reporte...")

        # Crear un movimiento de reporte
        movimiento = MovimientoReporte.objects.create(
            venta=self,
            turno=self.turno,
            sucursal=self.sucursal,
            total_venta=self.total_venta,
            pago=Pago.objects.filter(factura=self.factura).first()  # Relacionar con el pago si existe
        )

        print(f"Movimiento de reporte creado exitosamente con ID: {movimiento.id}")

    def __str__(self):
        return f"Venta de {self.producto.nombre} en {self.sucursal.nombre} - {self.cantidad} unidades - Total: {self.total_venta}"



#Cierra de caja
class CierreCaja(models.Model):
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)
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
        from ventas.models import Venta  # Evitar ciclos de importación

        # Filtrar las ventas para la fecha, sucursal y empleado específicos
        ventas = Venta.objects.filter(
            fecha__date=self.fecha_cierre.date(),
            sucursal=self.sucursal,
            usuario=self.usuario
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
    turno = models.ForeignKey('RegistroTurnos.RegistroTurno', on_delete=models.CASCADE, related_name='carritos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    agregado_el = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validar que la cantidad sea positiva
        if self.cantidad <= 0:
            raise ValidationError('La cantidad del producto debe ser mayor que cero.')

        # Verificar que haya suficiente inventario del producto
        inventario = Inventario.objects.filter(producto=self.producto, sucursal=self.turno.sucursal).first()
        if not inventario or inventario.cantidad < self.cantidad:
            raise ValidationError(f'No hay suficiente stock para {self.producto.nombre}. Disponibles: {self.producto.stock}')

        super().clean()

    def subtotal(self):
        # Calcular subtotal con precisión de dos decimales
        return (self.producto.precio_venta * self.cantidad).quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (en {self.turno.sucursal.nombre})"