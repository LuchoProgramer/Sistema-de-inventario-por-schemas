from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from decimal import Decimal
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models


class Cliente(models.Model):
    TIPO_IDENTIFICACION_OPCIONES = [
        ('04', 'RUC'),
        ('05', 'Cédula'),
        ('06', 'Pasaporte'),
        ('07', 'Consumidor Final'),
    ]

    identificacion = models.CharField(max_length=13, unique=True, validators=[
        RegexValidator(regex='^\d{10}|\d{13}$', message='La identificación debe tener 10 dígitos (cédula) o 13 dígitos (RUC).')
    ])
    tipo_identificacion = models.CharField(max_length=2, choices=TIPO_IDENTIFICACION_OPCIONES)
    razon_social = models.CharField(max_length=200)
    direccion = models.CharField(max_length=300, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    obligado_contabilidad = models.BooleanField(default=False)

    def clean(self):
        # Validar la identificación según el tipo de identificación
        if self.tipo_identificacion == '04' and len(self.identificacion) != 13:
            raise ValidationError('El RUC debe tener 13 dígitos.')
        if self.tipo_identificacion == '05' and len(self.identificacion) != 10:
            raise ValidationError('La cédula debe tener 10 dígitos.')
        if self.tipo_identificacion == '07' and self.identificacion != '9999999999':
            raise ValidationError('La identificación para Consumidor Final debe ser "9999999999".')

        # Validar que el email sea único si es proporcionado
        if self.email and Cliente.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError('El correo electrónico ya está en uso por otro cliente.')

        super(Cliente, self).clean()

    def __str__(self):
        return f'{self.razon_social} ({self.identificacion})'


def ruta_factura(instance, filename):
    # Guardar todas las facturas directamente en la carpeta 'media'
    return filename  # Solo devolvemos el nombre del archivo, sin crear subcarpetas

    
from django.db import models
from decimal import Decimal

class Factura(models.Model):
    ESTADOS_FACTURA = [
        ('EN_PROCESO', 'En Proceso'),
        ('AUTORIZADA', 'Autorizada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    ESTADOS_PAGO = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO_PARCIAL', 'Pagado Parcialmente'),
        ('PAGADO', 'Pagado'),
    ]

    TIPO_COMPROBANTE_OPCIONES = [
        ('01', 'Factura'),
        ('03', 'Liquidación de compra de bienes y prestación de servicios'),
        ('04', 'Nota de crédito'),
        ('05', 'Nota de débito'),
        ('06', 'Guía de remisión'),
        ('07', 'Comprobante de retención'),
    ]

    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE)
    razon_social = models.ForeignKey('sucursales.RazonSocial', on_delete=models.SET_NULL, null=True, blank=True)  # Nueva relación
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    numero_autorizacion = models.CharField(max_length=49, unique=True)
    clave_acceso = models.CharField(max_length=49, unique=True, null=True, blank=True)
    tipo_comprobante = models.CharField(max_length=2, choices=TIPO_COMPROBANTE_OPCIONES, default='01')
    contribuyente_especial = models.CharField(max_length=5, null=True, blank=True)
    obligado_contabilidad = models.BooleanField(default=False)
    moneda = models.CharField(max_length=10, default='DOLAR')
    total_sin_impuestos = models.DecimalField(max_digits=10, decimal_places=2)
    total_con_impuestos = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS_FACTURA, default='EN_PROCESO')
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='PENDIENTE')
    valor_iva = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    registroturno = models.ForeignKey('RegistroTurnos.RegistroTurno', on_delete=models.CASCADE, null=True, blank=True)
    archivo_pdf = models.FileField(upload_to=ruta_factura, null=True, blank=True)
    es_cotizacion = models.BooleanField(default=False)

    
    class Meta:
        unique_together = ('sucursal', 'numero_autorizacion')



    def calcular_total_pagado(self):
        return sum(pago.total for pago in self.pagos.all())

    def actualizar_estado_pago(self):
        total_pagado = self.calcular_total_pagado()
        if total_pagado >= self.total_con_impuestos:
            self.estado_pago = 'PAGADO'
        elif total_pagado > 0:
            self.estado_pago = 'PAGADO_PARCIAL'
        else:
            self.estado_pago = 'PENDIENTE'
        self.save()

    def clean(self):
        if not self.cliente or not self.cliente.razon_social:
            self.cliente = Cliente.objects.get_or_create(
                identificacion="9999999999",
                defaults={
                    'tipo_identificacion': '07',
                    'razon_social': 'Consumidor Final',
                }
            )[0]
        super(Factura, self).clean()

    def __str__(self):
        return f'Factura {self.numero_autorizacion} para {self.cliente.razon_social}'
    
    

