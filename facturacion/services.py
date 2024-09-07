from decimal import Decimal, ROUND_HALF_UP
from .models import Factura, DetalleFactura, Impuesto  # Asegúrate de importar el modelo Impuesto
from inventarios.models import Inventario, MovimientoInventario
from django.core.exceptions import ValidationError
from .utils.xml_generator import generar_xml_para_sri
from .utils.clave_acceso import generar_clave_acceso
from django.db import transaction

def crear_factura(cliente, sucursal, empleado, carrito_items):
    # Obtener el IVA activo
    iva = Impuesto.objects.filter(codigo_impuesto='2', activo=True).first()  # Código '2' para IVA

    if not iva:
        raise ValidationError("No se encontró un IVA activo en la base de datos")

    # Calcular el total sin impuestos y redondear a 2 decimales
    total_sin_impuestos = sum((item.subtotal() / (1 + (iva.porcentaje / Decimal(100)))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) for item in carrito_items)

    # Calcular el valor del IVA y redondear a 2 decimales
    valor_iva = sum(((item.subtotal() - (item.subtotal() / (1 + (iva.porcentaje / Decimal(100))))) for item in carrito_items))
    valor_iva = Decimal(valor_iva).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # El total con impuestos sigue siendo el subtotal de los productos, redondeado a 2 decimales
    total_con_impuestos = sum(item.subtotal().quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) for item in carrito_items)

    try:
        with transaction.atomic():
            # Incrementar el secuencial de la sucursal ANTES de crear la factura
            sucursal.incrementar_secuencial()
            secuencial = sucursal.secuencial_actual.zfill(9)

            # Crear la factura con el secuencial actual
            factura = Factura.objects.create(
                sucursal=sucursal,
                cliente=cliente,
                empleado=empleado,
                numero_autorizacion=secuencial,
                total_sin_impuestos=total_sin_impuestos,
                total_con_impuestos=total_con_impuestos,
                valor_iva=valor_iva,  # Guardar el valor del IVA redondeado
                estado='EN_PROCESO'
            )

            # Crear los detalles de la factura
            for item in carrito_items:
                # Verificar si hay suficiente stock en el inventario
                inventario = Inventario.objects.select_for_update().get(sucursal=sucursal, producto=item.producto)
                if inventario.cantidad < item.cantidad:
                    raise ValidationError(f"No hay suficiente stock para el producto: {item.producto.nombre}")

                # Calcular el subtotal sin impuestos y el IVA por cada ítem
                subtotal_sin_impuestos = (item.subtotal() / (1 + (iva.porcentaje / Decimal(100)))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                valor_iva_item = (item.subtotal() - subtotal_sin_impuestos).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                # Crear detalle de factura
                DetalleFactura.objects.create(
                    factura=factura,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio_venta,
                    subtotal=subtotal_sin_impuestos,  # Guardar el subtotal sin IVA
                    descuento=0,
                    total=item.subtotal().quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),  # El total sigue siendo el subtotal original que incluye IVA
                    valor_iva=valor_iva_item  # Guardar el IVA redondeado a dos decimales
                )

                # Descontar stock del inventario
                inventario.cantidad -= item.cantidad
                inventario.save()

                # Registrar movimiento de inventario
                MovimientoInventario.objects.create(
                    producto=item.producto,
                    sucursal=sucursal,
                    tipo_movimiento='VENTA',
                    cantidad=-item.cantidad
                )

            # Generar clave de acceso y el XML para SRI
            clave_acceso = generar_clave_acceso(
                fecha_emision=factura.fecha_emision.strftime('%d%m%Y'),
                tipo_comprobante='01',
                ruc=sucursal.ruc,
                ambiente='1',  # Ambiente de pruebas
                estab=sucursal.codigo_establecimiento,
                pto_emi=sucursal.punto_emision,
                secuencial=secuencial,
                tipo_emision='1'
            )

            # Generar el XML para la factura
            xml_factura = generar_xml_para_sri(factura)

            return factura

    except ValidationError as e:
        print(f"Error al crear la factura: {e}")
        raise e
