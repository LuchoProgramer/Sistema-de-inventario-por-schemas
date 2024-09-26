from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from RegistroTurnos.models import RegistroTurno
from sucursales.models import Sucursal

class TurnoTest(TestCase):
    def setUp(self):
        # Crear un usuario
        self.usuario = User.objects.create(username='testuser', password='testpassword')

        # Crear una sucursal
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

    def test_iniciar_turno(self):
        # Verificar que no hay un turno activo antes de iniciar
        turno_activo = RegistroTurno.objects.filter(usuario=self.usuario, fin_turno__isnull=True).exists()
        self.assertFalse(turno_activo)

        # Iniciar turno
        turno = RegistroTurno.objects.create(
            usuario=self.usuario,  # Cambiado a usuario
            sucursal=self.sucursal,
            inicio_turno=timezone.now()
        )

        # Verificar que ahora sí hay un turno activo
        turno_activo = RegistroTurno.objects.filter(usuario=self.usuario, fin_turno__isnull=True).exists()
        self.assertTrue(turno_activo)
        self.assertEqual(turno.usuario, self.usuario)
        self.assertEqual(turno.sucursal, self.sucursal)


class CierreTurnoTest(TestCase):
    def setUp(self):
        # Crear un usuario
        self.usuario = User.objects.create(username='testuser', password='testpassword')

        # Crear una sucursal
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

        # Iniciar un turno
        self.turno = RegistroTurno.objects.create(
            usuario=self.usuario,  # Cambiado a usuario
            sucursal=self.sucursal,
            inicio_turno=timezone.now()
        )

    def test_cerrar_turno(self):
        # Verificar que el turno no tiene fin_turno al inicio
        self.assertIsNone(self.turno.fin_turno)

        # Cerrar el turno
        self.turno.fin_turno = timezone.now()
        self.turno.save()

        # Verificar que ahora el turno tiene una fecha de fin
        turno_cerrado = RegistroTurno.objects.get(id=self.turno.id)
        self.assertIsNotNone(turno_cerrado.fin_turno)
        self.assertEqual(turno_cerrado.usuario, self.usuario)
