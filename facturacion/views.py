from django.shortcuts import render, redirect
from .models import Factura, Cotizacion, Cliente, ComprobantePago, DetalleFactura
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


def generar_factura(request):
    if request.method == 'POST':
        empleado = request.user.empleado
        turno_activo = RegistroTurno.objects.filter(empleado=empleado, fin_turno__isnull=True).first()

        if not turno_activo:
            return render(request, 'facturacion/error.html', {'message': 'No tienes un turno activo. Por favor inicia un turno.'})

        sucursal = turno_activo.sucursal

        cliente_id = request.POST.get('cliente_id')
        if cliente_id:
            cliente = Cliente.objects.get(id=cliente_id)
        else:
            cliente = Cliente.objects.create(
                identificacion=request.POST.get('identificacion'),
                tipo_identificacion=request.POST.get('tipo_identificacion'),
                razon_social=request.POST.get('razon_social'),
                direccion=request.POST.get('direccion'),
                telefono=request.POST.get('telefono'),
                email=request.POST.get('email')
            )

        carrito_items = obtener_carrito(request.user)

        try:
            factura = crear_factura(cliente, sucursal, request.user.empleado, carrito_items)

            nombre_archivo = f"factura_{factura.numero_autorizacion}.pdf"
            ruta_pdf = os.path.join(settings.MEDIA_ROOT, nombre_archivo)
            generar_pdf_factura(factura, ruta_pdf)

            pdf_url = f"/media/{nombre_archivo}"
            redirect_url = reverse('ventas:inicio_turno')

            return JsonResponse({'pdf_url': pdf_url, 'redirect_url': redirect_url})
        
        except ValidationError as e:
            return render(request, 'facturacion/generar_factura.html', {'errors': e.messages, 'clientes': Cliente.objects.all()})

    return render(request, 'facturacion/generar_factura.html', {'clientes': Cliente.objects.all()})


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
