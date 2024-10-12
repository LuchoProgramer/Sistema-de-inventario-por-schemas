from django.db import models, transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from facturacion.models import Impuesto


class Categoria(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    unidad_medida = models.CharField(max_length=50, null=True, blank=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)
    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE, null=True, blank=True)
    codigo_producto = models.CharField(max_length=50, unique=True, null=True, blank=True)
    impuesto = models.ForeignKey('facturacion.Impuesto', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='productos/', null=True, blank=True)
    stock_minimo = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    def obtener_valor_base_iva(self, presentacion):
        if self.impuesto and self.impuesto.porcentaje > 0:
            valor_base = (presentacion.precio / (1 + self.impuesto.porcentaje / 100)).quantize(Decimal('0.01'))
            valor_iva = (presentacion.precio - valor_base).quantize(Decimal('0.01'))
            return valor_base, valor_iva
        return presentacion.precio.quantize(Decimal('0.01')), Decimal('0.00')

    def calcular_precio_final(self, presentacion):
        return presentacion.precio

    def save(self, *args, **kwargs):
        if not self.impuesto:
            self.impuesto = Impuesto.objects.get(porcentaje=15.0)
        super().save(*args, **kwargs)

    def clean(self):
        pass  # Aquí podrías agregar validaciones futuras si lo deseas



class Inventario(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)  # Inventario unificado por producto
    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('producto', 'sucursal')

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad} unidades en {self.sucursal.nombre}'

    def clean(self):
        if self.cantidad < 0:
            raise ValidationError("La cantidad en inventario no puede ser negativa.")


class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)  # Razón Social
    ruc = models.CharField(max_length=13)  # Registro Único de Contribuyentes
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Compra(models.Model):
    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    numero_autorizacion = models.CharField(max_length=50, default='0000000000')
    fecha_emision = models.DateField()  # Extraído del XML
    total_sin_impuestos = models.DecimalField(max_digits=10, decimal_places=2)
    total_con_impuestos = models.DecimalField(max_digits=10, decimal_places=2)
    total_descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    metodo_pago = models.CharField(max_length=50, choices=[('efectivo', 'Efectivo'), ('transferencia', 'Transferencia')], default='efectivo')
    estado = models.CharField(max_length=20, choices=[('completada', 'Completada'), ('pendiente', 'Pendiente'), ('cancelada', 'Cancelada')], default='pendiente')

    def __str__(self):
        return f"Compra en {self.sucursal.nombre} el {self.fecha_emision.strftime('%Y-%m-%d')}"
    

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    codigo_principal = models.CharField(max_length=50)  # Código principal del producto
    descripcion = models.CharField(max_length=255)  # Descripción del producto
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total_por_producto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    impuesto_aplicado = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Porcentaje de impuesto
    valor_impuesto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Valor del impuesto aplicado

    def save(self, *args, **kwargs):
        # Calcular el total por producto (cantidad * precio unitario)
        self.total_por_producto = self.cantidad * self.precio_unitario
        
        # Actualizar el inventario al guardar el detalle de la compra
        inventario, created = Inventario.objects.get_or_create(
            producto=self.producto,
            sucursal=self.compra.sucursal,
            defaults={'cantidad': self.cantidad}
        )
        
        if not created:
            inventario.cantidad += self.cantidad  # Sumar la cantidad comprada al inventario existente
        inventario.save()

        # Llamar al método save de la clase padre
        super(DetalleCompra, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.descripcion} en {self.compra.sucursal.nombre}"
    


class Transferencia(models.Model):
    sucursal_origen = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE, related_name='transferencias_salida')
    sucursal_destino = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE, related_name='transferencias_entrada')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Actualizar inventario en la sucursal de origen
        inventario_origen = Inventario.objects.get(sucursal=self.sucursal_origen, producto=self.producto)
        if inventario_origen.cantidad < self.cantidad:
            raise ValueError("No hay suficiente inventario en la sucursal matriz para transferir.")
        
        inventario_origen.cantidad -= self.cantidad
        inventario_origen.save()

        # Actualizar inventario en la sucursal de destino
        inventario_destino, created = Inventario.objects.get_or_create(
            sucursal=self.sucursal_destino, 
            producto=self.producto
        )
        inventario_destino.cantidad += self.cantidad
        inventario_destino.save()

        # Registrar los movimientos de transferencia
        MovimientoInventario.objects.create(
            producto=self.producto,
            sucursal=self.sucursal_origen,
            tipo_movimiento='TRANSFERENCIA_SALIDA',
            cantidad=-self.cantidad
        )

        MovimientoInventario.objects.create(
            producto=self.producto,
            sucursal=self.sucursal_destino,
            tipo_movimiento='TRANSFERENCIA_ENTRADA',
            cantidad=self.cantidad
        )

        super(Transferencia, self).save(*args, **kwargs)



class MovimientoInventario(models.Model):
    TIPOS_MOVIMIENTO = [
        ('COMPRA', 'Compra'),
        ('TRANSFERENCIA_ENTRADA', 'Transferencia Entrada'),
        ('TRANSFERENCIA_SALIDA', 'Transferencia Salida'),
        ('VENTA', 'Venta'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=25, choices=TIPOS_MOVIMIENTO)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_movimiento} de {self.cantidad} de {self.producto.nombre} en {self.sucursal.nombre}"



class Presentacion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='presentaciones')
    nombre_presentacion = models.CharField(max_length=50)  # Ej. 'Unidad', 'Caja de 10', 'Caja de 20'
    cantidad = models.PositiveIntegerField()  # Cantidad de unidades en esta presentación
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio de la presentación
    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE, related_name='presentaciones')  # Agregar sucursal

    def __str__(self):
        return f"{self.nombre_presentacion} - {self.producto.nombre} - {self.sucursal.nombre}"

    def clean(self):
        if self.precio <= 0:
            raise ValidationError("El precio debe ser mayor que cero.")
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
