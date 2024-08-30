# ventas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from empleados.models import RegistroTurno
from .forms import SeleccionVentaForm
from .models import Venta, Carrito
from django.utils import timezone
from inventarios.models import Producto

@login_required
def registrar_venta(request):
    empleado = request.user.empleado
    turno_activo = RegistroTurno.objects.filter(empleado=empleado, fin_turno__isnull=True).first()

    if not turno_activo:
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo. Inicia un turno para registrar ventas.'})

    if request.method == 'POST':
        form = SeleccionVentaForm(request.POST, sucursal_id=turno_activo.sucursal.id)
        if form.is_valid():
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad']
            precio_unitario = producto.precio
            total_venta = cantidad * precio_unitario

            venta = Venta.objects.create(
                turno=turno_activo,
                sucursal=turno_activo.sucursal,
                empleado=empleado.usuario,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                total_venta=total_venta,
                metodo_pago=request.POST.get('metodo_pago'),
                fecha=timezone.now(),
            )

            return redirect('dashboard')
    else:
        form = SeleccionVentaForm(sucursal_id=turno_activo.sucursal.id)

    return render(request, 'ventas/registrar_venta.html', {'form': form})


# ventas/views.py
@login_required
def inicio_turno(request):
    turno = RegistroTurno.objects.filter(empleado__usuario=request.user, fin_turno__isnull=True).first()

    if turno:
        productos = Producto.objects.filter(inventario__sucursal=turno.sucursal)
        return render(request, 'ventas/inicio_turno.html', {'turno': turno, 'productos': productos})
    else:
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})


@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    turno = RegistroTurno.objects.filter(empleado__usuario=request.user, fin_turno__isnull=True).first()

    if turno:
        carrito_item, created = Carrito.objects.get_or_create(turno=turno, producto=producto)
        if not created:
            carrito_item.cantidad += 1
        carrito_item.save()
        return redirect('ventas:inicio_turno')
    else:
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})
    

@login_required
def ver_carrito(request):
    turno = RegistroTurno.objects.filter(empleado__usuario=request.user, fin_turno__isnull=True).first()
    
    if turno:
        carrito_items = Carrito.objects.filter(turno=turno)
        total = sum(item.subtotal() for item in carrito_items)  # subtotal usa ahora precio_venta
        return render(request, 'ventas/ver_carrito.html', {'carrito_items': carrito_items, 'total': total})
    else:
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})

    
@login_required
def finalizar_venta(request):
    turno = RegistroTurno.objects.filter(empleado__usuario=request.user, fin_turno__isnull=True).first()

    if turno:
        carrito_items = Carrito.objects.filter(turno=turno)
        for item in carrito_items:
            Venta.objects.create(
                turno=turno,
                sucursal=turno.sucursal,
                empleado=turno.empleado.usuario,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio,
                total_venta=item.subtotal(),
                metodo_pago="Efectivo",  # Aquí podrías permitir elegir el método de pago
            )
        carrito_items.delete()  # Vaciar el carrito después de completar la venta
        return redirect('ventas:inicio_turno')
    else:
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})