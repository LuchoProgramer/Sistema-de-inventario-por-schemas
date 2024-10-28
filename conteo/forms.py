from django import forms
from inventarios.models import Producto, Categoria

class ConteoProductoForm(forms.Form):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        empty_label="Todas las Categorías",
        label="Filtrar por Categoría",
        widget=forms.Select(attrs={
            'id': 'categoria-select',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        productos = kwargs.pop('productos')
        super().__init__(*args, **kwargs)
        self.productos = productos  # Guardamos los productos para usarlos en la validación

        for producto in productos:
            field_name = f'cantidad_{producto.id}'
            self.fields[field_name] = forms.IntegerField(
                required=False,
                min_value=0,
                label=producto.nombre,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Cantidad',
                    'type': 'number',
                    'min': '0'
                })
            )

    def clean(self):
        cleaned_data = super().clean()

        # Validamos que las cantidades no sean negativas
        for producto in self.productos:
            field_name = f'cantidad_{producto.id}'
            cantidad = cleaned_data.get(field_name)

            if cantidad is not None:
                if cantidad < 0:
                    self.add_error(field_name, f'La cantidad para {producto.nombre} no puede ser negativa.')

        return cleaned_data
