# forms.py

from django import forms
from .models import Producto
from inventarios.models import Inventario, Presentacion
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
    producto = forms.ModelChoiceField(queryset=Producto.objects.none(), label="Producto", empty_label="Seleccione un producto")
    presentacion = forms.ModelChoiceField(queryset=Presentacion.objects.none(), label="Presentación", empty_label="Seleccione una presentación")  # Nuevo campo
    cantidad = forms.IntegerField(min_value=1, label="Cantidad")
    
    def __init__(self, *args, **kwargs):
        sucursal_id = kwargs.pop('sucursal_id', None)
        self.sucursal_id = sucursal_id
        super().__init__(*args, **kwargs)
        if sucursal_id:
            productos_disponibles = Producto.objects.filter(inventario__sucursal_id=sucursal_id)
            if not productos_disponibles.exists():
                self.fields['producto'].empty_label = "No hay productos disponibles"
            self.fields['producto'].queryset = productos_disponibles

        # Si hay un producto seleccionado, cargamos las presentaciones correspondientes
        if 'producto' in self.data:
            try:
                producto_id = int(self.data.get('producto'))
                self.fields['presentacion'].queryset = Presentacion.objects.filter(producto_id=producto_id)
            except (ValueError, TypeError):
                self.fields['presentacion'].queryset = Presentacion.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get("producto")
        presentacion = cleaned_data.get("presentacion")
        cantidad = cleaned_data.get("cantidad")
        sucursal_id = self.initial.get('sucursal_id')

        if producto and presentacion and sucursal_id and cantidad:
            try:
                inventario = producto.inventario_set.get(sucursal_id=sucursal_id)
                total_unidades = presentacion.cantidad * cantidad  # Calculamos la cantidad total de unidades según la presentación
                if total_unidades > inventario.cantidad:
                    raise forms.ValidationError(f"No hay suficiente stock. Disponible: {inventario.cantidad} unidades.")
            except Inventario.DoesNotExist:
                raise forms.ValidationError("No hay inventario disponible para este producto en la sucursal seleccionada.")
            except Exception as e:
                raise forms.ValidationError(f"Error al verificar el inventario: {str(e)}")



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

