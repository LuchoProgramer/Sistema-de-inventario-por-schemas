from .models import Carrito

def obtener_carrito(usuario):
    """
    Obtiene el carrito asociado al usuario actual.
    """
    return Carrito.objects.filter(turno__empleado__usuario=usuario)
