from django import forms
from .models import Sucursal, RazonSocial
from django.contrib.auth.models import User

class SucursalForm(forms.ModelForm):
    usuarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Sucursal
        fields = [
            'nombre', 'razon_social', 'direccion', 'telefono', 
            'codigo_establecimiento', 'punto_emision', 'es_matriz', 'usuarios'
        ]
        widgets = {
            'razon_social': forms.Select(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_establecimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'punto_emision': forms.TextInput(attrs={'class': 'form-control'}),
            'es_matriz': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RazonSocialForm(forms.ModelForm):
    class Meta:
        model = RazonSocial
        fields = ['nombre', 'ruc']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ruc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el RUC'}),
        }