from django import forms
from RegistroTurnos.models import RegistroTurno
from sucursales.models import Sucursal

class RegistroTurnoForm(forms.ModelForm):
    class Meta:
        model = RegistroTurno
        fields = ['sucursal']  # Solo incluir la sucursal

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)  # Extraer el usuario de kwargs
        super().__init__(*args, **kwargs)
        if usuario:
            # Filtrar las sucursales asignadas al usuario
            self.fields['sucursal'].queryset = Sucursal.objects.filter(usuarios=usuario)
