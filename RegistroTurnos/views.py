from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from RegistroTurnos.models import RegistroTurno
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test
from .forms import RegistroTurnoForm  # Descomentado para usar el formulario
from django.core.exceptions import ValidationError
from .helpers import asignar_turno
from sucursales.models import Sucursal
import traceback 


# Verificar si la solicitud es AJAX
def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

from django.http import JsonResponse

@login_required
def dashboard(request):
    usuario = request.user

    # Verificar si el usuario ya tiene un turno activo
    turno_activo = RegistroTurno.objects.filter(usuario=usuario, fin_turno__isnull=True).first()

    if turno_activo:
        if is_ajax(request):
            return JsonResponse({'success': True, 'turno_id': turno_activo.id})
        return redirect('ventas:inicio_turno', turno_id=turno_activo.id)

    sucursales_usuario = Sucursal.objects.filter(usuarios=usuario)

    if sucursales_usuario.count() == 0:
        if is_ajax(request):
            return JsonResponse({'success': False, 'message': "No tienes ninguna sucursal asignada."})
        messages.error(request, "No tienes ninguna sucursal asignada.")
        return redirect('dashboard')

    if sucursales_usuario.count() == 1:
        try:
            sucursal_unica = sucursales_usuario.first()
            turno = RegistroTurno(usuario=usuario, sucursal=sucursal_unica, inicio_turno=timezone.now())
            turno.save()
            if is_ajax(request):
                return JsonResponse({'success': True, 'turno_id': turno.id})
            return redirect('ventas:inicio_turno', turno_id=turno.id)
        except Exception as e:
            if is_ajax(request):
                return JsonResponse({'success': False, 'message': f"Error al iniciar el turno: {str(e)}"})
            messages.error(request, f"Error al asignar el turno: {str(e)}")
            return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroTurnoForm(request.POST, usuario=request.user)
        if form.is_valid():
            try:
                turno = form.save(commit=False)
                turno.usuario = request.user
                turno.inicio_turno = timezone.now()
                turno.save()
                if is_ajax(request):
                    return JsonResponse({'success': True, 'turno_id': turno.id})
                return redirect('ventas:inicio_turno', turno_id=turno.id)
            except Exception as e:
                if is_ajax(request):
                    return JsonResponse({'success': False, 'message': f"Error al iniciar el turno: {str(e)}"})
                messages.error(request, f"Error al iniciar el turno: {str(e)}")
                return redirect('dashboard')
        else:
            if is_ajax(request):
                return JsonResponse({'success': False, 'message': "Error en el formulario.", 'errors': form.errors})
            messages.error(request, "Error en el formulario.")
    else:
        form = RegistroTurnoForm(usuario=request.user)

    return render(request, 'registro-turnos/dashboard.html', {'form': form})



# Verificar que el usuario es administrador
def es_administrador(user):
    return user.is_staff or user.is_superuser

#@user_passes_test(es_administrador)
def crear_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuario_creado_exitosamente')
    else:
        form = UserCreationForm()
    return render(request, 'registro-turnos/crear_usuario.html', {'form': form})


def usuario_creado_exitosamente(request):
    return render(request, 'registro-turnos/usuario_creado_exitosamente.html')



from .models import RegistroTurno

def turno_exito(request, turno_id):
    # Buscar el turno por su ID y pasarlo a la plantilla de éxito
    turno = RegistroTurno.objects.get(id=turno_id)
    return render(request, 'registro-turnos/turno_exito.html', {'turno': turno})