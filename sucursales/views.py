from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Sucursal
from .forms import SucursalForm, RazonSocialForm
from django.contrib.auth.decorators import login_required

# Lista de sucursales
@login_required
def lista_sucursales(request):
    sucursales = Sucursal.objects.all()
    return render(request, 'sucursales/lista_sucursales.html', {'sucursales': sucursales})

# Crear sucursal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SucursalForm

@login_required
def crear_sucursal(request):
    if request.method == 'POST':
        form = SucursalForm(request.POST)
        if form.is_valid():
            sucursal = form.save(commit=False)  # Guarda la instancia sin los m2m aún
            sucursal.save()  # Guarda la sucursal en la base de datos
            form.save_m2m()  # Guarda la relación de muchos a muchos (usuarios)
            messages.success(request, f'Sucursal "{sucursal.nombre}" creada exitosamente.')
            return redirect('sucursales:lista_sucursales')  # Redirige a la lista de sucursales
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = SucursalForm()

    return render(request, 'sucursales/crear_sucursal.html', {'form': form})


# Editar sucursal
@login_required
def editar_sucursal(request, sucursal_id):
    sucursal = get_object_or_404(Sucursal, pk=sucursal_id)
    if request.method == 'POST':
        form = SucursalForm(request.POST, instance=sucursal)
        if form.is_valid():
            form.save()  # Actualiza la sucursal y los usuarios asignados
            messages.success(request, 'Sucursal actualizada exitosamente.')
            return redirect('sucursales:lista_sucursales')
    else:
        form = SucursalForm(instance=sucursal)
    return render(request, 'sucursales/editar_sucursal.html', {'form': form})

# Eliminar sucursal
@login_required
def eliminar_sucursal(request, sucursal_id):
    sucursal = get_object_or_404(Sucursal, id=sucursal_id)
    if request.method == 'POST':
        sucursal.delete()
        messages.success(request, 'Sucursal eliminada exitosamente.')
        return redirect('sucursales:lista_sucursales')
    return render(request, 'sucursales/eliminar_sucursal.html', {'sucursal': sucursal})


def crear_razon_social(request):
    if request.method == 'POST':
        form = RazonSocialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Razón Social creada exitosamente.')
            return redirect('sucursales:lista_razones_sociales')  # Ajusta la redirección según tu flujo
    else:
        form = RazonSocialForm()

    return render(request, 'sucursales/crear_razon_social.html', {'form': form})