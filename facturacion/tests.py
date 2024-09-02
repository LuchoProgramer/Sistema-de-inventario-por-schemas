from django.test import TestCase
from facturacion.models import Factura, DetalleFactura, Cliente, Impuesto, FacturaImpuesto, Pago
from empleados.models import Empleado
from sucursales.models import Sucursal
from inventarios.models import Producto, Categoria
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class FacturaModelTest(TestCase):

    def setUp(self):
        # Crear un usuario de prueba
        self.usuario = User.objects.create_user(username='testuser', password='12345')

        # Crear una categoría, sucursal e impuesto para los productos
        self.categoria = Categoria.objects.create(nombre="Electrónica")
        self.sucursal = Sucursal.objects.create(
            nombre="Sucursal Central", 
            razon_social="Empresa Central S.A.", 
            telefono="0999999999", 
            direccion="Av. Principal 123"
        )
        self.impuesto = Impuesto.objects.create(nombre="IVA", porcentaje=12, monto=0)
        self.cliente = Cliente.objects.create(
            identificacion="1790012345001",
            tipo_identificacion="04",  # RUC
            razon_social="Cliente S.A.",
            direccion="Av. Secundaria 456",
            telefono="0888888888",
            email="cliente@example.com"
        )
        self.producto = Producto.objects.create(
            nombre="Laptop",
            descripcion="Laptop de alta gama",
            precio_compra=1000.00,
            precio_venta=1200.00,
            unidad_medida="unidad",
            categoria=self.categoria,
            sucursal=self.sucursal,
            codigo_producto="LAP123",
            impuesto=self.impuesto
        )
        self.empleado = Empleado.objects.create(
            usuario=self.usuario,  # Asignar el usuario al empleado
            nombre="Empleado de Prueba"
        )

    def test_validar_cliente_factura(self):
        # Crear una factura sin cliente y llamar a `full_clean` explícitamente
        factura = Factura(
            sucursal=self.sucursal,
            cliente=None,  # Cliente faltante
            empleado=self.empleado,
            total_sin_impuestos=1200.00,
            total_con_impuestos=1344.00,
        )
        
        # Llamar a `full_clean` que debería lanzar ValidationError
        with self.assertRaises(ValidationError):
            factura.full_clean()  # Esto debería lanzar el ValidationError

    def test_registrar_pago(self):
        # Crear una factura y registrar un pago
        factura = Factura.objects.create(
            sucursal=self.sucursal,
            cliente=self.cliente,
            empleado=self.empleado,
            total_sin_impuestos=1200.00,
            total_con_impuestos=1344.00,
        )
        pago = Pago.objects.create(
            factura=factura,
            forma_pago="Efectivo",
            valor=1344.00
        )
        self.assertEqual(factura.pagos.count(), 1)
        self.assertEqual(pago.valor, 1344.00)
    