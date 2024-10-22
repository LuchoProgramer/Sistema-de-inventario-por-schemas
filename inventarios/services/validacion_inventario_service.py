from inventarios.models import Inventario

class ValidacionInventarioService:

    @staticmethod
    def validar_inventario(producto, presentacion, cantidad):
        """
        Valida si hay suficientes unidades en el inventario para la presentación seleccionada.
        """
        unidades_requeridas = presentacion.cantidad * cantidad
        inventario = Inventario.objects.filter(producto=producto, sucursal=presentacion.sucursal).first()

        if not inventario:
            print(f"No se encontró inventario para el producto {producto.nombre} en la sucursal {presentacion.sucursal.nombre}.")
            return False

        if inventario.cantidad < unidades_requeridas:
            print(f"Inventario insuficiente: Se requieren {unidades_requeridas}, pero solo hay {inventario.cantidad} disponibles.")
            return False

        return True


    @staticmethod
    def validar_stock_disponible(producto, cantidad):
        """
        Valida si hay suficiente inventario disponible para un producto específico.
        """
        inventario = Inventario.objects.filter(producto=producto).first()

        if not inventario:
            print(f"No se encontró inventario para el producto {producto.nombre}.")
            return False

        if inventario.cantidad < cantidad:
            print(f"Stock insuficiente: Se requieren {cantidad} unidades, pero solo hay {inventario.cantidad} disponibles.")
            return False

        return True
