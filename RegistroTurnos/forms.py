from django import forms
from django.contrib.auth.models import User, Group
from .models import RegistroTurno
from sucursales.models import Sucursal


class RegistroTurnoForm(forms.ModelForm):
    class Meta:
        model = RegistroTurno
        fields = ['sucursal']

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario:
            sucursales = Sucursal.objects.filter(usuarios__id=usuario.id)
            if not sucursales.exists():
                # Si el usuario no tiene sucursales asociadas, mostrar un error
                self.fields['sucursal'].queryset = Sucursal.objects.none()
                self.fields['sucursal'].widget.attrs['disabled'] = 'disabled'
                self.fields['sucursal'].help_text = 'No tienes sucursales asignadas.'
            else:
                # Filtrar las sucursales a las que el usuario tiene acceso
                self.fields['sucursal'].queryset = sucursales

