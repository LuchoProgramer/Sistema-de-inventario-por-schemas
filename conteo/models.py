from django.db import models
from django.core.exceptions import ValidationError

class ConteoDiario(models.Model):
    sucursal = models.ForeignKey('sucursales.Sucursal', on_delete=models.CASCADE)  # Relación como cadena de texto
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    fecha_conteo = models.DateField(auto_now_add=True)
    producto = models.ForeignKey('inventarios.Producto', on_delete=models.CASCADE)  # Si hay problema con Producto
    cantidad_contada = models.IntegerField()

    def __str__(self):
        return f"Conteo de {self.producto.nombre} en {self.sucursal.nombre} - {self.cantidad_contada} unidades"

    def clean(self):
        cleaned_data = super().clean()
        errors = {}

        # Validamos que todas las cantidades estén ingresadas y no sean negativas
        for producto in self.productos:
            field_name = f'cantidad_{producto.id}'
            cantidad = cleaned_data.get(field_name)

            if cantidad is None or cantidad == '':
                errors[field_name] = f'Debes ingresar una cantidad para {producto.nombre}.'
            elif cantidad < 0:
                errors[field_name] = f'La cantidad para {producto.nombre} no puede ser negativa.'

        if errors:
            for field, error in errors.items():
                self.add_error(field, error)

        return cleaned_data

