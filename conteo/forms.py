# conteo/forms.py
from django import forms
from .models import ConteoDiario

class ConteoDiarioForm(forms.ModelForm):
    class Meta:
        model = ConteoDiario
        fields = ['sucursal', 'producto', 'cantidad_contada']
