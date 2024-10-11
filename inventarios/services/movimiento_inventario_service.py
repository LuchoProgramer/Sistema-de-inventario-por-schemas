from inventarios.models import Inventario, MovimientoInventario

class MovimientoInventarioService:

    @staticmethod
    def ajustar_inventario(producto, presentacion, cantidad):
        """
        Ajusta el inventario restando la cantidad especificada del inventario actual
        y registra el movimiento de inventario.
        """
        # Obtener el inventario para el producto y la sucursal de la presentación
        inventario = Inventario.objects.filter(producto=producto, sucursal=presentacion.sucursal).first()

        if not inventario:
            raise ValueError(f"No se encontró inventario para el producto {producto.nombre} en la sucursal {presentacion.sucursal.nombre}.")

        # Calcular las unidades a descontar
        unidades_a_descontar = presentacion.cantidad * cantidad

        if inventario.cantidad < unidades_a_descontar:
            raise ValueError(f"Inventario insuficiente: se requieren {unidades_a_descontar} unidades, pero solo hay {inventario.cantidad} disponibles.")

        # Actualizar el inventario
        inventario.cantidad -= unidades_a_descontar
        inventario.save()
        print(f"Inventario actualizado para el producto {producto.nombre}. Cantidad restante: {inventario.cantidad}")

        # Registrar el movimiento de inventario
        MovimientoInventario.objects.create(
            producto=producto,
            sucursal=presentacion.sucursal,
            tipo_movimiento='VENTA',
            cantidad=-unidades_a_descontar,
        )
        print(f"Movimiento de inventario registrado para el producto {producto.nombre}, cantidad ajustada: {unidades_a_descontar}")
