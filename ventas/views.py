# ventas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from RegistroTurnos.models import RegistroTurno
from .forms import SeleccionVentaForm, CierreCajaForm
from .models import Venta, Carrito
from django.utils import timezone
from inventarios.models import Producto
from django.contrib import messages
from django.db.models import Sum
from ventas.models import Venta, CierreCaja
from facturacion.models import Factura, Pago
from decimal import Decimal
from sucursales.models import Sucursal
from ventas.services import VentaService
from ventas.services import TurnoService 
from datetime import timedelta


@login_required
def registrar_venta(request):
    # Usar request.user directamente para obtener el turno activo
    turno_activo = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()

    if not turno_activo:
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo. Inicia un turno para registrar ventas.'})

    if request.method == 'POST':
        form = SeleccionVentaForm(request.POST, sucursal_id=turno_activo.sucursal.id)
        if form.is_valid():
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad']
            metodo_pago = request.POST.get('metodo_pago')

            try:
                # Usar turno_activo (encontrado usando request.user)
                VentaService.registrar_venta(turno_activo, producto, cantidad, metodo_pago)
                return redirect('dashboard')
            except ValueError as e:
                form.add_error(None, str(e))

    else:
        form = SeleccionVentaForm(sucursal_id=turno_activo.sucursal.id)

    return render(request, 'ventas/registrar_venta.html', {'form': form})


@login_required
def inicio_turno(request, turno_id):
    # Cargar el turno usando el turno_id y verificar que pertenece al usuario logueado
    turno = get_object_or_404(RegistroTurno, id=turno_id, usuario=request.user)  # Cambiado de empleado a usuario

    # Filtrar los productos disponibles en la sucursal del turno y con inventario mayor a 0
    productos = Producto.objects.filter(inventario__sucursal=turno.sucursal, inventario__cantidad__gt=0)

    # Renderizar la plantilla mostrando los detalles del turno y los productos disponibles
    return render(request, 'ventas/inicio_turno.html', {
        'turno': turno,  # Pasar el turno activo a la plantilla
        'productos': productos,  # Pasar la lista de productos a la plantilla filtrados
        'sucursal': turno.sucursal  # Mostrar la sucursal asociada al turno
    })

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Cambiado de empleado=request.user.empleado a usuario=request.user
    turno = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()

    if turno:
        carrito_item, created = Carrito.objects.get_or_create(turno=turno, producto=producto)
        if not created:
            carrito_item.cantidad += 1
        carrito_item.save()
        return redirect('ventas:inicio_turno', turno_id=turno.id)
    else:
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})
    

@login_required
def ver_carrito(request):
    # Cambiado de empleado=request.user.empleado a usuario=request.user
    turno = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()

    # Verificar si el usuario ha hecho clic en el botón "Eliminar"
    if request.method == 'POST':
        item_id = request.POST.get('item_id')  # Obtener el ID del producto del formulario
        carrito_item = get_object_or_404(Carrito, id=item_id)
        carrito_item.delete()  # Eliminar el producto del carrito
        return redirect('ventas:ver_carrito')  # Redirigir al carrito actualizado

    if turno:
        carrito_items = Carrito.objects.filter(turno=turno)
        total = sum(item.subtotal() for item in carrito_items)

        return render(request, 'ventas/ver_carrito.html', {
            'carrito_items': carrito_items,
            'total': total,
            'turno': turno
        })
    else:
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})
    
@login_required
def finalizar_venta(request):
    # Cambiado de empleado=request.user.empleado a usuario=request.user
    turno = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()

    if not turno:
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})

    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago', 'Efectivo')  # Selecciona el método de pago

        try:
            # Usar el servicio para finalizar la venta
            factura = VentaService.finalizar_venta(turno, metodo_pago)
            return redirect('ventas:inicio_turno', turno_id=turno.id)
        except ValueError as e:
            return render(request, 'ventas/ver_carrito.html', {
                'errores': str(e), 
                'carrito_items': Carrito.objects.filter(turno=turno),
                'total': sum(item.subtotal() for item in Carrito.objects.filter(turno=turno))
            })
    
    return redirect('ventas:ver_carrito')

@login_required
def cerrar_turno(request):
    usuario = request.user  # Cambiado de empleado a usuario
    turno_activo = RegistroTurno.objects.filter(usuario=usuario, fin_turno__isnull=True).first()

    if not turno_activo:
        messages.error(request, "No tienes un turno activo para cerrar.")
        return redirect('ventas:inicio_turno')

    if request.method == 'POST':
        form = CierreCajaForm(request.POST)
        if form.is_valid():
            try:
                # Usar el servicio para cerrar el turno
                TurnoService.cerrar_turno(turno_activo, form.cleaned_data)
                messages.success(request, "Turno cerrado correctamente.")
                return redirect('dashboard')  # Redirige al dashboard después del cierre
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Por favor, revisa los datos ingresados.")
    
    else:
        form = CierreCajaForm()

    return render(request, 'ventas/cierre_caja.html', {'form': form, 'turno': turno_activo})

@login_required
@user_passes_test(lambda u: u.is_staff)
def comparar_cierre_ventas(request, turno_id):
    # Obtener el turno
    turno = get_object_or_404(RegistroTurno, id=turno_id)

    # Obtener las ventas realizadas durante el turno
    ventas = Venta.objects.filter(turno=turno)

    # Calcular totales de ventas reales
    total_ventas_efectivo = ventas.filter(metodo_pago='Efectivo').aggregate(Sum('total_venta'))['total_venta__sum'] or 0
    total_ventas_tarjeta = ventas.filter(metodo_pago='Tarjeta').aggregate(Sum('total_venta'))['total_venta__sum'] or 0
    total_ventas_transferencia = ventas.filter(metodo_pago='Transferencia').aggregate(Sum('total_venta'))['total_venta__sum'] or 0

    # Comparar con los valores ingresados por el usuario (anteriormente empleado), usando un rango de tiempo
    cierre_caja = CierreCaja.objects.filter(
        usuario=turno.usuario,  # Cambiado de empleado a usuario
        fecha_cierre__range=(turno.fin_turno - timedelta(minutes=5), turno.fin_turno + timedelta(minutes=5))
    ).first()

    if not cierre_caja:
        return render(request, 'ventas/error.html', {'mensaje': 'No se encontró un cierre de caja para este turno.'})

    context = {
        'turno': turno,
        'ventas': ventas,
        'cierre_caja': cierre_caja,
        'total_ventas_efectivo': total_ventas_efectivo,
        'total_ventas_tarjeta': total_ventas_tarjeta,
        'total_ventas_transferencia': total_ventas_transferencia,
    }

    return render(request, 'ventas/comparar_ventas.html', context)
