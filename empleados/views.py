from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import RegistroEmpleadoForm, RegistroTurnoForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Empleado
from empleados.models import RegistroTurno
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse


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

# Dashboard: Esta vista maneja la lógica de iniciar turno
def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

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
        # Si hay un turno activo, redirigir o devolver una respuesta JSON si es una solicitud AJAX
        if is_ajax(request):
            return JsonResponse({'success': True, 'turno_id': turno_activo.id})
        return redirect('ventas:inicio_turno', turno_id=turno_activo.id)

    # Si no hay turno activo, permitir iniciar uno nuevo
    if request.method == 'POST':
        form = RegistroTurnoForm(request.POST, empleado=empleado)
        if form.is_valid():
            try:
                turno = form.save(commit=False)
                turno.empleado = empleado
                turno.inicio_turno = timezone.now()
                turno.save()

                # Guardar la sucursal seleccionada en la sesión
                request.session['sucursal_seleccionada'] = turno.sucursal.id

                # Responder con JSON si es una solicitud AJAX
                if is_ajax(request):
                    return JsonResponse({'success': True, 'turno_id': turno.id})

                # Redirigir al inicio del turno con el turno_id recién creado
                return redirect('ventas:inicio_turno', turno_id=turno.id)
            except Exception as e:
                # Manejar cualquier error durante la creación del turno
                if is_ajax(request):
                    return JsonResponse({'success': False, 'message': f"Error: {str(e)}"})
                messages.error(request, f"Error al iniciar el turno: {e}")
        else:
            if is_ajax(request):
                return JsonResponse({'success': False, 'message': 'Formulario no válido.'})
            messages.error(request, "Formulario no válido. Por favor, corrige los errores.")
    else:
        form = RegistroTurnoForm(empleado=empleado)

    return render(request, 'empleados/dashboard.html', {'form': form})