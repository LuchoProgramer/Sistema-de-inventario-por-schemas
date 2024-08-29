from django.db import models, transaction
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from sucursales.models import Sucursal

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

    class Meta:
        pass
