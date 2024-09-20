from django.test import TestCase
from django.contrib.auth.models import User
from inventarios.models import Producto, Categoria
from .models import ConteoDiario
from .forms import ConteoProductoForm
from django.core.exceptions import ValidationError

class ConteoDiarioModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.producto = Producto.objects.create(nombre="Producto Test", precio_compra=10, precio_venta=20)
        self.conteo = ConteoDiario.objects.create(
            sucursal="Sucursal Test",
            usuario=self.user,  # Cambiado de empleado a usuario
            producto=self.producto,
            cantidad_contada=100
        )

    def test_conteo_diario_creation(self):
        self.assertEqual(self.conteo.cantidad_contada, 100)
        self.assertEqual(self.conteo.__str__(), "Conteo de Producto Test en Sucursal Test - 100 unidades")

    def test_conteo_diario_invalid(self):
        conteo = ConteoDiario(
            sucursal="",
            usuario=self.user,  # Cambiado de empleado a usuario
            producto=self.producto,
            cantidad_contada=-10  # Cantidad inválida
        )
        with self.assertRaises(ValidationError):
            conteo.full_clean()  # Ejecuta las validaciones que lanzan ValidationError

class ConteoProductoFormTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Categoria Test")
        self.producto = Producto.objects.create(nombre="Producto Test", categoria=self.categoria, precio_compra=10, precio_venta=20)
        self.form = ConteoProductoForm(productos=[self.producto])

    def test_form_initialization(self):
        self.assertIn(f'producto_{self.producto.id}', self.form.fields)
        self.assertIn(f'cantidad_{self.producto.id}', self.form.fields)

    def test_form_validation(self):
        form_data = {
            f'producto_{self.producto.id}': True,
            f'cantidad_{self.producto.id}': 5,
        }
        form = ConteoProductoForm(data=form_data, productos=[self.producto])
        self.assertTrue(form.is_valid())

