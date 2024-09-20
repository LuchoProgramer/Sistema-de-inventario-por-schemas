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

    Args:
        usuario (User): El usuario actual.

    Returns:
        QuerySet: Un queryset del modelo Carrito relacionado con el turno activo.
    """
    turno_activo = obtener_turno_activo(usuario)

    if turno_activo:
        return Carrito.objects.filter(turno=turno_activo)
    else:
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

