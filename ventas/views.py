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
from inventarios.models import Inventario, Categoria


@transaction.atomic
def registrar_venta(request):
    # Verificar turno activo del usuario
    turno_activo = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()
    if not turno_activo:
        print("No se encontró un turno activo para el usuario.")
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
                print(f"Método de pago no válido: {metodo_pago_seleccionado}")
                form.add_error(None, f"Método de pago no válido: {metodo_pago_seleccionado}")
                return render(request, 'ventas/registrar_venta.html', {'form': form})

            try:
                # Comenzamos una transacción atómica
                with transaction.atomic():
                    # Verificar si el cliente existe
                    cliente = getattr(turno_activo.usuario, 'cliente', None)
                    if not cliente:
                        print("No se encontró un cliente asociado al usuario.")
                        form.add_error(None, "No se encontró un cliente asociado al usuario.")
                        return render(request, 'ventas/registrar_venta.html', {'form': form})

                    # Verificar disponibilidad de inventario antes de crear la factura
                    if producto.stock < cantidad:
                        print(f"No hay suficiente inventario disponible para {producto.nombre}. Stock actual: {producto.stock}, cantidad solicitada: {cantidad}")
                        return JsonResponse({'error': f'No hay suficiente inventario disponible para {producto.nombre}.'}, status=400)

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

                    print(f"Factura creada con número de autorización: {factura.numero_autorizacion}")

                    # Registrar el pago
                    Pago.objects.create(
                        factura=factura,
                        codigo_sri=metodo_pago_seleccionado,
                        descripcion=metodo_pago,
                        total=total_con_impuestos
                    )

                    print(f"Pago registrado para la factura {factura.numero_autorizacion}, método: {metodo_pago_seleccionado}")

                    # Validación para evitar registrar la venta más de una vez
                    if not Venta.objects.filter(factura=factura, producto=producto).exists():
                        # Reducir el inventario solo si no se ha registrado la venta antes
                        producto.stock -= cantidad
                        producto.save()

                        # Registrar la venta
                        VentaService.registrar_venta(turno_activo, producto, cantidad, factura)
                        print(f"Venta registrada para el producto {producto.nombre}, cantidad: {cantidad}")
                    else:
                        print(f"La venta para el producto {producto.nombre} ya está registrada.")

                    return redirect('dashboard')

            except Exception as e:
                # Capturar el error y mostrarlo
                print(f"Error al generar la factura o registrar la venta: {str(e)}")
                return JsonResponse({'error': f'Error al generar la factura o registrar la venta: {str(e)}'}, status=500)

    else:
        form = SeleccionVentaForm(sucursal_id=turno_activo.sucursal.id)

    return render(request, 'ventas/registrar_venta.html', {'form': form})




@login_required
def inicio_turno(request, turno_id):
    # Obtener el turno activo del usuario
    turno = get_object_or_404(RegistroTurno, id=turno_id, usuario=request.user)

    # Obtener la categoría seleccionada y el término de búsqueda desde el request
    categoria_seleccionada = request.GET.get('categoria')
    termino_busqueda = request.GET.get('q')

    # Obtener todas las categorías para mostrarlas en el formulario
    categorias = Categoria.objects.all()

    # Filtrar los productos disponibles en la sucursal del turno activo
    inventarios = Inventario.objects.filter(sucursal=turno.sucursal).select_related('producto__categoria')

    if categoria_seleccionada:
        inventarios = inventarios.filter(producto__categoria_id=categoria_seleccionada)

    if termino_busqueda:
        inventarios = inventarios.filter(producto__nombre__icontains=termino_busqueda)

    # Verificar si los productos en el carrito ya alcanzaron su stock máximo
    carrito_items = Carrito.objects.filter(turno=turno).select_related('producto')
    inventario_dict = {inv.producto.id: inv.cantidad for inv in inventarios}

    for item in carrito_items:
        producto_cantidad = inventario_dict.get(item.producto.id, 0)
        if item.cantidad >= producto_cantidad:
            messages.warning(request, f'El producto {item.producto.nombre} ya tiene todo su stock agregado al carrito.')

    # Renderizar la vista y pasar los inventarios a la plantilla
    return render(request, 'ventas/inicio_turno.html', {
        'turno': turno,
        'inventarios': inventarios,
        'categorias': categorias,  # Pasamos las categorías al template
        'carrito_items': carrito_items  # Pasamos los items del carrito para verificar el stock
    })




@login_required
def agregar_al_carrito(request, producto_id):
    # Obtener el producto con la categoría precargada para evitar una consulta adicional
    producto = get_object_or_404(Producto.objects.select_related('categoria'), id=producto_id)
    
    # Obtener el turno activo del usuario con la sucursal ya cargada para evitar más consultas
    turno = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).select_related('sucursal').first()

    if turno:
        # Obtener el inventario disponible del producto en la sucursal del turno
        try:
            inventario_disponible = Inventario.objects.get(producto=producto, sucursal=turno.sucursal).cantidad
        except Inventario.DoesNotExist:
            messages.error(request, f'No hay inventario disponible para el producto {producto.nombre}.')
            return redirect('ventas:inicio_turno', turno_id=turno.id)

        cantidad = int(request.POST.get('cantidad', 1))  # Obtener la cantidad del formulario, por defecto 1

        # Validar que la cantidad solicitada no exceda el stock disponible
        if cantidad > inventario_disponible:
            messages.error(request, f'No hay suficiente stock de {producto.nombre}. Solo quedan {inventario_disponible} en stock.')
            return redirect('ventas:inicio_turno', turno_id=turno.id)

        # Obtener o crear un ítem en el carrito
        carrito_item, created = Carrito.objects.get_or_create(turno=turno, producto=producto)

        # Actualizar la cantidad en el carrito
        nueva_cantidad = carrito_item.cantidad + cantidad if not created else cantidad

        if nueva_cantidad > inventario_disponible:
            messages.error(request, f'No puedes agregar más de {inventario_disponible} de {producto.nombre}.')
            return redirect('ventas:inicio_turno', turno_id=turno.id)

        carrito_item.cantidad = nueva_cantidad
        carrito_item.save()

        messages.success(request, f'Se ha agregado {cantidad} de {producto.nombre} al carrito.')
        return redirect('ventas:inicio_turno', turno_id=turno.id)
    else:
        messages.error(request, 'No tienes un turno activo.')
        return redirect('ventas:inicio_turno', turno_id=request.POST.get('turno_id', 0))

    

@login_required
def ver_carrito(request):
    # Obtener el turno activo del usuario con la sucursal ya cargada si se usa en la vista
    turno = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).select_related('sucursal').first()

    # Verificar si el usuario ha hecho clic en el botón "Eliminar"
    if request.method == 'POST':
        item_id = request.POST.get('item_id')  # Obtener el ID del producto del formulario
        carrito_item = get_object_or_404(Carrito, id=item_id)
        carrito_item.delete()  # Eliminar el producto del carrito
        return redirect('ventas:ver_carrito')  # Redirigir al carrito actualizado

    if turno:
        # Obtener los items del carrito con el producto precargado
        carrito_items = Carrito.objects.filter(turno=turno).select_related('producto')

        # Calcular el total utilizando los datos ya cargados
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
        return redirect('ventas:inicio_turno', turno_id=turno_activo.id)

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



def buscar_productos(request):
    termino_busqueda = request.GET.get('q', '')
    turno_id = request.GET.get('turno_id')

    # Obtener el turno activo del usuario
    turno = get_object_or_404(RegistroTurno, id=turno_id, usuario=request.user)

    # Filtrar los productos por nombre y sucursal del turno activo
    inventarios = Inventario.objects.filter(sucursal=turno.sucursal, producto__nombre__icontains=termino_busqueda)

    # Crear una lista de los productos filtrados
    productos_filtrados = [
        {
            'id': inventario.producto.id,
            'nombre': inventario.producto.nombre,
            'precio': inventario.producto.precio_venta,
            'stock': inventario.cantidad,
            'imagen': inventario.producto.image.url if inventario.producto.image else '/static/default_image.png'
        } for inventario in inventarios
    ]

    return JsonResponse({'productos': productos_filtrados})
