from decimal import Decimal
from .models import Factura, DetalleFactura
from inventarios.models import Inventario, MovimientoInventario
from django.core.exceptions import ValidationError
from .utils.xml_generator import generar_xml_para_sri
from .utils.clave_acceso import generar_clave_acceso
from django.db import transaction

def crear_factura(cliente, sucursal, empleado, carrito_items, metodo_pago):
    total_sin_impuestos = sum(item.subtotal() for item in carrito_items)
    total_con_impuestos = total_sin_impuestos * Decimal('1.12')  # Asumiendo 12% de IVA

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
                numero_autorizacion=secuencial,  # Usar el secuencial de la sucursal como número de autorización
                total_sin_impuestos=total_sin_impuestos,
                total_con_impuestos=total_con_impuestos,
                estado='EN_PROCESO',
                metodo_pago=metodo_pago  # Guardar el método de pago
            )

            # Crear los detalles de la factura
            for item in carrito_items:
                DetalleFactura.objects.create(
                    factura=factura,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio_venta,
                    subtotal=item.subtotal(),
                    descuento=0,
                    total=item.subtotal() * Decimal('1.12')
                )

                # Actualizar inventario
                inventario = Inventario.objects.select_for_update().get(
                    sucursal=sucursal,
                    producto=item.producto
                )
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

            xml_factura = generar_xml_para_sri(factura)

            return factura

    except ValidationError as e:
        print(f"Error al crear la factura: {e}")
        raise e
