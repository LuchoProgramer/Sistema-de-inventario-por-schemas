from django.shortcuts import render, redirect, get_object_or_404
from .models import Factura, Cotizacion, Cliente, DetalleFactura, Impuesto, Pago   
from django.http import HttpResponse, FileResponse
from ventas.utils import obtener_carrito, vaciar_carrito
from RegistroTurnos.models import RegistroTurno
from django.utils import timezone
from django.core.exceptions import ValidationError
from .utils.xml_generator import generar_xml_para_sri
from inventarios.models import Inventario, MovimientoInventario
from django.db import transaction
from decimal import Decimal
from .services import crear_factura
from sucursales.models import Sucursal
from .forms import ImpuestoForm
import os
from django.conf import settings
from .pdf.factura_pdf import generar_pdf_factura
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from ventas.forms import MetodoPagoForm
from facturacion.services import obtener_o_crear_cliente, verificar_turno_activo, asignar_pagos_a_factura, generar_pdf_factura_y_guardar
from facturacion.services import crear_factura  # Si no lo tienes aún, importa la función que maneja la creación de facturas.


 
@transaction.atomic
def generar_cotizacion(request):
    if request.method == 'POST':
        try:
            # Obtener el cliente (si existe)
            cliente_id = request.POST.get('cliente_id')
            cliente = Cliente.objects.get(id=cliente_id) if cliente_id else None

            # Obtener los productos en el carrito del usuario
            carrito_items = obtener_carrito(request.user)
            if not carrito_items.exists():
                return JsonResponse({'error': 'El carrito está vacío. No se puede generar una cotización.'}, status=400)

            # Calcular los totales
            total_sin_impuestos = sum(item.subtotal() for item in carrito_items)
            total_con_impuestos = total_sin_impuestos * 1.12  # Asumiendo 12% de IVA

            # Crear la cotización
            cotizacion = Cotizacion.objects.create(
                sucursal=request.user.sucursal_actual,  # Suponiendo que la relación está en el User
                cliente=cliente,
                empleado=request.user,  # Usar directamente el User
                total_sin_impuestos=total_sin_impuestos,
                total_con_impuestos=total_con_impuestos,
                observaciones=request.POST.get('observaciones', '')
            )

            # Redirigir a la página de éxito
            return redirect('ventas:cotizacion_exitosa')

        except Cliente.DoesNotExist:
            logger.error("Cliente no encontrado.")
            return JsonResponse({'error': 'Cliente no encontrado.'}, status=400)
        except ValidationError as e:
            logger.error(f"Error en la validación: {e}")
            return JsonResponse({'error': e.messages}, status=400)
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'facturacion/generar_cotizacion.html')


from django.urls import reverse
from django.http import JsonResponse
from django.db import transaction
import logging
from ventas.services import VentaService
logger = logging.getLogger(__name__)



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

            # Verificar que el usuario tiene un turno activo
            usuario = request.user
            turno_activo = verificar_turno_activo(usuario)

            # Obtener la sucursal y el carrito
            sucursal = turno_activo.sucursal
            carrito_items = obtener_carrito(usuario)
            if not carrito_items.exists():
                return JsonResponse({'error': 'El carrito está vacío. No se puede generar una factura.'}, status=400)

            # Registrar la venta para cada producto en el carrito
            for item in carrito_items:
                # Registrar la venta en el sistema
                VentaService.registrar_venta(turno_activo, item.producto, item.cantidad, request.POST.get('metodo_pago', 'Efectivo'))
                print(f"Venta registrada para el producto {item.producto.nombre} con cantidad {item.cantidad}")

            # Obtener métodos y montos de pago del formulario
            metodos_pago = request.POST.getlist('metodos_pago')
            montos_pago = request.POST.getlist('montos_pago')

            if len(metodos_pago) != len(montos_pago):
                return JsonResponse({'error': 'Métodos de pago y montos no coinciden.'}, status=400)

            # Crear la factura y asociar los detalles del carrito
            factura = crear_factura(cliente, sucursal, usuario, carrito_items)

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
            logger.error(f"Error al generar la factura: {str(e)}")
            return JsonResponse({'error': 'Ocurrió un error al generar la factura.'}, status=500)

    else:
        # Si la solicitud es GET, obtener los detalles del carrito y el total de la factura
        carrito_items = obtener_carrito(request.user)
        total_factura = sum(item.subtotal() for item in carrito_items)

        return render(request, 'facturacion/generar_factura.html', {
            'clientes': Cliente.objects.all(),
            'total_factura': total_factura,
        })

   

def ver_pdf_factura(request, numero_autorizacion):
    ruta_pdf = os.path.join(settings.MEDIA_ROOT, f'factura_{numero_autorizacion}.pdf')
    
    if os.path.exists(ruta_pdf):
        try:
            return FileResponse(open(ruta_pdf, 'rb'), content_type='application/pdf')
        except Exception as e:
            logger.error(f"Error al abrir el PDF {ruta_pdf}: {e}")
            return HttpResponse("Error al intentar abrir el PDF.", status=500)
    else:
        logger.warning(f"El PDF factura_{numero_autorizacion}.pdf no se encontró en {settings.MEDIA_ROOT}")
        return HttpResponse("El PDF no se encuentra disponible.", status=404)
    


def actualizar_impuesto(request, impuesto_id):
    impuesto = get_object_or_404(Impuesto, id=impuesto_id)
    if request.method == 'POST':
        form = ImpuestoForm(request.POST, instance=impuesto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')  # O la vista que quieras redirigir
    else:
        form = ImpuestoForm(instance=impuesto)
    
    return render(request, 'facturacion/actualizar_impuesto.html', {'form': form})

def lista_impuestos(request):
    impuestos = Impuesto.objects.all()
    return render(request, 'facturacion/lista_impuestos.html', {'impuestos': impuestos})


def crear_impuesto(request):
    if request.method == 'POST':
        form = ImpuestoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('facturacion/lista_impuestos.html')
    else:
        form = ImpuestoForm()
    
    return render(request, 'facturacion/crear_impuesto.html', {'form': form})

def eliminar_impuesto(request, impuesto_id):
    impuesto = get_object_or_404(Impuesto, id=impuesto_id)
    impuesto.delete()
    return redirect('lista_impuestos')