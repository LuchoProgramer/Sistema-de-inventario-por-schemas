from ventas.models import Venta, CierreCaja, Carrito
from inventarios.models import Producto, Inventario
from RegistroTurnos.models import RegistroTurno
from facturacion.models import Factura
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

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
            usuario=turno_activo.usuario,  # Cambiado de empleado a usuario
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
                    usuario=turno.usuario,  # Cambiado de empleado a usuario
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
            cliente=turno.usuario.cliente,  # Cambiado de empleado.cliente a usuario.cliente
            usuario=turno.usuario,  # Cambiado de empleado a usuario
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
        try:
            cierre_caja = CierreCaja.objects.create(
                usuario=turno.usuario,
                sucursal=turno.sucursal,
                fecha_cierre=timezone.now(),
                efectivo_total=cierre_form_data.get('efectivo_total'),
                tarjeta_total=cierre_form_data.get('tarjeta_total'),
                transferencia_total=cierre_form_data.get('transferencia_total'),
                salidas_caja=cierre_form_data.get('salidas_caja', 0),
            )
            turno.fin_turno = timezone.now()
            turno.save()

            return cierre_caja

        except Exception as e:
            raise ValueError(f"Error al cerrar el turno: {str(e)}")
