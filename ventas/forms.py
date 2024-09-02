# forms.py

from django import forms
from .models import Producto
from inventarios.models import Inventario

class SeleccionVentaForm(forms.Form):
    producto = forms.ModelChoiceField(queryset=Producto.objects.none(), label="Producto")
    cantidad = forms.IntegerField(min_value=1, label="Cantidad")
    
    def __init__(self, *args, **kwargs):
        sucursal_id = kwargs.pop('sucursal_id', None)
        super().__init__(*args, **kwargs)
        if sucursal_id:
            self.fields['producto'].queryset = Producto.objects.filter(inventario__sucursal_id=sucursal_id)
    
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get("producto")
        cantidad = cleaned_data.get("cantidad")
        sucursal_id = self.initial.get('sucursal_id')

        if producto and sucursal_id and cantidad:
            try:
                inventario = producto.inventario_set.get(sucursal_id=sucursal_id)
                if cantidad > inventario.cantidad:
                    raise forms.ValidationError(f"No hay suficiente stock. Disponible: {inventario.cantidad} unidades.")
            except Inventario.DoesNotExist:
                raise forms.ValidationError("No hay inventario disponible para este producto en la sucursal seleccionada.")
