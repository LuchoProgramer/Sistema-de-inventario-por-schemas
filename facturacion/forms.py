from django import forms
from .models import Impuesto
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo_identificacion', 'identificacion', 'razon_social', 'direccion', 'telefono', 'email']
        widgets = {
            'tipo_identificacion': forms.Select(attrs={'class': 'form-select'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class PagoMixtoForm(forms.Form):
    metodo_pago = forms.ChoiceField(
        choices=[('01', 'Sin utilización del sistema financiero'),
                 ('16', 'Tarjeta de débito'),
                 ('19', 'Tarjeta de crédito'),
                 ('20', 'Otros con utilización del sistema financiero')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    monto = forms.DecimalField(
        max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'})
    )



class ImpuestoForm(forms.ModelForm):
    class Meta:
        model = Impuesto
        fields = ['codigo_impuesto', 'nombre', 'porcentaje', 'activo']
