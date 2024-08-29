# views.py (si es necesario actualizar)
from django.shortcuts import render
from .forms import SeleccionVentaForm
from django.contrib.auth.decorators import login_required

@login_required
def crear_venta(request):
    if request.method == 'POST':
        form = SeleccionVentaForm(request.POST, sucursal_id=request.POST.get('sucursal'))
        if form.is_valid():
            # Procesar la información de la venta (en este punto, sabemos que el stock es suficiente)
            # Aquí es donde podrías avanzar al siguiente paso del flujo, como la confirmación de la venta.
            pass
    else:
        form = SeleccionVentaForm()
    
    return render(request, 'mi_aplicacion/crear_venta.html', {'form': form})
