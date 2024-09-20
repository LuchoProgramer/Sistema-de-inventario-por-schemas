from ventas.models import Venta, CierreCaja
from inventarios.models import Producto
from empleados.models import RegistroTurno
from django.utils import timezone
from django.db import transaction
from ventas.models import Venta, Carrito
from facturacion.models import Factura
from inventarios.models import Inventario
from decimal import Decimal
from django.db import transaction


class VentaService:
    @staticmethod
    @transaction.atomic
    def registrar_venta(turno_activo, producto, cantidad, metodo_pago):
        # Verificar inventario
        inventario = producto.inventario_set.filter(sucursal=turno_activo.sucursal).first()
        if not inventario or inventario.cantidad < cantidad:
            raise ValueError(f"No hay suficiente inventario disponible. Solo hay {inventario.cantidad} unidades.")

        # Calcular total de la venta
        precio_unitario = producto.precio
        total_venta = cantidad * precio_unitario

        # Registrar la venta
        venta = Venta.objects.create(
            turno=turno_activo,
            sucursal=turno_activo.sucursal,
            empleado=turno_activo.empleado,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            total_venta=total_venta,
            metodo_pago=metodo_pago,
            fecha=timezone.now(),
        )

        # Actualizar el inventario
        inventario.cantidad -= cantidad
        inventario.save()

        return venta


class VentaService:
    @staticmethod
    @transaction.atomic
    def finalizar_venta(turno, metodo_pago):
        carrito_items = Carrito.objects.filter(turno=turno)
        if not carrito_items.exists():
            raise ValueError("El carrito está vacío. No se puede finalizar la venta.")

        total_venta = Decimal('0.00')
        total_sin_impuestos = Decimal('0.00')
        total_con_impuestos = Decimal('0.00')
        errores = []

        for item in carrito_items:
            inventario = item.producto.inventario_set.filter(sucursal=turno.sucursal).first()
            if not inventario or inventario.cantidad < item.cantidad:
                errores.append(f"No hay suficiente inventario para {item.producto.nombre}.")
            else:
                # Registrar la venta
                total_item = item.subtotal()  # El subtotal ya incluye el precio unitario * cantidad
                Venta.objects.create(
                    turno=turno,
                    sucursal=turno.sucursal,
                    empleado=turno.empleado,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio,
                    total_venta=total_item,
                    metodo_pago=metodo_pago
                )
                # Actualizar inventario
                inventario.cantidad -= item.cantidad
                inventario.save()

                total_sin_impuestos += total_item
                total_con_impuestos += total_item * Decimal('1.12')  # Ejemplo: con IVA 12%

        if errores:
            raise ValueError("\n".join(errores))

        # Crear la factura
        factura = Factura.objects.create(
            sucursal=turno.sucursal,
            cliente=turno.empleado.cliente,
            empleado=turno.empleado,
            total_sin_impuestos=total_sin_impuestos,
            total_con_impuestos=total_con_impuestos,
            estado='AUTORIZADA',
            turno=turno
        )

        carrito_items.delete()  # Vaciar el carrito después de completar la venta

        return factura
    

class TurnoService:
    @staticmethod
    @transaction.atomic
    def cerrar_turno(turno, cierre_form_data):
        # Guardar cierre de caja
        cierre_caja = CierreCaja.objects.create(
            empleado=turno.empleado,
            sucursal=turno.sucursal,
            fecha_cierre=timezone.now(),
            efectivo_total=cierre_form_data.get('efectivo_total'),  # Corregido a efectivo_total
            tarjeta_total=cierre_form_data.get('tarjeta_total'),  # Corregido a tarjeta_total
            transferencia_total=cierre_form_data.get('transferencia_total'),  # Corregido a transferencia_total
            salidas_caja=cierre_form_data.get('salidas_caja', 0),  # Añadido salidas_caja con valor por defecto
        )

        # Marcar el turno como cerrado
        turno.fin_turno = timezone.now()
        turno.save()

        return cierre_caja