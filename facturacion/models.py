from django.db import models
from empleados.models import Empleado
from sucursales.models import Sucursal
from inventarios.models import Producto
from django.core.exceptions import ValidationError


class Cliente(models.Model):
    TIPO_IDENTIFICACION_OPCIONES = [
        ('04', 'RUC'),
        ('05', 'Cédula'),
        ('06', 'Pasaporte'),
        ('07', 'Consumidor Final'),
    ]

    identificacion = models.CharField(max_length=13, unique=True)
    tipo_identificacion = models.CharField(max_length=2, choices=TIPO_IDENTIFICACION_OPCIONES)
    razon_social = models.CharField(max_length=200)
    direccion = models.CharField(max_length=300, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f'{self.razon_social} ({self.identificacion})'


class Factura(models.Model):
    ESTADOS_FACTURA = [
        ('EN_PROCESO', 'En Proceso'),
        ('AUTORIZADA', 'Autorizada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    numero_autorizacion = models.CharField(max_length=49, unique=True, null=True, blank=True)
    clave_acceso = models.CharField(max_length=49, unique=True, null=True, blank=True)
    total_sin_impuestos = models.DecimalField(max_digits=10, decimal_places=2)
    total_con_impuestos = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS_FACTURA, default='EN_PROCESO')

    def __str__(self):
        return f'Factura {self.numero_autorizacion} para {self.cliente.razon_social}'
    

class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
        if self.precio_unitario <= 0:
            raise ValidationError("El precio unitario debe ser mayor que cero.")
        if self.subtotal <= 0 or self.total <= 0:
            raise ValidationError("El subtotal y el total deben ser valores positivos.")

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad} unidades'
    


class Pago(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pagos')
    forma_pago = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.valor <= 0:
            raise ValidationError("El valor del pago debe ser mayor que cero.")

    def __str__(self):
        return f'Pago de {self.valor} para {self.factura.numero_autorizacion}'
    


from django.db import models

class Impuesto(models.Model):
    nombre = models.CharField(max_length=100)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.nombre} - {self.porcentaje}%'


class FacturaImpuesto(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='impuestos')
    impuesto = models.ForeignKey(Impuesto, on_delete=models.CASCADE)
    base_imponible = models.DecimalField(max_digits=10, decimal_places=2)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.impuesto.nombre} para factura {self.factura.numero_autorizacion}'
