# forms.py

from django import forms
from .models import Producto
from inventarios.models import Inventario
from .models import CierreCaja

class CierreCajaForm(forms.ModelForm):
    class Meta:
        model = CierreCaja
        fields = ['efectivo_total', 'tarjeta_total', 'transferencia_total', 'salidas_caja']

        widgets = {
            'efectivo_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'tarjeta_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'transferencia_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'salidas_caja': forms.NumberInput(attrs={'class': 'form-control'}),
        }

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

class MetodoPagoForm(forms.Form):
    METODOS_PAGO_SRI = [
        ('01', 'Sin utilización del sistema financiero'),
        ('15', 'Compensación de deudas'),
        ('16', 'Tarjeta de débito'),
        ('17', 'Dinero electrónico'),
        ('18', 'Tarjeta prepago'),
        ('19', 'Tarjeta de crédito'),
        ('20', 'Otros con utilización del sistema financiero'),
        ('21', 'Endoso de títulos'),
    ]
    metodo_pago = forms.ChoiceField(choices=METODOS_PAGO_SRI, label="Método de Pago")