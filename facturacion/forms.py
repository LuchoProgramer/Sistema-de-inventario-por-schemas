from django import forms
from .models import Impuesto

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
