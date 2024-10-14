from decimal import Decimal, ROUND_HALF_UP
from .models import Factura, DetalleFactura, Impuesto  # Asegúrate de importar el modelo Impuesto
from inventarios.models import Inventario, MovimientoInventario
from django.core.exceptions import ValidationError
from .utils.xml_generator import generar_xml_para_sri
from .utils.clave_acceso import generar_clave_acceso
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from decimal import Decimal
from facturacion.models import Cliente, Pago
from RegistroTurnos.models import RegistroTurno
from facturacion.pdf.factura_pdf import generar_pdf_factura
import os
from django.conf import settings
from inventarios.services.validacion_inventario_service import ValidacionInventarioService
from inventarios.services.ajuste_inventario_service import AjusteInventarioService


def crear_factura(cliente, sucursal, usuario, carrito_items):
    print("Iniciando la creación de la factura...")

    # Obtener el IVA activo
    iva = Impuesto.objects.filter(codigo_impuesto='2', activo=True).first()
    if not iva:
        print("No se encontró un IVA activo.")
        raise ValidationError("No se encontró un IVA activo en la base de datos")

    total_sin_impuestos = Decimal('0.00')
    total_iva = Decimal('0.00')
    total_con_impuestos = Decimal('0.00')

    for item in carrito_items:
        print(f"Procesando producto {item.producto.nombre}...")

        presentacion = item.presentacion
        total_unidades_solicitadas = item.cantidad * presentacion.cantidad

        # Obtener el valor base e IVA del producto
        valor_base, valor_iva = item.producto.obtener_valor_base_iva(presentacion)

        subtotal_item = valor_base * total_unidades_solicitadas
        iva_item = valor_iva * total_unidades_solicitadas

        total_sin_impuestos += subtotal_item
        total_iva += iva_item
        total_con_impuestos += subtotal_item + iva_item

    try:
        with transaction.atomic():
            print("Iniciando transacción para crear la factura y los detalles...")
            sucursal.incrementar_secuencial()
            sucursal.save()

            # Generar número de autorización
            codigo_establecimiento = int(sucursal.codigo_establecimiento)
            punto_emision = int(sucursal.punto_emision)
            secuencial = f"{int(sucursal.secuencial_actual):09d}"
            numero_autorizacion = f"{codigo_establecimiento:03d} {punto_emision:03d} {secuencial}"

            # Crear la factura
            factura = Factura.objects.create(
                sucursal=sucursal,
                cliente=cliente,
                usuario=usuario,
                numero_autorizacion=numero_autorizacion,
                total_sin_impuestos=total_sin_impuestos.quantize(Decimal('0.01')),
                valor_iva=total_iva.quantize(Decimal('0.01')),
                total_con_impuestos=total_con_impuestos.quantize(Decimal('0.01')),
                estado='EN_PROCESO',
                es_cotizacion=False
            )
            print(f"Factura creada con número de autorización {factura.numero_autorizacion}...")

            # Crear los detalles de la factura y actualizar el inventario
            for item in carrito_items:
                presentacion = item.presentacion
                total_unidades_solicitadas = item.cantidad * presentacion.cantidad

                # Calcular valores de detalle
                valor_base, valor_iva = item.producto.obtener_valor_base_iva(presentacion)
                subtotal_item = valor_base * total_unidades_solicitadas
                iva_item = valor_iva * total_unidades_solicitadas
                total_item = subtotal_item + iva_item

                print(f"Valores de detalle: cantidad={total_unidades_solicitadas}, precio_unitario={presentacion.precio}, subtotal={subtotal_item}, total={total_item}")

                # Crear el detalle de la factura
                detalle = DetalleFactura.objects.create(
                    factura=factura,
                    producto=item.producto,
                    presentacion=presentacion,
                    cantidad=total_unidades_solicitadas,
                    precio_unitario=presentacion.precio,
                    subtotal=subtotal_item.quantize(Decimal('0.01')),
                    descuento=0,
                    total=total_item.quantize(Decimal('0.01')),
                    valor_iva=iva_item.quantize(Decimal('0.01'))
                )
                print(f"Detalle creado: {detalle}")

                # Validar y ajustar inventario usando los servicios especializados
                if not ValidacionInventarioService.validar_inventario(item.producto, presentacion, item.cantidad):
                    print(f"No hay suficiente inventario para {item.producto.nombre}.")
                    raise ValidationError(f"No hay suficiente inventario disponible para {item.producto.nombre}.")

                # Ajuste del inventario a través del servicio de movimiento
                AjusteInventarioService.ajustar_inventario(item.producto, presentacion, item.cantidad)

            if not factura.detalles.exists():
                print("Error: La factura no tiene detalles asociados.")
                raise ValidationError("La factura no tiene detalles asociados.")
            
            print(f"Factura {factura.numero_autorizacion} completada con {factura.detalles.count()} detalles.")
            return factura

    except Exception as e:
        print(f"Error general en la transacción: {e}")
        raise e






# Función para validar o crear un cliente
def obtener_o_crear_cliente(cliente_id, identificacion, data_cliente):
    try:
        if cliente_id:
            cliente = Cliente.objects.get(id=cliente_id)
        else:
            cliente, created = Cliente.objects.get_or_create(
                identificacion=identificacion,
                defaults=data_cliente
            )
            if not created and not cliente.razon_social:
                raise ValidationError("Cliente incompleto. Por favor revisa los datos ingresados.")
        return cliente
    except Cliente.DoesNotExist:
        raise ValidationError("Cliente no encontrado.")

# Función para verificar si el usuario tiene un turno activo
def verificar_turno_activo(usuario):
    turno_activo = RegistroTurno.objects.filter(usuario=usuario, fin_turno__isnull=True).first()
    if not turno_activo:
        raise ValidationError("No tienes un turno activo. Por favor inicia un turno.")
    return turno_activo

# Función para asignar los métodos de pago
def asignar_pagos_a_factura(factura, metodos_pago, montos_pago):
    metodo_descripciones = {
        '01': 'Efectivo',
        '16': 'Tarjeta de Débito',
        '19': 'Tarjeta de Crédito',
        '20': 'Transferencias',
        '17': 'Dinero Electrónico'
    }

    for metodo_pago, monto_pago in zip(metodos_pago, montos_pago):
        descripcion = metodo_descripciones.get(metodo_pago, 'Método de Pago Desconocido')
        Pago.objects.create(
            factura=factura,
            codigo_sri=metodo_pago,
            total=Decimal(monto_pago),
            descripcion=f"Pago con {descripcion}"
        )


# Función para generar el PDF de la factura
def generar_pdf_factura_y_guardar(factura):
    nombre_archivo = f"factura_{factura.numero_autorizacion}.pdf"
    ruta_pdf = os.path.join(settings.MEDIA_ROOT, nombre_archivo)
    generar_pdf_factura(factura, ruta_pdf)
    return f"/media/{nombre_archivo}"