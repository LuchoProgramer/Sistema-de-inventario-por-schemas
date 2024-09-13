# ventas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from empleados.models import RegistroTurno
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

            # Verificar que hay suficiente inventario
            inventario = producto.inventario_set.filter(sucursal=turno_activo.sucursal).first()
            if inventario and inventario.cantidad >= cantidad:
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

                # Actualizar el inventario
                inventario.cantidad -= cantidad
                inventario.save()

                return redirect('dashboard')
            else:
                form.add_error(None, f"No hay suficiente inventario disponible. Solo hay {inventario.cantidad} unidades.")
    else:
        form = SeleccionVentaForm(sucursal_id=turno_activo.sucursal.id)

    return render(request, 'ventas/registrar_venta.html', {'form': form})


@login_required
def inicio_turno(request, turno_id):
    # Cargar el turno usando el turno_id y verificar que pertenece al empleado logueado
    turno = get_object_or_404(RegistroTurno, id=turno_id, empleado=request.user.empleado)

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
    turno = RegistroTurno.objects.filter(empleado__usuario=request.user, fin_turno__isnull=True).first()

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
    turno = RegistroTurno.objects.filter(empleado__usuario=request.user, fin_turno__isnull=True).first()

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
    turno = RegistroTurno.objects.filter(empleado__usuario=request.user, fin_turno__isnull=True).first()

    if turno:
        carrito_items = Carrito.objects.filter(turno=turno)
        errores = []

        for item in carrito_items:
            # Verificar inventario para cada producto
            inventario = item.producto.inventario_set.filter(sucursal=turno.sucursal).first()
            if inventario and inventario.cantidad >= item.cantidad:
                # Registrar la venta
                venta = Venta.objects.create(
                    turno=turno,
                    sucursal=turno.sucursal,
                    empleado=turno.empleado.usuario,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio,
                    total_venta=item.subtotal(),
                    metodo_pago=request.POST.get('metodo_pago', 'Efectivo'),  # Aquí se selecciona el método de pago
                )
                # Actualizar el inventario
                inventario.cantidad -= item.cantidad
                inventario.save()

                # Generar la factura asociada al turno y al cliente
                factura = Factura.objects.create(
                    sucursal=turno.sucursal,
                    cliente=turno.empleado.cliente,  # Asumiendo que hay un cliente relacionado al empleado
                    empleado=turno.empleado,
                    total_sin_impuestos=item.subtotal(),
                    total_con_impuestos=item.subtotal() * Decimal('1.12'),  # Ejemplo con IVA
                    estado='AUTORIZADA',
                    turno=turno  # Asociamos la factura al turno
                )
            else:
                errores.append(f"No hay suficiente inventario para {item.producto.nombre}. Solo hay {inventario.cantidad} unidades disponibles.")

        if errores:
            return render(request, 'ventas/ver_carrito.html', {'carrito_items': carrito_items, 'total': sum(item.subtotal() for item in carrito_items), 'errores': errores})

        carrito_items.delete()  # Vaciar el carrito después de completar la venta
        return redirect('ventas:inicio_turno', turno_id=turno.id)
    else:
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})

@login_required
def cerrar_turno(request):
    empleado = request.user.empleado
    turno_activo = RegistroTurno.objects.filter(empleado=empleado, fin_turno__isnull=True).first()

    if not turno_activo:
        messages.error(request, "No tienes un turno activo para cerrar.")
        return redirect('ventas:inicio_turno')

    if request.method == 'POST':
        form = CierreCajaForm(request.POST)
        if form.is_valid():
            cierre_caja = form.save(commit=False)
            cierre_caja.empleado = request.user
            cierre_caja.sucursal = turno_activo.sucursal
            cierre_caja.fecha_cierre = timezone.now()
            cierre_caja.save()

            # Marcar el turno como cerrado
            turno_activo.fin_turno = timezone.now()
            turno_activo.save()

            messages.success(request, "Turno cerrado correctamente.")
            # Redirigir al dashboard después del cierre
            return redirect('dashboard')  # Redirige al dashboard sin namespace
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

    # Comparar con los valores ingresados por el empleado
    cierre_caja = CierreCaja.objects.filter(empleado=turno.empleado, fecha_cierre=turno.fin_turno).first()

    context = {
        'turno': turno,
        'ventas': ventas,
        'cierre_caja': cierre_caja,
        'total_ventas_efectivo': total_ventas_efectivo,
        'total_ventas_tarjeta': total_ventas_tarjeta,
        'total_ventas_transferencia': total_ventas_transferencia,
    }

    return render(request, 'ventas/comparar_ventas.html', context)
