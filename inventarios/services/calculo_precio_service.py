class CalculoPrecioService:

    @staticmethod
    def calcular_precio(presentacion, cantidad):
        """
        Calcula el precio correcto basado en la presentación seleccionada y la cantidad.
        No multiplica por unidades individuales si la presentación ya tiene un precio global.
        """
        print(f"Calculando precio para la presentación: {presentacion.nombre_presentacion}, Cantidad solicitada: {cantidad}")
        print(f"Precio por presentación: {presentacion.precio} (nombre presentación: {presentacion.nombre_presentacion})")

        if presentacion.nombre_presentacion == "Unidad":
            # Precio se calcula por unidad
            precio_total = presentacion.precio * cantidad
            print(f"Presentación 'Unidad' seleccionada. Precio unitario: {presentacion.precio}. Total calculado: {precio_total}")
        else:
            # Para "Media" o "Entera", usar el precio global de la presentación y multiplicar por la cantidad de paquetes
            precio_total = presentacion.precio * cantidad
            print(f"Presentación '{presentacion.nombre_presentacion}' seleccionada. Precio total por paquete: {presentacion.precio}. Total calculado: {precio_total} para {cantidad} paquetes.")

        print(f"Precio total final calculado: {precio_total} para {cantidad} presentaciones de {presentacion.nombre_presentacion}")

        return precio_total
