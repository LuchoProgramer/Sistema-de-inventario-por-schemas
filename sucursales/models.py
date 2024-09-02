from django.db import models
from django.core.exceptions import ValidationError

class Sucursal(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    razon_social = models.CharField(max_length=200, unique=True)
    ruc = models.CharField(max_length=13, unique=True, blank=True, null=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    codigo_establecimiento = models.CharField(max_length=3, unique=True, blank=True, null=True)
    punto_emision = models.CharField(max_length=3, unique=True, blank=True, null=True)
    es_matriz = models.BooleanField(default=False)

    def clean(self):
        if self.es_matriz and Sucursal.objects.filter(es_matriz=True).exclude(pk=self.pk).exists():
            raise ValidationError('Ya existe una sucursal marcada como matriz. Solo una puede estar marcada como matriz.')
        if not self.ruc and (self.codigo_establecimiento or self.punto_emision):
            raise ValidationError('El RUC es obligatorio si se especifica código de establecimiento o punto de emisión.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Sucursal, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre} - {self.codigo_establecimiento if self.codigo_establecimiento else "Sin código"}'
