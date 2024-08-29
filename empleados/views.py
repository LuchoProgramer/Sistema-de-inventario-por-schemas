from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import RegistroEmpleadoForm
from django.contrib.auth.decorators import login_required

def es_administrador(user):
    return user.groups.filter(name='Administrador').exists()

#Registrar Empleado
@user_passes_test(es_administrador, login_url='login')
def registrar_empleado(request):
    if request.method == 'POST':
        form = RegistroEmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuario_creado_exitosamente')
    else:
        form = RegistroEmpleadoForm()
    return render(request, 'empleados/registro.html', {'form': form})

#Dashboard
@login_required
def dashboard(request):
    return render(request, 'empleados/dashboard.html')


#Usuario creado exitosamente
@login_required
def usuario_creado_exitosamente(request):
    return render(request, 'empleados/usuario_creado_exitosamente.html')