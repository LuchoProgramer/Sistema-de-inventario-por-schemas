from django.test import TestCase
from inventarios.models import Producto, Categoria, Sucursal
from facturacion.models import Impuesto
from django.core.exceptions import ValidationError

class ProductoModelTest(TestCase):

    def setUp(self):
        # Crear una categoría, sucursal e impuesto para los productos
        self.categoria = Categoria.objects.create(nombre="Electrónica")
        self.sucursal = Sucursal.objects.create(
            nombre="Sucursal Central", 
            razon_social="Empresa Central S.A.",
            telefono="0999999999",
            direccion="Av. Principal 123"
        )
        self.impuesto = Impuesto.objects.create(nombre="IVA", porcentaje=12, monto=0)

    def test_crear_producto(self):
        # Crear un producto y verificar que se guarda correctamente
        producto = Producto.objects.create(
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
        self.assertEqual(producto.nombre, "Laptop")
        self.assertEqual(producto.calcular_margen(), 200.00)
        self.assertAlmostEqual(producto.calcular_precio_final(), 1200.00 * 1.12, places=2)

    def test_producto_con_precio_venta_menor_a_precio_compra(self):
        # Intentar crear un producto con precio de venta menor al precio de compra debería lanzar un ValidationError
        with self.assertRaises(ValidationError):
            producto = Producto(
                nombre="Tablet",
                descripcion="Tablet de última generación",
                precio_compra=1000.00,
                precio_venta=900.00,
                unidad_medida="unidad",
                categoria=self.categoria,
                sucursal=self.sucursal,
                codigo_producto="TAB123",
                impuesto=self.impuesto
            )
            producto.clean()  # Esto debería lanzar el ValidationError

    def test_calculo_precio_final_sin_impuesto(self):
        # Crear un producto sin impuesto y verificar que el precio final es igual al precio de venta
        producto = Producto.objects.create(
            nombre="Smartphone",
            descripcion="Smartphone con pantalla OLED",
            precio_compra=500.00,
            precio_venta=700.00,
            unidad_medida="unidad",
            categoria=self.categoria,
            sucursal=self.sucursal,
            codigo_producto="PHN123"
        )
        self.assertAlmostEqual(producto.calcular_precio_final(), 700.00, places=2)

    def test_producto_sin_codigo(self):
        # Verificar que un producto sin código puede ser creado
        producto = Producto.objects.create(
            nombre="Mouse",
            descripcion="Mouse inalámbrico",
            precio_compra=20.00,
            precio_venta=30.00,
            unidad_medida="unidad",
            categoria=self.categoria,
            sucursal=self.sucursal
        )
        self.assertIsNone(producto.codigo_producto)
        self.assertAlmostEqual(producto.calcular_precio_final(), 30.00, places=2)
