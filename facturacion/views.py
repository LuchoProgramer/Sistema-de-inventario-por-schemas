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
from decimal import Decimal

def generar_factura(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        identificacion = request.POST.get('identificacion')

        # Validar que se ha seleccionado un cliente o proporcionado los datos de uno nuevo
        if not cliente_id and not identificacion:
            return JsonResponse({'error': 'Debes seleccionar un cliente o ingresar los datos de un nuevo cliente.'}, status=400)

        empleado = request.user.empleado
        turno_activo = RegistroTurno.objects.filter(empleado=empleado, fin_turno__isnull=True).first()

        if not turno_activo:
            return JsonResponse({'error': 'No tienes un turno activo. Por favor inicia un turno.'}, status=400)

        sucursal = turno_activo.sucursal

        # Verificar si el cliente ya existe o crear uno nuevo
        try:
            if cliente_id:
                cliente = Cliente.objects.get(id=cliente_id)
            else:
                cliente, created = Cliente.objects.get_or_create(
                    identificacion=identificacion,
                    defaults={
                        'tipo_identificacion': request.POST.get('tipo_identificacion'),
                        'razon_social': request.POST.get('razon_social'),
                        'direccion': request.POST.get('direccion'),
                        'telefono': request.POST.get('telefono'),
                        'email': request.POST.get('email')
                    }
                )
                # Si el cliente ya existía pero no tiene todos los campos completos
                if not created and not cliente.razon_social:
                    return JsonResponse({'error': 'Cliente incompleto. Por favor revisa los datos ingresados.'}, status=400)
        except Cliente.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado.'}, status=400)

        # Obtener el carrito de compras
        carrito_items = obtener_carrito(request.user)
        if not carrito_items.exists():
            return JsonResponse({'error': 'El carrito está vacío. No se puede generar una factura.'}, status=400)

        # Capturar los métodos de pago y montos desde el formulario
        metodos_pago = request.POST.getlist('metodos_pago')
        montos_pago = request.POST.getlist('montos_pago')

        # Descripciones para los métodos de pago
        metodo_descripciones = {
            '01': 'Efectivo',
            '16': 'Tarjeta de Débito',
            '19': 'Tarjeta de Crédito',
            '20': 'Transferencias',
            '17': 'Dinero Electrónico'
        }

        try:
            with transaction.atomic():
                # Crear la factura
                factura = crear_factura(cliente, sucursal, empleado, carrito_items)

                # Asignar los pagos a la factura
                for metodo_pago, monto_pago in zip(metodos_pago, montos_pago):
                    descripcion = metodo_descripciones.get(metodo_pago, 'Método de Pago Desconocido')
                    Pago.objects.create(
                        factura=factura,
                        codigo_sri=metodo_pago,
                        total=Decimal(monto_pago),
                        descripcion=f"Pago con {descripcion}"
                    )

                # Generar PDF de la factura
                nombre_archivo = f"factura_{factura.numero_autorizacion}.pdf"
                ruta_pdf = os.path.join(settings.MEDIA_ROOT, nombre_archivo)
                generar_pdf_factura(factura, ruta_pdf)

                # Vaciar el carrito después de generar la factura
                carrito_items.delete()

                # URLs de respuesta
                pdf_url = f"/media/{nombre_archivo}"
                # Aquí pasamos el turno_id al redirigir
                redirect_url = reverse('ventas:inicio_turno', args=[turno_activo.id])

                return JsonResponse({'pdf_url': pdf_url, 'redirect_url': redirect_url})

        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=400)

    # Si el método es GET, cargamos la página con los datos del carrito
    else:
        carrito_items = obtener_carrito(request.user)

        # Calcular el total de la factura
        total_factura = sum(item.subtotal() for item in carrito_items)

        return render(request, 'facturacion/generar_factura.html', {
            'clientes': Cliente.objects.all(),
            'total_factura': total_factura,  # Pasar el total al template
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
