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
    def registrar_venta(turno_activo, producto, cantidad, factura):
        print("Iniciando el registro de la venta...")

        # Calcular el total de la venta
        precio_unitario = producto.precio_venta
        total_venta = cantidad * precio_unitario
        print(f"Total de la venta calculado: {total_venta} para {cantidad} unidades de {producto.nombre}")

        # Registrar la venta, incluyendo la factura
        try:
            venta = Venta.objects.create(
                turno=turno_activo,
                sucursal=turno_activo.sucursal,
                usuario=turno_activo.usuario,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                total_venta=total_venta,
                factura=factura,  # Aquí pasamos la factura
                fecha=timezone.now(),  # Registrar la fecha actual
            )
            print(f"Venta registrada exitosamente con ID: {venta.id} para el producto {producto.nombre}")
        except Exception as e:
            print(f"Error al registrar la venta: {str(e)}")
            raise ValueError(f"Error al registrar la venta: {str(e)}")

        return venta




    @staticmethod
    @transaction.atomic
    def finalizar_venta(turno):
        print(f"Iniciando el proceso de finalizar venta para el turno: {turno.id}")
        carrito_items = Carrito.objects.filter(turno=turno)
        print(f"Carrito para el turno {turno.id}, productos en el carrito: {carrito_items.count()}")
        
        if not carrito_items.exists():
            print("El carrito está vacío. No se puede finalizar la venta.")
            raise ValueError("El carrito está vacío. No se puede finalizar la venta.")
        
        print("Procesando el carrito...")

        total_sin_impuestos = Decimal('0.00')
        total_con_impuestos = Decimal('0.00')
        errores = []

        for item in carrito_items:
            print(f"Procesando producto: {item.producto.nombre}, cantidad: {item.cantidad}")
            inventario = item.producto.inventario_set.filter(sucursal=turno.sucursal).first()
            if not inventario or inventario.cantidad < item.cantidad:
                print(f"Error: No hay suficiente inventario para {item.producto.nombre}.")
                errores.append(f"No hay suficiente inventario para {item.producto.nombre}.")
            else:
                try:
                    # Registrar la venta sin metodo_pago
                    total_item = item.subtotal()  # El subtotal ya incluye el precio unitario * cantidad
                    nueva_venta = Venta.objects.create(
                        turno=turno,
                        sucursal=turno.sucursal,
                        usuario=turno.usuario,  # Cambiado de empleado a usuario
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio_unitario=item.producto.precio_venta,
                        total_venta=total_item
                    )
                    print(f"Venta creada: {nueva_venta.id} para el producto: {item.producto.nombre}")
                except Exception as e:
                    print(f"Error al crear la venta para {item.producto.nombre}: {str(e)}")
                    errores.append(f"No se pudo registrar la venta para {item.producto.nombre}")

                # Actualizar inventario
                inventario.cantidad -= item.cantidad
                inventario.save()
                print(f"Inventario actualizado para {item.producto.nombre}. Nueva cantidad: {inventario.cantidad}")

                total_sin_impuestos += total_item
                total_con_impuestos += total_item * Decimal('1.12')  # Ejemplo con IVA 12%

        if errores:
            print(f"Errores al registrar ventas: {'; '.join(errores)}")
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
        print(f"Factura creada exitosamente con ID: {factura.id} para el turno {turno.id}")

        carrito_items.delete()  # Vaciar el carrito después de completar la venta
        print("Carrito vaciado después de la venta.")

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
