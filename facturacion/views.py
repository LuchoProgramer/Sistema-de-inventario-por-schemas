from django.shortcuts import render, redirect
from .models import Factura, Cotizacion, Cliente, ComprobantePago, DetalleFactura, Impuesto, Pago   
from django.http import HttpResponse, FileResponse
from ventas.utils import obtener_carrito, vaciar_carrito
from empleados.models import RegistroTurno
from django.utils import timezone
from django.core.exceptions import ValidationError
from .utils.xml_generator import generar_xml_para_sri
from inventarios.models import Inventario, MovimientoInventario
from django.db import transaction
from decimal import Decimal
from .services import crear_factura
from sucursales.models import Sucursal
import os
from django.conf import settings
from .pdf.factura_pdf import generar_pdf_factura
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from ventas.forms import MetodoPagoForm
from facturacion.services import obtener_o_crear_cliente, verificar_turno_activo, asignar_pagos_a_factura, generar_pdf_factura_y_guardar
from facturacion.services import crear_factura  # Si no lo tienes aún, importa la función que maneja la creación de facturas.


 
def generar_cotizacion(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        cliente = Cliente.objects.get(id=cliente_id) if cliente_id else None

        carrito_items = obtener_carrito(request.user)

        total_sin_impuestos = sum(item.subtotal for item in carrito_items)
        total_con_impuestos = total_sin_impuestos * 1.12  # Asumiendo 12% de IVA

        cotizacion = Cotizacion.objects.create(
            sucursal=request.user.empleado.sucursal_actual,
            cliente=cliente,
            empleado=request.user.empleado,
            total_sin_impuestos=total_sin_impuestos,
            total_con_impuestos=total_con_impuestos,
            observaciones=request.POST.get('observaciones', '')
        )

        return redirect('ventas:cotizacion_exitosa')

    return render(request, 'facturacion/generar_cotizacion.html')


from django.urls import reverse
from django.http import JsonResponse
from django.db import transaction


@transaction.atomic
def generar_factura(request):
    if request.method == 'POST':
        # Datos del cliente proporcionados por la solicitud POST
        cliente_id = request.POST.get('cliente_id')
        identificacion = request.POST.get('identificacion')

        if not cliente_id and not identificacion:
            return JsonResponse({'error': 'Debes seleccionar un cliente o ingresar los datos de un nuevo cliente.'}, status=400)

        try:
            data_cliente = {
                'tipo_identificacion': request.POST.get('tipo_identificacion'),
                'razon_social': request.POST.get('razon_social'),
                'direccion': request.POST.get('direccion'),
                'telefono': request.POST.get('telefono'),
                'email': request.POST.get('email')
            }

            # Validar o crear el cliente
            cliente = obtener_o_crear_cliente(cliente_id, identificacion, data_cliente)

            # Verificar que el empleado tiene un turno activo
            empleado = request.user.empleado
            turno_activo = verificar_turno_activo(empleado)

            # Obtener la sucursal y el carrito
            sucursal = turno_activo.sucursal
            carrito_items = obtener_carrito(request.user)
            if not carrito_items.exists():
                return JsonResponse({'error': 'El carrito está vacío. No se puede generar una factura.'}, status=400)

            # Obtener métodos y montos de pago del formulario
            metodos_pago = request.POST.getlist('metodos_pago')
            montos_pago = request.POST.getlist('montos_pago')
            print(f"Métodos de pago: {metodos_pago}, Montos de pago: {montos_pago}")

            # Crear la factura y asociar los detalles del carrito
            factura = crear_factura(cliente, sucursal, empleado, carrito_items)

            # Verificar si la factura tiene detalles asociados
            detalles = factura.detalles.all()
            if not detalles.exists():
                return JsonResponse({'error': 'La factura no tiene detalles asociados.'}, status=400)

            # Asignar los pagos a la factura
            asignar_pagos_a_factura(factura, metodos_pago, montos_pago)

            # Generar el PDF de la factura y guardarlo
            pdf_url = generar_pdf_factura_y_guardar(factura)

            # Eliminar los artículos del carrito después de generar la factura
            carrito_items.delete()

            # Redirigir al turno activo
            redirect_url = reverse('ventas:inicio_turno', args=[turno_activo.id])
            return JsonResponse({'pdf_url': pdf_url, 'redirect_url': redirect_url})

        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        # Si la solicitud es GET, obtener los detalles del carrito y el total de la factura
        carrito_items = obtener_carrito(request.user)
        total_factura = sum(item.subtotal() for item in carrito_items)

        return render(request, 'facturacion/generar_factura.html', {
            'clientes': Cliente.objects.all(),
            'total_factura': total_factura,
        })
    

def generar_comprobante_pago(request):
    if request.method == 'POST':
        carrito_items = obtener_carrito(request.user)
        total = sum(item.subtotal for item in carrito_items)

        # Generar un número de autorización único
        numero_autorizacion = f"CP-{request.user.id}-{int(timezone.now().timestamp())}"

        comprobante_pago = ComprobantePago.objects.create(
            sucursal=request.user.empleado.sucursal_actual,
            cliente=request.POST.get('cliente', 'Consumidor Final'),
            empleado=request.user.empleado,
            numero_autorizacion=numero_autorizacion,
            total=total,
            observaciones=request.POST.get('observaciones', '')
        )

        # Actualizar el inventario aquí si es necesario
        for item in carrito_items:
            # Lógica para reducir el inventario
            item.producto.reducir_inventario(item.cantidad)
            item.producto.save()

        return HttpResponse(f"Comprobante de Pago #{comprobante_pago.numero_autorizacion} generado correctamente.")
    
    return render(request, 'facturacion/generar_comprobante_pago.html')

def factura_exitosa(request):
    return render(request, 'facturacion/factura_exitosa.html')

def error_view(request, message):
    return render(request, 'facturacion/error.html', {'message': message})

def ver_pdf_factura(request, numero_autorizacion):
    ruta_pdf = os.path.join(settings.MEDIA_ROOT, f'factura_{numero_autorizacion}.pdf')
    if os.path.exists(ruta_pdf):
        return FileResponse(open(ruta_pdf, 'rb'), content_type='application/pdf')
    else:
        return HttpResponse("El PDF no se encuentra disponible.", status=404)
