from django.db import models, transaction
from django.core.exceptions import ValidationError
from decimal import Decimal


class Categoria(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=50)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)
    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE, null=True, blank=True)
    codigo_producto = models.CharField(max_length=50, unique=True, null=True, blank=True)
    impuesto = models.ForeignKey('facturacion.Impuesto', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='productos/', null=True, blank=True)
    stock_minimo = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    def calcular_margen(self):
        return self.precio_venta - self.precio_compra

    def obtener_valor_base_iva(self):
        """
        Calcula el valor sin impuestos y el valor del IVA,
        asumiendo que el precio de venta ya incluye IVA.
        Si no hay impuesto, retorna el precio de venta como valor base y 0 como IVA.
        """
        if self.impuesto and self.impuesto.porcentaje > 0:
            valor_base = (self.precio_venta / (1 + self.impuesto.porcentaje / 100)).quantize(Decimal('0.01'))
            valor_iva = (self.precio_venta - valor_base).quantize(Decimal('0.01'))
            return valor_base, valor_iva
        return self.precio_venta.quantize(Decimal('0.01')), Decimal('0.00')

    def calcular_precio_final(self):
        """
        Retorna el precio final del producto, que en este caso es el precio de venta
        que ya incluye el IVA.
        """
        return self.precio_venta

    def clean(self):
        if self.precio_compra <= 0:
            raise ValidationError("El precio de compra debe ser mayor que cero.")
        if self.precio_venta <= 0:
            raise ValidationError("El precio de venta debe ser mayor que cero.")
        if self.precio_venta <= self.precio_compra:
            raise ValidationError("El precio de venta debe ser mayor que el precio de compra para generar un margen positivo.")



class Inventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    class Meta:
        unique_together = ('producto', 'sucursal')

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad} unidades en {self.sucursal.nombre}'

    def clean(self):
        if self.cantidad < 0:
            raise ValidationError("La cantidad en inventario no puede ser negativa.")

class Compra(models.Model):
    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Permitir que sea nulo inicialmente
    fecha = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validar que la cantidad sea un número positivo
        if self.cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor que cero.')

        # Si el precio_unitario es None, establece un valor predeterminado antes de la validación
        if self.precio_unitario is None:
            self.precio_unitario = self.producto.precio_compra

        # Verificar que el precio unitario sea un valor positivo
        if self.precio_unitario <= 0:
            raise ValidationError('El precio unitario debe ser mayor que cero.')

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Ejecutar validaciones antes de guardar
        self.full_clean()  # Esto ejecuta el método clean automáticamente

        # Actualizar el inventario
        inventario, created = Inventario.objects.get_or_create(
            sucursal=self.sucursal,
            producto=self.producto,
            defaults={'cantidad': self.cantidad}
        )
        if not created:
            inventario.cantidad += self.cantidad
            inventario.save()

        # Registrar el movimiento de compra
        MovimientoInventario.objects.create(
            producto=self.producto,
            sucursal=self.sucursal,
            tipo_movimiento='COMPRA',
            cantidad=self.cantidad
        )

        super(Compra, self).save(*args, **kwargs)

    def __str__(self):
        return f"Compra de {self.cantidad} {self.producto.unidad_medida} de {self.producto.nombre} para {self.sucursal.nombre}"

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
