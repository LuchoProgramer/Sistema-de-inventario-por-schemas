from django import forms
from .models import Sucursal
from django.contrib.auth.models import User

class SucursalForm(forms.ModelForm):
    usuarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Sucursal
        fields = ['nombre', 'razon_social', 'ruc', 'direccion', 'telefono', 'codigo_establecimiento', 'punto_emision', 'es_matriz', 'usuarios']
        widgets = {
            # Añadimos el id 'sucursal_id' al campo sucursal para que coincida con el label
            'sucursal': forms.Select(attrs={'id': 'sucursal_id', 'class': 'form-control'}),
        }