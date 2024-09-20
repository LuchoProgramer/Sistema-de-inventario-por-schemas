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

# Verificar si es una solicitud AJAX
def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


# Dashboard: Esta vista maneja la lógica de iniciar turno
@login_required
def dashboard(request): 
    usuario = request.user

    # Verificar si el usuario ya tiene un turno activo
    turno_activo = RegistroTurno.objects.filter(usuario=usuario, fin_turno__isnull=True).first()

    if turno_activo:
        if is_ajax(request):
            return JsonResponse({'success': True, 'turno_id': turno_activo.id})
        return redirect('ventas:inicio_turno', turno_id=turno_activo.id)

    if request.method == 'POST':
        form = RegistroTurnoForm(request.POST, usuario=usuario)  
        if form.is_valid():
            try:
                turno = form.save(commit=False)
                turno.usuario = usuario  
                turno.inicio_turno = timezone.now()
                turno.save()

                request.session['sucursal_seleccionada'] = turno.sucursal.id

                if is_ajax(request):
                    return JsonResponse({'success': True, 'turno_id': turno.id})

                return redirect('ventas:inicio_turno', turno_id=turno.id)
            except Exception as e:
                if is_ajax(request):
                    return JsonResponse({'success': False, 'message': f"Error: {str(e)}"})
                messages.error(request, f"Error al iniciar el turno: {e}")
        else:
            if is_ajax(request):
                return JsonResponse({'success': False, 'message': 'Formulario no válido.'})
            messages.error(request, "Formulario no válido. Por favor, corrige los errores.")
    else:
       

        form = RegistroTurnoForm(usuario=usuario)

    return render(request, 'empleados/dashboard.html', {'form': form})



# Verificar que el usuario es administrador
def es_administrador(user):
    return user.is_staff or user.is_superuser

@user_passes_test(es_administrador)
def crear_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuario_creado_exitosamente')
    else:
        form = UserCreationForm()
    return render(request, 'empleados/crear_usuario.html', {'form': form})


@login_required
def usuario_creado_exitosamente(request):
    return render(request, 'empleados/usuario_creado_exitosamente.html')
