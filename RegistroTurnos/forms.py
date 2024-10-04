from django import forms
from RegistroTurnos.models import RegistroTurno
from sucursales.models import Sucursal
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

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


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido. Introduce una dirección de correo electrónico válida.")
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False, help_text="Selecciona los grupos para este usuario.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "groups")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            user.groups.set(self.cleaned_data["groups"])  # Asignar los grupos seleccionados al usuario
        return user