from django.db import models
from django.contrib.auth.models import User
from sucursales.models import Sucursal

class Empleado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, unique=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre
