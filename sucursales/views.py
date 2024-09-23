from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Sucursal
from .forms import SucursalForm
from django.contrib.auth.decorators import login_required

# Lista de sucursales
@login_required
def lista_sucursales(request):
    sucursales = Sucursal.objects.all()
    return render(request, 'sucursales/lista_sucursales.html', {'sucursales': sucursales})

# Crear sucursal
@login_required
def crear_sucursal(request):
    if request.method == 'POST':
        form = SucursalForm(request.POST)
        if form.is_valid():
            form.save()  # Esto guardará tanto la sucursal como los usuarios asignados
            messages.success(request, 'Sucursal creada exitosamente.')
            return redirect('sucursales:lista_sucursales')
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
