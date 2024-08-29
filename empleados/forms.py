# empleados/forms.py

from django import forms
from django.contrib.auth.models import User, Group
from .models import Empleado
from sucursales.models import Sucursal

class RegistroEmpleadoForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Nombre de Usuario')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    grupo = forms.ChoiceField(choices=[('Empleado', 'Empleado'), ('Administrador', 'Administrador')], label='Rol')
    sucursales = forms.ModelMultipleChoiceField(queryset=Sucursal.objects.all(), label='Sucursales')  # Cambiado a ModelMultipleChoiceField

    class Meta:
        model = Empleado
        fields = ['nombre', 'sucursales']

    def save(self, commit=True):
        # Crear el usuario
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )

        # Crear el empleado sin guardar aún (commit=False)
        empleado = Empleado(
            usuario=user,
            nombre=self.cleaned_data['nombre'],
        )

        # Asignar grupo
        grupo_name = self.cleaned_data['grupo']
        grupo = Group.objects.get(name=grupo_name)
        user.groups.add(grupo)

        if commit:
            user.save()
            empleado.save()
            # Asignar las sucursales seleccionadas
            empleado.sucursales.set(self.cleaned_data['sucursales'])
            empleado.save()

        return empleado
