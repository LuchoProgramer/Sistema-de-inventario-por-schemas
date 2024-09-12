from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import RegistroEmpleadoForm, RegistroTurnoForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Empleado
from empleados.models import RegistroTurno
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
        # Verificar si el usuario es un empleado
        empleado = Empleado.objects.get(usuario=request.user)
    except Empleado.DoesNotExist:
        return redirect('home')

    # Verificar si el empleado ya tiene un turno activo
    turno_activo = RegistroTurno.objects.filter(empleado=empleado, fin_turno__isnull=True).first()

    if turno_activo:
        # Redirigir al inicio del turno, pasando el turno_id del turno activo
        return redirect('ventas:inicio_turno', turno_id=turno_activo.id)

    # Si no hay turno activo, permitir iniciar uno nuevo
    if request.method == 'POST':
        form = RegistroTurnoForm(request.POST, empleado=empleado)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.empleado = empleado
            turno.inicio_turno = timezone.now()
            turno.save()

            # Guardar la sucursal seleccionada en la sesión
            request.session['sucursal_seleccionada'] = turno.sucursal.id

            # Redirigir al inicio del turno con el turno_id recién creado
            return redirect('ventas:inicio_turno', turno_id=turno.id)
    else:
        form = RegistroTurnoForm(empleado=empleado)

    return render(request, 'empleados/dashboard.html', {'form': form})
