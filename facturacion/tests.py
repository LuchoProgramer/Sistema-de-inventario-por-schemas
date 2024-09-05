# Importar la función desde utils/clave_acceso.py
from facturacion.utils.clave_acceso import generar_clave_acceso
from django.test import TestCase
from facturacion.models import Sucursal, Factura, Cliente
from datetime import datetime


class FacturaTestCase(TestCase):
    def setUp(self):
        # Crear una sucursal
        self.sucursal = Sucursal.objects.create(
            nombre="Sucursal Test",
            razon_social="Test Razon Social",
            ruc="0999999999001",
            direccion="Calle Test",
            telefono="0999999999",
            codigo_establecimiento="001",
            punto_emision="001",
            es_matriz=True
        )

        # Crear un cliente
        self.cliente = Cliente.objects.create(
            identificacion="1711234567",
            tipo_identificacion="05",
            razon_social="Cliente Test",
            direccion="Av. Test",
            telefono="0999999999",
            email="cliente@test.com"
        )

    def test_incrementar_secuencial(self):
        # Asegurar que el secuencial de la sucursal incrementa correctamente
        secuencial_inicial = self.sucursal.secuencial_actual
        self.sucursal.incrementar_secuencial()
        self.assertNotEqual(self.sucursal.secuencial_actual, secuencial_inicial)
        self.assertEqual(self.sucursal.secuencial_actual, "000000002")

    def test_clave_acceso_49_digitos(self):
        # Crear una factura
        factura = Factura.objects.create(
            sucursal=self.sucursal,
            cliente=self.cliente,
            empleado=None,
            total_sin_impuestos=100,
            total_con_impuestos=112,
            numero_autorizacion="000000001",
            clave_acceso=None,  # Esto se generará en algún proceso posterior
        )
        
        # Suponiendo que tienes un método para generar la clave de acceso
        clave_acceso = generar_clave_acceso(
            fecha_emision=datetime.now(),
            tipo_comprobante='01',
            ruc=self.sucursal.ruc,
            ambiente='1',
            estab=self.sucursal.codigo_establecimiento,
            pto_emi=self.sucursal.punto_emision,
            secuencial=factura.numero_autorizacion,
            tipo_emision='1'
        )
        # Asegurarse de que la clave tiene 49 dígitos
        self.assertEqual(len(clave_acceso), 49)
