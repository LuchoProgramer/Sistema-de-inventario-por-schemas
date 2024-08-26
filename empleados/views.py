# empleados/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import RegistroEmpleadoForm

def es_administrador(user):
    return user.groups.filter(name='Administrador').exists()

@user_passes_test(es_administrador, login_url='login')
def registrar_empleado(request):
    if request.method == 'POST':
        form = RegistroEmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirigir al login después de registrarse
    else:
        form = RegistroEmpleadoForm()
    return render(request, 'empleados/registro.html', {'form': form})
