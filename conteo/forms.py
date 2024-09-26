from django import forms
from inventarios.models import Producto, Categoria

class ConteoProductoForm(forms.Form):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        empty_label="Todas las Categorías",
        label="Filtrar por Categoría",
        widget=forms.Select(attrs={'id': 'categoria-select'})
    )

    def __init__(self, *args, **kwargs):
        productos = kwargs.pop('productos')
        super(ConteoProductoForm, self).__init__(*args, **kwargs)
        self.productos = productos  # Guardamos los productos para usarlos en la validación
        for producto in productos:
            self.fields[f'producto_{producto.id}'] = forms.BooleanField(
                required=False,
                label=producto.nombre
            )
            self.fields[f'cantidad_{producto.id}'] = forms.IntegerField(
                required=False,
                min_value=0,
                widget=forms.NumberInput(attrs={'placeholder': 'Cantidad'})
            )

    def clean(self):
        cleaned_data = super().clean()

        # Validamos que si un producto está marcado, la cantidad debe estar presente y ser mayor que cero.
        for producto in self.productos:
            producto_marcado = cleaned_data.get(f'producto_{producto.id}')
            cantidad = cleaned_data.get(f'cantidad_{producto.id}')

            if producto_marcado and (cantidad is None or cantidad <= 0):
                self.add_error(f'cantidad_{producto.id}', f'Debes ingresar una cantidad válida para el producto {producto.nombre} marcado.')
            elif not producto_marcado and (cantidad is not None and cantidad > 0):
                self.add_error(f'producto_{producto.id}', 'Este producto no está marcado, no puedes asignar una cantidad.')

        return cleaned_data
