from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import RegistroEmpleadoForm, RegistroTurnoForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Empleado
from sucursales.models import Sucursal
from django.utils import timezone

def es_administrador(user):
    return user.groups.filter(name='Administrador').exists()

#Registrar Empleado
#@user_passes_test(es_administrador, login_url='login')
def registrar_empleado(request):
    if request.method == 'POST':
        form = RegistroEmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuario_creado_exitosamente')
    else:
        form = RegistroEmpleadoForm()
    return render(request, 'empleados/registro.html', {'form': form})


#Usuario creado exitosamente
@login_required
def usuario_creado_exitosamente(request):
    return render(request, 'empleados/usuario_creado_exitosamente.html')

#Dashboard
@login_required
def dashboard(request):
    try:
        empleado = Empleado.objects.get(usuario=request.user)
    except Empleado.DoesNotExist:
        return render(request, 'empleados/no_es_empleado.html')

    if request.method == 'POST':
        form = RegistroTurnoForm(request.POST, empleado=empleado)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.empleado = empleado
            turno.inicio_turno = timezone.now()
            turno.save()
            request.session['sucursal_seleccionada'] = turno.sucursal.id
            return redirect('ventas:inicio_turno')
    else:
        form = RegistroTurnoForm(empleado=empleado)

    return render(request, 'empleados/dashboard.html', {'form': form})
