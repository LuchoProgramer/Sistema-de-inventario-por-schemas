from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.models import User


class RazonSocial(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    ruc = models.CharField(
        max_length=13,
        unique=True,
        validators=[
            RegexValidator(
                regex='^\d{13}$',
                message='El RUC debe tener exactamente 13 dígitos numéricos.'
            )
        ]
    )

    def __str__(self):
        return self.nombre


class Sucursal(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    razon_social = models.ForeignKey(RazonSocial, on_delete=models.CASCADE, related_name='sucursales')
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    codigo_establecimiento = models.CharField(max_length=3, blank=True, null=True)
    punto_emision = models.CharField(max_length=3, blank=True, null=True)
    es_matriz = models.BooleanField(default=False)
    secuencial_actual = models.CharField(max_length=9, default="000000001")  # Para manejar el secuencial de facturas
    usuarios = models.ManyToManyField(User, related_name='sucursales')

    class Meta:
        unique_together = ('codigo_establecimiento', 'punto_emision')  # Unicidad combinada

    def clean(self):
        # Validar que solo haya una sucursal marcada como matriz
        if self.es_matriz and Sucursal.objects.filter(es_matriz=True).exclude(pk=self.pk).exists():
            raise ValidationError('Ya existe una sucursal marcada como matriz. Solo una puede estar marcada como matriz.')

        # Validar que el RUC sea obligatorio si se especifican código de establecimiento o punto de emisión
        if not self.razon_social.ruc and (self.codigo_establecimiento or self.punto_emision):
            raise ValidationError('El RUC es obligatorio si se especifica código de establecimiento o punto de emisión.')

        # Validar que el RUC tiene exactamente 13 dígitos (si es proporcionado)
        if self.razon_social.ruc and len(self.razon_social.ruc) != 13:
            raise ValidationError('El RUC debe tener exactamente 13 dígitos.')

    def incrementar_secuencial(self):
        # Incrementa el secuencial en 1
        nuevo_secuencial = str(int(self.secuencial_actual) + 1).zfill(9)
        self.secuencial_actual = nuevo_secuencial
        self.save()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Sucursal, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre} - {self.codigo_establecimiento if self.codigo_establecimiento else "Sin código"}'
