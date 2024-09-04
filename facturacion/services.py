from django.db import transaction
from decimal import Decimal
from .models import Factura, DetalleFactura
from inventarios.models import Inventario, MovimientoInventario
from django.core.exceptions import ValidationError
from .utils.xml_generator import generar_xml_para_sri
from .utils.clave_acceso import generar_clave_acceso
from django.utils import timezone

def generar_numero_autorizacion():
    # Genera un número de autorización único basado en el timestamp actual
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')  # Incluye microsegundos para mayor unicidad
    numero_autorizacion = f'{timestamp}'
    return numero_autorizacion

def crear_factura(cliente, sucursal, empleado, carrito_items):
    print("Llamando a crear_factura...")
    total_sin_impuestos = sum(item.subtotal() for item in carrito_items)
    total_con_impuestos = total_sin_impuestos * Decimal('1.12')  # Asumiendo 12% de IVA

    try:
        with transaction.atomic():
            # Generar un número de autorización único
            numero_autorizacion = generar_numero_autorizacion()
            factura = Factura.objects.create(
                sucursal=sucursal,
                cliente=cliente,
                empleado=empleado,
                numero_autorizacion=numero_autorizacion,
                total_sin_impuestos=total_sin_impuestos,
                total_con_impuestos=total_con_impuestos,
                estado='EN_PROCESO'
            )

            # Verificación de la factura creada
            factura.refresh_from_db()
            print(f"Fecha de emisión: {factura.fecha_emision}")  # Verifica la fecha de emisión
            print(f"Sucursal: {factura.sucursal}")
            print(f"Cliente: {factura.cliente}")
            print(f"Empleado: {factura.empleado}")
            print(f"Número de autorización: {factura.numero_autorizacion}")

            for item in carrito_items:
                # Detalles adicionales de depuración
                print(f"Producto: {item.producto.nombre}, Cantidad: {item.cantidad}")

                DetalleFactura.objects.create(
                    factura=factura,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio_venta,
                    subtotal=item.subtotal(),
                    descuento=0,
                    total=item.subtotal() * Decimal('1.12')
                )

                inventario = Inventario.objects.select_for_update().get(
                    sucursal=sucursal,
                    producto=item.producto
                )
                inventario.cantidad -= item.cantidad
                inventario.save()

                MovimientoInventario.objects.create(
                    producto=item.producto,
                    sucursal=sucursal,
                    tipo_movimiento='VENTA',
                    cantidad=-item.cantidad
                )

            # Verifica que estab y pto_emi no sean None
            if sucursal.codigo_establecimiento is None or sucursal.punto_emision is None:
                raise ValueError("El código de establecimiento o punto de emisión no está definido en la sucursal.")

            # Asignar valores predeterminados si es necesario
            estab = sucursal.codigo_establecimiento if sucursal.codigo_establecimiento else "001"
            pto_emi = sucursal.punto_emision if sucursal.punto_emision else "001"

            # Continuar con la generación de la clave de acceso
            clave_acceso = generar_clave_acceso(
                fecha_emision=factura.fecha_emision.strftime('%d%m%Y'),
                tipo_comprobante='01',
                ruc=sucursal.ruc,
                ambiente='1',
                estab=estab,
                pto_emi=pto_emi,
                secuencial=factura.numero_autorizacion,
                tipo_emision='1'
            )

            xml_factura = generar_xml_para_sri(factura)
            print(f"XML Factura Generado: {xml_factura[:500]}")  # Muestra los primeros 500 caracteres del XML generado

            return factura

    except ValidationError as e:
        print(f"Error al crear la factura: {e}")
        raise e
