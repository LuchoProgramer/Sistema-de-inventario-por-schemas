from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from ventas.models import Carrito
from empleados.models import Empleado, RegistroTurno
from sucursales.models import Sucursal
from inventarios.models import Producto, Inventario
from facturacion.models import Cliente, Impuesto, DetalleFactura, Factura
from facturacion.services import crear_factura
from decimal import Decimal, ROUND_HALF_UP


class TestFacturaRegistroTurno(TestCase):
    def setUp(self):
        # Crear un usuario y empleado
        self.usuario = User.objects.create(username='testuser', password='testpassword')
        self.empleado = Empleado.objects.create(usuario=self.usuario, nombre='Empleado Test')

        # Crear una sucursal con los campos obligatorios
        self.sucursal = Sucursal.objects.create(
            nombre='Sucursal 1', 
            direccion='Dirección 1',
            razon_social='Empresa Test',
            telefono='0987654321',
            ruc='1234567890001',  
            codigo_establecimiento='001',  
            punto_emision='001',  
            secuencial_actual='000000001'
        )

        # Crear un producto
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            descripcion='Descripción del producto',
            precio_compra=10.00,
            precio_venta=15.00,
            unidad_medida='unidad',
            sucursal=self.sucursal,
            categoria=None
        )

        # Crear inventario para el producto
        Inventario.objects.create(producto=self.producto, sucursal=self.sucursal, cantidad=10)

        # Crear un cliente
        self.cliente = Cliente.objects.create(
            identificacion='9999999999',
            tipo_identificacion='07',
            razon_social='Consumidor Final'
        )

        # Crear un turno para el empleado
        self.turno = RegistroTurno.objects.create(
            empleado=self.empleado,
            sucursal=self.sucursal,
            inicio_turno=timezone.now(), 
            fin_turno=None
        )

        # Crear un IVA activo
        self.iva = Impuesto.objects.create(
            codigo_impuesto='2', 
            nombre='IVA',
            porcentaje=12.00,  # IVA del 12%
            activo=True
        )

    def test_generar_factura(self):
        # Crear un item en el carrito
        Carrito.objects.create(turno=self.turno, producto=self.producto, cantidad=2)

        # Obtener los items del carrito
        carrito_items = Carrito.objects.filter(turno=self.turno)

        # Llamar al servicio para crear la factura
        factura = crear_factura(cliente=self.cliente, sucursal=self.sucursal, empleado=self.empleado, carrito_items=carrito_items)

        # Validar que la factura se ha creado correctamente
        self.assertIsNotNone(factura)
        self.assertEqual(factura.cliente, self.cliente)
        self.assertEqual(factura.sucursal, self.sucursal)

        # Verificar que los detalles de la factura se han creado correctamente
        detalles = DetalleFactura.objects.filter(factura=factura)
        self.assertEqual(detalles.count(), 1)  # Debe haber un solo detalle de la factura
        detalle = detalles.first()
        self.assertEqual(detalle.producto, self.producto)
        self.assertEqual(detalle.cantidad, 2)
        self.assertEqual(detalle.precio_unitario, Decimal('15.00'))  # Verificar que se guarde como Decimal

        # Verificar los valores calculados correctamente con redondeo
        subtotal = (Decimal('15.00') * 2).quantize(Decimal('0.01'))  # Redondear subtotal
        valor_iva = (subtotal * Decimal('0.12')).quantize(Decimal('0.01'))  # Redondear IVA
        total_con_impuestos = (subtotal + valor_iva).quantize(Decimal('0.01'))

        self.assertEqual(factura.total_sin_impuestos, subtotal)
        self.assertEqual(factura.valor_iva, valor_iva)
        self.assertEqual(factura.total_con_impuestos, total_con_impuestos)
