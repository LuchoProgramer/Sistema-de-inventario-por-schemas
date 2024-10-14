from .models import Carrito
from RegistroTurnos.models import RegistroTurno
import logging

logger = logging.getLogger(__name__)

def obtener_turno_activo(usuario):
    """
    Busca el turno activo para el usuario.

    Args:
        usuario (User): El usuario para el cual se desea buscar el turno activo.

    Returns:
        RegistroTurno or None: El turno activo si existe, None en caso contrario.
    """
    try:
        # Ahora buscamos el turno directamente con el usuario
        return RegistroTurno.objects.filter(usuario=usuario, fin_turno__isnull=True).first()
    except Exception as e:
        logger.error(f"Error al obtener el turno activo: {e}")
        return None


def obtener_carrito(usuario):
    """
    Obtiene el carrito asociado al usuario actual, basado en su turno activo.
    """
    turno_activo = obtener_turno_activo(usuario)
    print(f"Turno activo para el usuario {usuario.username}: {turno_activo}")

    if turno_activo:
        carrito_items = Carrito.objects.filter(turno=turno_activo)
        print(f"Productos en el carrito para el turno {turno_activo.id}: {carrito_items.count()}")
        return carrito_items
    else:
        print("No hay turno activo para este usuario.")
        return Carrito.objects.none()


def vaciar_carrito(usuario):
    """
    Vacía el carrito asociado al usuario actual después de procesar la factura.

    Args:
        usuario (User): El usuario actual.

    """
    turno_activo = obtener_turno_activo(usuario)

    if turno_activo:
        carrito_items = Carrito.objects.filter(turno=turno_activo)
        carrito_items.delete()
    else:
        logger.warning(f"Intento de vaciar carrito sin turno activo para el usuario: {usuario}")


def obtener_total_items_en_carrito(request):
    """
    Obtiene el número total de ítems en el carrito de un usuario.
    """
    # Suponiendo que usas sesiones para almacenar los datos del carrito
    cart = request.session.get('cart', {})
    print("Contenido del carrito en la sesión:", cart)  # Log para depuración
    total_items = sum(item['quantity'] for item in cart.values())
    return total_items