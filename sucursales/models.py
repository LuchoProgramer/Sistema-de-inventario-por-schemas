from django.db import models
from django.core.exceptions import ValidationError

class Sucursal(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    es_matriz = models.BooleanField(default=False)  # Indica si la sucursal es la matriz

    def clean(self):
        # Verifica si hay otra sucursal marcada como matriz
        if self.es_matriz and Sucursal.objects.filter(es_matriz=True).exists() and not self.pk:
            raise ValidationError('Ya existe una sucursal marcada como matriz. Solo una puede estar marcada como matriz.')

    def save(self, *args, **kwargs):
        # Llama al método clean para validar antes de guardar
        self.full_clean()  # Esto ejecuta el método clean automáticamente
        super(Sucursal, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre
