from django import forms
from .models import Sucursal
from django.contrib.auth.models import User

class SucursalForm(forms.ModelForm):
    usuarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Puedes cambiar el widget si prefieres un dropdown
        required=False  # Esto es opcional, si deseas permitir sucursales sin usuarios asignados
    )

    class Meta:
        model = Sucursal
        fields = ['nombre', 'razon_social', 'ruc', 'direccion', 'telefono', 'codigo_establecimiento', 'punto_emision', 'es_matriz', 'usuarios']
