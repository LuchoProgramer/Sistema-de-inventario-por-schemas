from django.test import TestCase
from inventarios.models import Categoria, Producto, Inventario, Compra
from sucursales.models import Sucursal

class CategoriaTestCase(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Electrónica")

    def test_creacion_categoria(self):
        self.assertEqual(str(self.categoria), "Electrónica")
        self.assertTrue(Categoria.objects.filter(nombre="Electrónica").exists())

class ProductoTestCase(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Electrónica")
        self.sucursal = Sucursal.objects.create(
            nombre="Sucursal Centro", 
            direccion="Calle Principal 123", 
            telefono="123456789"
        )
        self.producto = Producto.objects.create(
            nombre="Laptop",
            descripcion="Laptop de alta gama",
            precio_compra=1000.00,
            precio_venta=1200.00,
            unidad_medida="Unidad",
            categoria=self.categoria,
            sucursal=self.sucursal
        )

    def test_creacion_producto(self):
        self.assertEqual(str(self.producto), "Laptop")
        self.assertEqual(self.producto.calcular_margen(), 200.00)

class InventarioTestCase(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Electrónica")
        self.sucursal = Sucursal.objects.create(
            nombre="Sucursal Centro", 
            direccion="Calle Principal 123", 
            telefono="123456789"
        )
        self.producto = Producto.objects.create(
            nombre="Laptop",
            descripcion="Laptop de alta gama",
            precio_compra=1000.00,
            precio_venta=1200.00,
            unidad_medida="Unidad",
            categoria=self.categoria,
            sucursal=self.sucursal
        )
        self.inventario = Inventario.objects.create(producto=self.producto, sucursal=self.sucursal, cantidad=50)

    def test_creacion_inventario(self):
        self.assertEqual(str(self.inventario), "Laptop - 50 unidades en Sucursal Centro")
        self.assertEqual(self.inventario.cantidad, 50)

class CompraTestCase(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Electrónica")
        self.sucursal = Sucursal.objects.create(
            nombre="Sucursal Centro", 
            direccion="Calle Principal 123", 
            telefono="123456789", 
            es_matriz=True
        )
        self.producto = Producto.objects.create(
            nombre="Laptop",
            descripcion="Laptop de alta gama",
            precio_compra=1000.00,
            precio_venta=1200.00,
            unidad_medida="Unidad",
            categoria=self.categoria,
            sucursal=self.sucursal
        )
        self.compra = Compra.objects.create(sucursal=self.sucursal, producto=self.producto, cantidad=10)

    def test_creacion_compra(self):
        self.assertEqual(self.compra.cantidad, 10)
        inventario = Inventario.objects.get(producto=self.producto, sucursal=self.sucursal)
        self.assertEqual(inventario.cantidad, 10)
