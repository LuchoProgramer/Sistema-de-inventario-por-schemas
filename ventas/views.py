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
from .utils import obtener_total_items_en_carrito
from inventarios.models import Inventario, Categoria, Presentacion
from inventarios.services.validacion_inventario_service import ValidacionInventarioService
from inventarios.services.ajuste_inventario_service import AjusteInventarioService
from inventarios.services.movimiento_inventario_service import MovimientoInventarioService
from inventarios.services.calculo_precio_service import CalculoPrecioService
from inventarios.services.obtener_inventarios_sucursal_service import ObtenerInventariosSucursalService
from django.views.decorators.http import require_POST


@login_required
@transaction.atomic
def registrar_venta(request):
    print("Verificando turno activo...")
    turno_activo = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()
    
    if not turno_activo:
        print("Error: No tienes un turno activo.")
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})

    if request.method == 'POST':
        form = SeleccionVentaForm(request.POST, sucursal_id=turno_activo.sucursal.id)
        
        if form.is_valid():
            producto = form.cleaned_data['producto']
            presentacion = form.cleaned_data['presentacion']
            cantidad = form.cleaned_data['cantidad']

            print(f"Producto seleccionado: {producto.nombre}, Presentación: {presentacion.nombre_presentacion}, Cantidad seleccionada: {cantidad}")
            print(f"Cada presentación tiene {presentacion.cantidad} unidades.")

            metodo_pago_seleccionado = request.POST.get('metodo_pago')
            metodo_pago = dict(Pago.METODOS_PAGO_SRI).get(metodo_pago_seleccionado)

            if not metodo_pago:
                form.add_error(None, f"Método de pago no válido: {metodo_pago_seleccionado}")
                return render(request, 'ventas/registrar_venta.html', {'form': form})

            try:
                with transaction.atomic():
                    cliente = getattr(turno_activo.usuario, 'cliente', None)
                    if not cliente:
                        form.add_error(None, "No se encontró un cliente asociado al usuario.")
                        return render(request, 'ventas/registrar_venta.html', {'form': form})

                    # 1. Validar inventario
                    if not ValidacionInventarioService.validar_inventario(producto, presentacion, cantidad):
                        return JsonResponse({'error': f'No hay suficiente inventario disponible para {producto.nombre}.'}, status=400)

                    # 2. Calcular el precio usando el servicio
                    total_sin_impuestos = CalculoPrecioService.calcular_precio(presentacion, cantidad)
                    total_con_impuestos = total_sin_impuestos * Decimal('1.12')  # Aplicar impuestos

                    # 3. Crear la factura
                    factura = Factura.objects.create(
                        sucursal=turno_activo.sucursal,
                        cliente=cliente,
                        usuario=turno_activo.usuario,
                        total_sin_impuestos=total_sin_impuestos,
                        total_con_impuestos=total_con_impuestos,
                        estado='AUTORIZADA',
                        registroturno=turno_activo
                    )

                    # 4. Registrar la venta y ajustar el inventario
                    VentaService.registrar_venta(
                        turno_activo=turno_activo, 
                        producto=producto, 
                        cantidad=cantidad,  # Usamos la cantidad directamente
                        factura=factura, 
                        presentacion=presentacion
                    )

                    # 5. Ajustar inventario después de la venta
                    AjusteInventarioService.ajustar_inventario(producto, presentacion, cantidad)

                    return redirect('dashboard')

            except Exception as e:
                print(f"Error al generar la factura o registrar la venta: {str(e)}")
                return JsonResponse({'error': f'Error al generar la factura o registrar la venta: {str(e)}'}, status=500)

    else:
        print("Solicitud GET: Mostrando formulario de selección de venta.")
        form = SeleccionVentaForm(sucursal_id=turno_activo.sucursal.id)

    return render(request, 'ventas/registrar_venta.html', {'form': form})








from inventarios.models import Presentacion


@login_required
def inicio_turno(request, turno_id):
    # Obtener el turno activo para el usuario
    turno = get_object_or_404(RegistroTurno, id=turno_id, usuario=request.user)

    # Filtrar categorías y manejar búsqueda
    categoria_seleccionada = request.GET.get('categoria')
    termino_busqueda = request.GET.get('q')
    categorias = Categoria.objects.all()

    # Obtener los inventarios de la sucursal del turno activo
    inventarios = ObtenerInventariosSucursalService.obtener_inventarios(turno.sucursal)

    if categoria_seleccionada:
        inventarios = inventarios.filter(producto__categoria_id=categoria_seleccionada)

    if termino_busqueda:
        inventarios = inventarios.filter(producto__nombre__icontains=termino_busqueda)

    # Filtrar presentaciones por la sucursal del turno
    for inventario in inventarios:
        inventario.presentaciones = inventario.producto.presentaciones.filter(sucursal=turno.sucursal)

    # Obtener los items del carrito
    carrito_items = Carrito.objects.filter(turno=turno).select_related('producto')

    # Validar stock usando el servicio
    for item in carrito_items:
        if not ValidacionInventarioService.validar_stock_disponible(item.producto, item.cantidad):
            messages.warning(request, f'El producto {item.producto.nombre} ya tiene todo su stock agregado al carrito.')

    # Renderizar la plantilla con los datos necesarios
    return render(request, 'ventas/inicio_turno.html', {
        'turno': turno,
        'inventarios': inventarios,
        'categorias': categorias,
        'carrito_items': carrito_items,
    })








from django.http import JsonResponse, HttpResponseNotAllowed

@login_required
def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        # Obtener el producto con la categoría precargada para evitar una consulta adicional
        producto = get_object_or_404(Producto.objects.select_related('categoria'), id=producto_id)
        print(f"Producto seleccionado: {producto.nombre}")

        # Obtener el turno activo del usuario con la sucursal ya cargada para evitar más consultas
        turno = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).select_related('sucursal').first()
        print(f"Turno activo encontrado: {turno.id} en la sucursal {turno.sucursal.nombre}" if turno else "No hay turno activo")

        if turno:
            # Obtener la presentación seleccionada desde el formulario
            presentacion_id = request.POST.get('presentacion')  # Obtener el id de la presentación seleccionada
            presentacion = get_object_or_404(Presentacion, id=presentacion_id, producto=producto)
            print(f"Presentación seleccionada: {presentacion.nombre_presentacion} con {presentacion.cantidad} unidades por presentación")

            # Obtener la cantidad solicitada desde el formulario
            cantidad = int(request.POST.get('cantidad', 1))  # Obtener la cantidad del formulario, por defecto 1
            total_unidades_solicitadas = presentacion.cantidad * cantidad  # Calcular las unidades totales según la presentación
            print(f"Total de unidades solicitadas: {total_unidades_solicitadas} (Cantidad solicitada: {cantidad}, Unidades por presentación: {presentacion.cantidad})")

            # Validar inventario usando el servicio ValidacionInventarioService
            if not ValidacionInventarioService.validar_inventario(producto, presentacion, cantidad):
                messages.error(request, f'No hay suficiente inventario disponible para {producto.nombre}.')
                return redirect('ventas:inicio_turno', turno_id=turno.id)

            # Obtener o crear un ítem en el carrito para esta presentación
            carrito_items = Carrito.objects.filter(turno=turno, producto=producto, presentacion=presentacion)

            if carrito_items.exists():
                carrito_item = carrito_items.first()  # Obtener el primer ítem existente en el carrito
                nueva_cantidad = carrito_item.cantidad + cantidad  # Sumar la cantidad al existente
                print(f"Carrito actualizado para el producto: {producto.nombre}, Presentación: {presentacion.nombre_presentacion}")
            else:
                carrito_item = Carrito(turno=turno, producto=producto, presentacion=presentacion, cantidad=cantidad)
                nueva_cantidad = cantidad
                print(f"Carrito creado para el producto: {producto.nombre}, Presentación: {presentacion.nombre_presentacion}")

            total_unidades_en_carrito = presentacion.cantidad * nueva_cantidad  # Unidades según la presentación
            print(f"Total de unidades en carrito: {total_unidades_en_carrito} (Nueva cantidad: {nueva_cantidad})")

            carrito_item.cantidad = nueva_cantidad
            carrito_item.save()
            print(f"Cantidad actualizada en el carrito: {nueva_cantidad}")

            # Después de agregar al carrito, actualizar la sesión
            cart = request.session.get('cart', {})
            key = f"{producto_id}_{presentacion.id}"  # Usar un identificador único para producto y presentación
            if key in cart:
                cart[key]['quantity'] += cantidad
            else:
                cart[key] = {
                    'producto_id': producto_id,
                    'presentacion_id': presentacion.id,
                    'quantity': cantidad
                }
            request.session['cart'] = cart
            request.session.modified = True
            print("Contenido del carrito en la sesión después de la actualización:", cart)

            # Devolver la respuesta JSON
            total_items = obtener_total_items_en_carrito(request)
            return JsonResponse({'message': 'Producto agregado al carrito', 'total_items': total_items}, status=200)
        else:
            messages.error(request, 'No tienes un turno activo.')
            return JsonResponse({'status': 'error', 'message': 'No tienes un turno activo.'})
    else:
        return HttpResponseNotAllowed(['POST'])










    

@login_required
def ver_carrito(request):
    # Obtener el turno activo del usuario con la sucursal ya cargada si se usa en la vista
    turno = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).select_related('sucursal').first()
    print(f"Turno activo encontrado: {turno.id} en la sucursal {turno.sucursal.nombre}" if turno else "No hay turno activo.")

    # Verificar si el usuario ha hecho clic en el botón "Eliminar"
    if request.method == 'POST':
        item_id = request.POST.get('item_id')  # Obtener el ID del producto del formulario
        carrito_item = get_object_or_404(Carrito, id=item_id)
        print(f"Eliminando el producto del carrito: {carrito_item.producto.nombre} con presentación {carrito_item.presentacion.nombre_presentacion}")
        
        # Eliminar el producto del carrito en la base de datos
        carrito_item.delete()
        
        # Actualizar la sesión para reflejar la eliminación
        cart = request.session.get('cart', {})
        key = f"{carrito_item.producto.id}_{carrito_item.presentacion.id}"
        if key in cart:
            del cart[key]
            request.session['cart'] = cart
            request.session.modified = True
            print("Carrito actualizado en la sesión después de la eliminación:", cart)
        
        return redirect('ventas:ver_carrito')  # Redirigir al carrito actualizado

    if turno:
        # Obtener los items del carrito con el producto y presentación precargados
        carrito_items = Carrito.objects.filter(turno=turno).select_related('producto', 'presentacion')
        print(f"Carrito contiene {carrito_items.count()} items.")

        # Actualizar la sesión con los ítems actuales del carrito para mantener sincronización
        cart = {}
        for item in carrito_items:
            key = f"{item.producto.id}_{item.presentacion.id}"
            cart[key] = {
                'producto_id': item.producto.id,
                'presentacion_id': item.presentacion.id,
                'quantity': item.cantidad
            }
        request.session['cart'] = cart
        request.session.modified = True
        print("Carrito sincronizado con la sesión:", cart)

        # Calcular el total utilizando los datos ya cargados
        total = sum(item.subtotal() for item in carrito_items)
        print(f"Total calculado del carrito: {total}")

        return render(request, 'ventas/ver_carrito.html', {
            'carrito_items': carrito_items,
            'total': total,
            'turno': turno
        })
    else:
        print("No hay turno activo.")
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})




@login_required
@require_POST
def eliminar_item_carrito(request):
    # Obtener el ID del item a eliminar
    item_id = request.POST.get('item_id')
    
    if item_id:
        try:
            # Verificar que el item pertenece al usuario actual y está en el turno activo
            turno = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()
            carrito_item = Carrito.objects.get(id=item_id, turno=turno)
            print(f"Eliminando el producto del carrito: {carrito_item.producto.nombre} con presentación {carrito_item.presentacion.nombre_presentacion}")
            
            # Eliminar el producto del carrito
            carrito_item.delete()
            
            # Recalcular el total
            carrito_items = Carrito.objects.filter(turno=turno)
            total = sum(item.subtotal() for item in carrito_items)
            
            return JsonResponse({'success': True, 'total': total})
        except Carrito.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'El item no existe o no pertenece al usuario.'})
    else:
        return JsonResponse({'success': False, 'error': 'No se proporcionó un ID de item válido.'})

    
@login_required
@require_POST
def actualizar_cantidad_carrito(request):
    item_id = request.POST.get('item_id')
    nueva_cantidad = request.POST.get('cantidad')
    
    if item_id and nueva_cantidad:
        try:
            nueva_cantidad = int(nueva_cantidad)
            if nueva_cantidad < 1:
                return JsonResponse({'success': False, 'error': 'La cantidad debe ser al menos 1.'})
            turno = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()
            carrito_item = Carrito.objects.get(id=item_id, turno=turno)
            carrito_item.cantidad = nueva_cantidad
            carrito_item.save()
            
            # Calcular el nuevo subtotal y total
            nuevo_subtotal = carrito_item.subtotal()
            carrito_items = Carrito.objects.filter(turno=turno)
            total = sum(item.subtotal() for item in carrito_items)
            
            return JsonResponse({
                'success': True,
                'nuevo_subtotal': nuevo_subtotal,
                'total': total
            })
        except ValueError:
            return JsonResponse({'success': False, 'error': 'La cantidad debe ser un número entero.'})
        except Carrito.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'El item no existe o no pertenece al usuario.'})
    else:
        return JsonResponse({'success': False, 'error': 'Datos incompletos.'})




@login_required
def finalizar_venta(request):
    # Obtener el turno activo del usuario
    turno_activo = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()
    if not turno_activo:
        print("No tienes un turno activo.")
        return render(request, 'ventas/error.html', {'mensaje': 'No tienes un turno activo.'})

    # Obtener productos en el carrito
    carrito_items = Carrito.objects.filter(turno=turno_activo)
    print(f"Carrito contiene {carrito_items.count()} productos.")

    if not carrito_items.exists():
        print("El carrito está vacío. No se puede finalizar la venta.")
        return render(request, 'ventas/error.html', {'mensaje': 'El carrito está vacío. No se puede finalizar la venta.'})

    # Calcular totales
    total_sin_impuestos = sum(item.subtotal() for item in carrito_items)
    total_con_impuestos = total_sin_impuestos * Decimal('1.12')  # Aplicar IVA del 12%
    print(f"Total sin impuestos: {total_sin_impuestos}, Total con impuestos: {total_con_impuestos}")

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
    print(f"Factura creada con ID: {factura.id}")

    # Registrar cada venta en base a los productos del carrito
    for item in carrito_items:
        producto = item.producto
        presentacion = item.presentacion
        cantidad = item.cantidad

        # Validar el inventario antes de registrar la venta usando el servicio
        if not ValidacionInventarioService.validar_inventario(producto, presentacion, cantidad):
            print(f"Inventario insuficiente para {producto.nombre} en la presentación {presentacion.nombre_presentacion}")
            return render(request, 'ventas/error.html', {'mensaje': f'Inventario insuficiente para {producto.nombre}.'})

        # Registrar la venta usando el servicio
        print(f"Registrando venta para el producto: {producto.nombre}, Cantidad: {cantidad}")
        VentaService.registrar_venta(turno_activo, producto, cantidad, factura, presentacion)
        print(f"Venta registrada para {producto.nombre}")

        # El ajuste del inventario se maneja dentro de VentaService.

    # Vaciar el carrito después de completar la venta
    carrito_items.delete()
    print("Carrito vaciado después de la venta.")

    return redirect('ventas:inicio_turno', turno_id=turno_activo.id)





@login_required
def cerrar_turno(request):
    usuario = request.user
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
                return redirect('dashboard')
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
    print(f"Término de búsqueda: {termino_busqueda}, Turno ID: {turno_id}")

    # Obtener el turno activo del usuario
    turno = get_object_or_404(RegistroTurno, id=turno_id, usuario=request.user)
    print(f"Turno activo encontrado: {turno.id} en la sucursal {turno.sucursal.nombre}")

    # Filtrar los productos por nombre y sucursal del turno activo
    inventarios = Inventario.objects.filter(sucursal=turno.sucursal, producto__nombre__icontains=termino_busqueda).select_related('producto')
    print(f"Productos encontrados: {inventarios.count()} para el término de búsqueda '{termino_busqueda}'")

    # Crear una lista de los productos filtrados
    productos_filtrados = []
    for inventario in inventarios:
        # Obtener la primera presentación asociada al producto
        presentacion = inventario.producto.presentaciones.first()
        if presentacion:
            productos_filtrados.append({
                'id': inventario.producto.id,
                'nombre': inventario.producto.nombre,
                'precio': presentacion.precio,  # Usar el precio de la presentación
                'stock': inventario.cantidad,
                'imagen': inventario.producto.image.url if inventario.producto.image else '/static/default_image.png'
            })
            print(f"Producto: {inventario.producto.nombre}, Precio: {presentacion.precio}, Stock: {inventario.cantidad}")
        else:
            print(f"Producto: {inventario.producto.nombre} no tiene presentaciones asociadas.")

    return JsonResponse({'productos': productos_filtrados})


