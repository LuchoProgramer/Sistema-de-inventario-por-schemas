from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from RegistroTurnos.models import RegistroTurno
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test
from .forms import RegistroTurnoForm, CustomUserCreationForm  # Descomentado para usar el formulario
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
    print(f"Usuario: {usuario.username}, es administrador: {usuario.is_staff or usuario.is_superuser}")

    # Verificar si el usuario ya tiene un turno activo (solo una consulta)
    turno_activo = RegistroTurno.objects.filter(usuario=usuario, fin_turno__isnull=True).first()
    if turno_activo:
        print(f"Turno activo encontrado: {turno_activo.id} para el usuario {usuario.username}")
        if is_ajax(request):
            return JsonResponse({'success': True, 'turno_id': turno_activo.id})
        return redirect('ventas:inicio_turno', turno_id=turno_activo.id)

    # Obtener las sucursales del usuario, en lugar de contar repetidamente, guardamos en una variable
    sucursales_usuario = list(Sucursal.objects.filter(usuarios=usuario))
    sucursales_count = len(sucursales_usuario)
    print(f"Cantidad de sucursales asignadas al usuario {usuario.username}: {sucursales_count}")

    # Si el usuario no tiene sucursales, redirigir a la vista `sin_sucursales`
    if sucursales_count == 0:
        print(f"Usuario {usuario.username} no tiene sucursales asignadas. Redirigiendo a la vista `sin_sucursales`.")
        return redirect('sin_sucursales')

    # Mostrar el dashboard sin redirigir si el usuario tiene una sola sucursal
    if sucursales_count == 1:
        sucursal_unica = sucursales_usuario[0]
        print(f"Usuario {usuario.username} tiene una sola sucursal asignada: {sucursal_unica.id}")
        form = RegistroTurnoForm(usuario=request.user, initial={'sucursal': sucursal_unica})
    else:
        form = RegistroTurnoForm(usuario=request.user)
        print(f"Mostrando el formulario para seleccionar sucursal e iniciar turno para el usuario {usuario.username}")

    if request.method == 'POST':
        print(f"Usuario {usuario.username} está intentando iniciar un turno con datos POST.")
        form = RegistroTurnoForm(request.POST, usuario=request.user)
        if form.is_valid():
            try:
                turno = form.save(commit=False)
                turno.usuario = request.user
                turno.inicio_turno = timezone.now()
                turno.save()
                print(f"Turno creado exitosamente: {turno.id} para el usuario {usuario.username}")
                if is_ajax(request):
                    return JsonResponse({'success': True, 'turno_id': turno.id})
                return redirect('ventas:inicio_turno', turno_id=turno.id)
            except Exception as e:
                print(f"Error al iniciar el turno para el usuario {usuario.username}: {str(e)}")
                if is_ajax(request):
                    return JsonResponse({'success': False, 'message': f"Error al iniciar el turno: {str(e)}"})
                messages.error(request, f"Error al iniciar el turno: {str(e)}")
        else:
            print(f"Formulario de turno inválido para el usuario {usuario.username}. Errores: {form.errors}")
            if is_ajax(request):
                return JsonResponse({'success': False, 'message': "Error en el formulario.", 'errors': form.errors})
            messages.error(request, "Error en el formulario.")

    return render(request, 'registro-turnos/dashboard.html', {'form': form})


@login_required
def sin_sucursales(request):
    return render(request, 'registro-turnos/sin_sucursales.html', {
        'mensaje': "No tienes ninguna sucursal asignada. Por favor, contacta con un administrador para más información."
    })

# Verificar que el usuario es administrador
def es_administrador(user):
    return user.is_staff or user.is_superuser

#@user_passes_test(es_administrador)
def crear_usuario(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuario_creado_exitosamente')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registro-turnos/crear_usuario.html', {'form': form})



def usuario_creado_exitosamente(request):
    return render(request, 'registro-turnos/usuario_creado_exitosamente.html')



from .models import RegistroTurno

def turno_exito(request, turno_id):
    # Buscar el turno por su ID y pasarlo a la plantilla de éxito
    turno = RegistroTurno.objects.get(id=turno_id)
    return render(request, 'registro-turnos/turno_exito.html', {'turno': turno})