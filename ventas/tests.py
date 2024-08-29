from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from ventas.models import Venta, CierreCaja
from empleados.models import Empleado
from sucursales.models import Sucursal
from inventarios.models import Producto, Categoria, Inventario  # Asegúrate de importar Inventario

class CierreCajaTestCase(TestCase):

    def setUp(self):
        # Crear una sucursal
        self.sucursal = Sucursal.objects.create(
            nombre="Sucursal 1",
            direccion="Calle Falsa 123",
            telefono="1234567890"
        )
        
        # Crear una categoría de producto
        self.categoria = Categoria.objects.create(nombre="Categoría de Prueba")
        
        # Crear un producto de prueba
        self.producto = Producto.objects.create(
            nombre="Producto de Prueba",
            descripcion="Descripción del producto de prueba",
            precio_compra=5.00,
            precio_venta=10.00,
            unidad_medida="Unidad",
            categoria=self.categoria,
            sucursal=self.sucursal
        )
        
        # Crear un inventario para el producto y la sucursal
        self.inventario = Inventario.objects.create(
            sucursal=self.sucursal,
            producto=self.producto,
            cantidad=100  # Cantidad inicial en inventario
        )
        
        # Crear un usuario
        self.usuario = User.objects.create_user(username="Empleado1", password="password123")
        
        # Crear un empleado asociado al usuario
        self.empleado = Empleado.objects.create(
            usuario=self.usuario,
            nombre="Empleado1",
            sucursal=self.sucursal,
            grupo="Empleado"
        )
        
        # Crear ventas de ejemplo usando el producto
        Venta.objects.create(
            sucursal=self.sucursal,
            empleado=self.usuario,  # Asignar User aquí
            producto=self.producto,  # Asignar el Producto aquí
            metodo_pago="Efectivo",
            total_venta=100.00,  # Este puede ser calculado automáticamente
            cantidad=10,  # Asigna un valor válido para la cantidad
            precio_unitario=10.00,  # Asigna un valor válido para el precio unitario
            fecha=timezone.now()
        )
        Venta.objects.create(
            sucursal=self.sucursal,
            empleado=self.usuario,  # Asignar User aquí
            producto=self.producto,  # Asignar el Producto aquí
            metodo_pago="Tarjeta",
            total_venta=50.00,  # Este puede ser calculado automáticamente
            cantidad=5,  # Asigna un valor válido para la cantidad
            precio_unitario=10.00,  # Asigna un valor válido para el precio unitario
            fecha=timezone.now()
        )
        
        # Crear un cierre de caja con montos coincidentes
        self.cierre_caja = CierreCaja.objects.create(
            sucursal=self.sucursal,
            empleado=self.usuario,  # Cambiar self.empleado a self.usuario
            efectivo_total=100.00,
            tarjeta_total=50.00,
            transferencia_total=0.00
        )

    def test_verificar_montos_incorrectos(self):
        # Modificar el cierre de caja para simular una discrepancia
        self.cierre_caja.efectivo_total = 120.00
        resultado = self.cierre_caja.verificar_montos()

        # Asegurarse de que el resultado incluya la discrepancia, ignorando el formato exacto
        esperado = "Discrepancia en efectivo"
        self.assertTrue(any(esperado in mensaje for mensaje in resultado))