class DetalleFactura(models.Model):
    factura = models.ForeignKey('facturacion.Factura', on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('inventarios.Producto', on_delete=models.CASCADE)
    presentacion = models.ForeignKey('inventarios.Presentacion', on_delete=models.CASCADE)  # Nueva relación con Presentacion
    codigo_principal = models.CharField(max_length=20, null=True, blank=True)  # Código único del producto
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_iva = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def clean(self):
        print(f"Cantidad: {self.cantidad}, Precio Unitario: {self.precio_unitario}, Subtotal esperado: {(self.cantidad * self.precio_unitario) - self.descuento}, Subtotal actual: {self.subtotal}, Descuento: {self.descuento}")
        print(f"Total esperado: {self.subtotal}, Total actual: {self.total}")

        # Validación de cantidad
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
        
        # Validación de precio unitario
        if self.precio_unitario <= 0:
            raise ValidationError("El precio unitario debe ser mayor que cero.")
        
        # Cálculo y validación de subtotal
        if self.subtotal != (self.cantidad * self.precio_unitario) - self.descuento:
            raise ValidationError("El subtotal no es correcto. Debe ser igual a (cantidad * precio unitario) - descuento.")
        
        # Validación del total
        if self.total != self.subtotal:
            raise ValidationError("El total debe ser igual al subtotal.")

        super(DetalleFactura, self).clean()



class Pago(models.Model):
    # Definir los métodos de pago según el SRI
    METODOS_PAGO_SRI = [
        ('01', 'Sin utilización del sistema financiero'),
        ('15', 'Compensación de deudas'),
        ('16', 'Tarjeta de débito'),
        ('17', 'Dinero electrónico'),
        ('18', 'Tarjeta prepago'),
        ('19', 'Tarjeta de crédito'),
        ('20', 'Otros con utilización del sistema financiero'),
        ('21', 'Endoso de títulos'),
    ]

    factura = models.ForeignKey('facturacion.Factura', on_delete=models.CASCADE, related_name="pagos")
    codigo_sri = models.CharField(max_length=2, choices=METODOS_PAGO_SRI, default='01', help_text="Código del método de pago según el SRI")
    descripcion = models.CharField(max_length=100, help_text="Descripción del método de pago", default='Sin descripción')
    total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monto total del pago", default=0.00)
    plazo = models.IntegerField(null=True, blank=True, help_text="Plazo de pago en días, si aplica", default=0)
    unidad_tiempo = models.CharField(max_length=20, null=True, blank=True, help_text="Unidad de tiempo para el plazo, ej. días, meses", default='días')
    fecha_pago = models.DateTimeField(auto_now_add=True)  # Mantener como en el modelo anterior

    def __str__(self):
        return f"{self.descripcion} - {self.total} USD"



class Impuesto(models.Model):
    codigo_impuesto = models.CharField(max_length=2)  # Código SRI del impuesto (ej: '2' para IVA)
    nombre = models.CharField(max_length=100)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)  # Porcentaje del impuesto (ej: 15%)
    activo = models.BooleanField(default=True)  # Para manejar qué impuesto está activo

    def __str__(self):
        return f'{self.nombre} - {self.porcentaje}%'

    def save(self, *args, **kwargs):
        if self.activo and not kwargs.pop('skip_update', False):
            # Desactiva otros impuestos antes de guardar este como activo
            Impuesto.objects.filter(activo=True).update(activo=False)
        super(Impuesto, self).save(*args, **kwargs)

        impuestos_activos = Impuesto.objects.filter(activo=True)
        print(f"Impuestos activos después de guardar: {[impuesto.nombre for impuesto in impuestos_activos]}")




class FacturaImpuesto(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='impuestos')
    impuesto = models.ForeignKey(Impuesto, on_delete=models.CASCADE)
    base_imponible = models.DecimalField(max_digits=10, decimal_places=2)  # Valor sobre el que se calcula el impuesto
    valor = models.DecimalField(max_digits=10, decimal_places=2)  # Valor calculado del impuesto

    def clean(self):
        # Validar que el valor del impuesto sea correcto basado en el porcentaje del impuesto aplicado
        if self.valor != (self.base_imponible * (self.impuesto.porcentaje / 100)).quantize(Decimal('0.01')):
            raise ValidationError('El valor del impuesto no coincide con el porcentaje aplicado sobre la base imponible.')
        super(FacturaImpuesto, self).clean()

    def __str__(self):
        return f'{self.impuesto.nombre} para factura {self.factura.numero_autorizacion}'

    

class Cotizacion(models.Model):
    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    total_sin_impuestos = models.DecimalField(max_digits=10, decimal_places=2)
    total_con_impuestos = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Cotización #{self.id} para {self.cliente.razon_social if self.cliente else "Sin cliente"}'
    
