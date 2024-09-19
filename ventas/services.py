from ventas.models import Venta
from inventarios.models import Producto
from empleados.models import RegistroTurno
from django.utils import timezone
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
            empleado=turno_activo.empleado.usuario,
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
