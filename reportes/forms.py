from django import forms
from sucursales.models import Sucursal
from django.contrib.auth.models import User
from RegistroTurnos.models import RegistroTurno  # Cambiado de Turno a RegistroTurno

class FiltroReporteVentasForm(forms.Form):
    sucursal = forms.ModelChoiceField(queryset=Sucursal.objects.all(), required=False)
    fecha_inicio = forms.DateField(widget=forms.SelectDateWidget(), required=False)
    fecha_fin = forms.DateField(widget=forms.SelectDateWidget(), required=False)
    usuario = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    turno = forms.ModelChoiceField(queryset=RegistroTurno.objects.all(), required=False)  # Utilizar RegistroTurno
