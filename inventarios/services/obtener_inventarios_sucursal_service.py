from inventarios.models import Inventario

class ObtenerInventariosSucursalService:

    @staticmethod
    def obtener_inventarios(sucursal):
        """
        Obtiene los inventarios de una sucursal y carga las presentaciones disponibles para cada producto.
        """
        inventarios = Inventario.objects.filter(sucursal=sucursal).select_related('producto__categoria')

        # Añadir las presentaciones de cada producto sin asignarlas
        for inventario in inventarios:
            presentaciones = inventario.producto.presentaciones.all()  # Accedemos sin reasignar
            print(f"Producto: {inventario.producto.nombre}, Presentaciones: {[p.nombre_presentacion for p in presentaciones]}")

        return inventarios
