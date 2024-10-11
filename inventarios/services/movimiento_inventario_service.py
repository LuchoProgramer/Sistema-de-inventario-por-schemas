from inventarios.models import Inventario, MovimientoInventario

class MovimientoInventarioService:

    @staticmethod
    def registrar_movimiento(producto, sucursal, tipo_movimiento, cantidad):
        """
        Registra un movimiento de inventario sin modificar las cantidades.
        """
        MovimientoInventario.objects.create(
            producto=producto,
            sucursal=sucursal,
            tipo_movimiento=tipo_movimiento,
            cantidad=cantidad
        )
        print(f"Movimiento de inventario registrado para el producto {producto.nombre}, cantidad ajustada: {cantidad}")
