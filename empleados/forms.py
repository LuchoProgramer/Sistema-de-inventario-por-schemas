# empleados/forms.py

from django import forms
from django.contrib.auth.models import User, Group
from .models import Empleado

class RegistroEmpleadoForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Nombre de Usuario')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    grupo = forms.ChoiceField(choices=[('Empleado', 'Empleado'), ('Administrador', 'Administrador')], label='Rol')

    class Meta:
        model = Empleado
        fields = ['nombre', 'sucursal']

    def save(self, commit=True):
        # Crear el usuario
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )

        # Crear el empleado
        empleado = Empleado(
            usuario=user,
            nombre=self.cleaned_data['nombre'],
            sucursal=self.cleaned_data['sucursal'],
        )

        # Asignar grupo
        grupo_name = self.cleaned_data['grupo']
        grupo = Group.objects.get(name=grupo_name)
        user.groups.add(grupo)

        if commit:
            user.save()
            empleado.save()

        return empleado
