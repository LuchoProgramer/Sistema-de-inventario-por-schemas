from django.db import models, transaction
from django.contrib.auth.models import User, Group
from sucursales.models import Sucursal
from django.utils import timezone
from django.core.exceptions import ValidationError


class Empleado(models.Model):
    GRUPOS_OPCIONES = [
        ('Empleado', 'Empleado'),
        ('Administrador', 'Administrador'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, unique=True)
    sucursales = models.ManyToManyField(Sucursal, blank=True)  # Relación muchos a muchos
    grupo = models.CharField(max_length=20, choices=GRUPOS_OPCIONES, default='Empleado')

    def __str__(self):
        return self.nombre

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Validar los datos antes de guardar
        self.full_clean()

        # Asignar al grupo seleccionado
        grupo, created = Group.objects.get_or_create(name=self.grupo)
        if not self.usuario.groups.filter(name=self.grupo).exists():
            self.usuario.groups.add(grupo)
        
        super(Empleado, self).save(*args, **kwargs)



class RegistroTurno(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE)
    inicio_turno = models.DateTimeField()
    fin_turno = models.DateTimeField(null=True, blank=True)
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    otros_metodos_pago = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def cerrar_turno(self, efectivo_total, tarjeta_total, transferencia_total, salidas_caja):
        from ventas.models import CierreCaja

        # Verificar si el turno ya ha sido cerrado
        if self.fin_turno:
            raise ValidationError("Este turno ya está cerrado.")

        # Actualizar los totales y cerrar el turno
        self.fin_turno = timezone.now()
        self.total_efectivo = efectivo_total
        self.otros_metodos_pago = tarjeta_total + transferencia_total
        self.save()

        # Crear el registro de cierre de caja
        CierreCaja.objects.create(
            empleado=self.empleado.usuario,
            sucursal=self.sucursal,
            efectivo_total=efectivo_total,
            tarjeta_total=tarjeta_total,
            transferencia_total=transferencia_total,
            salidas_caja=salidas_caja,
            fecha_cierre=self.fin_turno
        )

    @classmethod
    def turno_activo(cls, empleado):
        """
        Verifica si el empleado tiene un turno activo (es decir, sin fin_turno).
        """
        return cls.objects.filter(empleado=empleado, fin_turno__isnull=True).first()

    def clean(self):
        # Validar que el fin del turno sea posterior al inicio
        if self.fin_turno and self.fin_turno <= self.inicio_turno:
            raise ValidationError('El fin del turno debe ser posterior al inicio.')
        super(RegistroTurno, self).clean()

    def __str__(self):
        return f"Turno de {self.empleado.nombre} en {self.sucursal.nombre} - Inicio: {self.inicio_turno}"