from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from ventas.models import Venta, NotaVenta, CierreCaja

class Command(BaseCommand):
    help = 'Configura los grupos y asigna los permisos correspondientes'

    def handle(self, *args, **kwargs):
        # Crear grupos
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        empleado_group, created = Group.objects.get_or_create(name='Empleado')

        # Obtener los permisos para cada modelo
        permisos_venta = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Venta))
        permisos_notaventa = Permission.objects.filter(content_type=ContentType.objects.get_for_model(NotaVenta))
        permisos_cierrecaja = Permission.objects.filter(content_type=ContentType.objects.get_for_model(CierreCaja))

        # Asignar permisos al grupo Administrador (acceso completo)
        admin_group.permissions.set(list(permisos_venta) + list(permisos_notaventa) + list(permisos_cierrecaja))

        # Asignar permisos al grupo Empleado (acceso restringido)
        empleado_permisos = Permission.objects.filter(codename__in=[
            'add_venta', 'view_venta',
            'view_notaventa',
            'add_cierrecaja', 'view_cierrecaja'
        ])
        empleado_group.permissions.set(empleado_permisos)

        self.stdout.write(self.style.SUCCESS('Grupos y permisos configurados correctamente.'))
