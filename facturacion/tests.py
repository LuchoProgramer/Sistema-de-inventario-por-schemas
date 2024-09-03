from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from facturacion.models import Cliente, Factura, Sucursal, Empleado
from ventas.models import RegistroTurno, Carrito
from inventarios.models import Producto, Inventario

class GenerarFacturaViewTestCase(TestCase):
    def setUp(self):
        # Crear usuario y empleado
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.sucursal = Sucursal.objects.create(
            nombre="Sucursal de prueba",
            razon_social="Razón Social de prueba",
            ruc="1234567890123",
            direccion="Calle de prueba",
            telefono="0999999999",
            codigo_establecimiento="001",
            punto_emision="001"
        )
        self.empleado = Empleado.objects.create(usuario=self.user, nombre="Empleado de prueba")
        self.empleado.sucursales.add(self.sucursal)

        # Crear turno activo
        self.turno = RegistroTurno.objects.create(
            empleado=self.empleado,
            sucursal=self.sucursal,
            inicio_turno="2024-09-02 09:00:00"
        )

        # Crear cliente
        self.cliente = Cliente.objects.create(
            identificacion="9999999999",
            tipo_identificacion="07",
            razon_social="Consumidor Final",
            direccion="",
            telefono="",
            email=""
        )

        # Crear producto y asociar con inventario
        self.producto = Producto.objects.create(
            nombre="Producto de prueba",
            precio_venta=10.00,
            precio_compra=5.00  # Asegúrate de proporcionar el precio de compra también
        )

        # Crear inventario
        self.inventario = Inventario.objects.create(
            sucursal=self.sucursal,
            producto=self.producto,
            cantidad=100  # Especifica una cantidad en stock
        )

        # Iniciar sesión del usuario
        self.client.login(username='testuser', password='12345')

    def test_generar_factura(self):
        # Agregar producto al carrito
        Carrito.objects.create(turno=self.turno, producto=self.producto, cantidad=1)

        # Datos para la solicitud POST
        post_data = {
            'cliente_id': self.cliente.id,
        }

        # Llamar a la vista de generar factura
        response = self.client.post(reverse('facturacion:generar_factura'), post_data)

        # Verificar que la factura se creó
        facturas = Factura.objects.all()
        self.assertEqual(facturas.count(), 1)
        factura = facturas.first()
        self.assertEqual(factura.sucursal, self.sucursal)
        self.assertEqual(factura.cliente, self.cliente)
        self.assertEqual(factura.empleado, self.empleado)

        # Verificar código de establecimiento y punto de emisión
        self.assertEqual(factura.sucursal.codigo_establecimiento, "001")
        self.assertEqual(factura.sucursal.punto_emision, "001")

        # Verificar que la respuesta redirige a la página de éxito
        self.assertRedirects(response, reverse('facturacion:factura_exitosa'))
