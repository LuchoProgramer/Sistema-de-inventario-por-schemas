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
from django.http import JsonResponse
from django.db import transaction


@transaction.atomic
def registrar_venta(request):
    turno_activo = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()
    if not turno_activo:
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})

    if request.method == 'POST':
        form = SeleccionVentaForm(request.POST, sucursal_id=turno_activo.sucursal.id)
        if form.is_valid():
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad']
            metodo_pago_seleccionado = request.POST.get('metodo_pago')

            # Obtener el código SRI del método de pago
            metodo_pago = dict(Pago.METODOS_PAGO_SRI).get(metodo_pago_seleccionado)

            if not metodo_pago:
                form.add_error(None, f"Método de pago no válido: {metodo_pago_seleccionado}")
                return render(request, 'ventas/registrar_venta.html', {'form': form})

            try:
                # Comenzamos una transacción atómica
                with transaction.atomic():
                    # Verificar si el cliente existe
                    cliente = getattr(turno_activo.usuario, 'cliente', None)
                    if not cliente:
                        form.add_error(None, "No se encontró un cliente asociado al usuario.")
                        return render(request, 'ventas/registrar_venta.html', {'form': form})

                    # Crear la factura
                    total_sin_impuestos = Decimal('100.00')  # Ajusta según tu lógica
                    total_con_impuestos = total_sin_impuestos * Decimal('1.12')

                    # Asignación segura de factura
                    factura = Factura.objects.create(
                        sucursal=turno_activo.sucursal,
                        cliente=cliente,
                        usuario=turno_activo.usuario,
                        total_sin_impuestos=total_sin_impuestos,
                        total_con_impuestos=total_con_impuestos,
                        estado='AUTORIZADA',
                        registroturno=turno_activo
                    )

                    if not factura:
                        return JsonResponse({'error': 'Error al crear la factura. No se pudo registrar la venta.'}, status=500)

                    # Registrar el pago
                    Pago.objects.create(
                        factura=factura,
                        codigo_sri=metodo_pago_seleccionado,  # Código SRI de pago (como '01' para efectivo)
                        descripcion=metodo_pago,
                        total=total_con_impuestos
                    )

                    # Registrar la venta, asegurando que la factura esté asignada
                    VentaService.registrar_venta(turno_activo, producto, cantidad, factura)

                    return redirect('dashboard')

            except Exception as e:
                # Capturar el error y mostrarlo
                return JsonResponse({'error': f'Error al generar la factura o registrar la venta: {str(e)}'}, status=500)

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
    
    # Obtener el turno activo del usuario
    turno = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()
    print(f"Turno activo obtenido: {turno}")

    if turno:
        carrito_item, created = Carrito.objects.get_or_create(turno=turno, producto=producto)
        if not created:
            carrito_item.cantidad += 1
            print(f"Producto ya existente en el carrito. Nueva cantidad: {carrito_item.cantidad}")
        else:
            print(f"Producto {producto.nombre} agregado al carrito.")
        carrito_item.save()
        return redirect('ventas:inicio_turno', turno_id=turno.id)
    else:
        print("No hay turno activo para este usuario.")
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
    
def finalizar_venta(request):
    turno_activo = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()
    if not turno_activo:
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})

    # Obtener productos en el carrito
    carrito_items = Carrito.objects.filter(turno=turno_activo)

    if not carrito_items.exists():
        return render(request, 'ventas/error.html', {'mensaje': 'El carrito está vacío. No se puede finalizar la venta.'})

    # Calcular totales
    total_sin_impuestos = sum(item.subtotal() for item in carrito_items)
    total_con_impuestos = total_sin_impuestos * Decimal('1.12')  # Aplicar IVA del 12%

    # Crear la factura antes de registrar las ventas
    factura = Factura.objects.create(
        sucursal=turno_activo.sucursal,
        cliente=turno_activo.usuario.cliente,  # Asegúrate de que el cliente está asociado
        usuario=turno_activo.usuario,
        total_sin_impuestos=total_sin_impuestos,
        total_con_impuestos=total_con_impuestos,
        estado='AUTORIZADA',
        registroturno=turno_activo
    )

    # Registrar cada venta en base a los productos del carrito
    for item in carrito_items:
        VentaService.registrar_venta(turno_activo, item.producto, item.cantidad, factura)

    # Vaciar el carrito después de completar la venta
    carrito_items.delete()

    return redirect('ventas:inicio_turno', turno_id=turno_activo.id)



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
