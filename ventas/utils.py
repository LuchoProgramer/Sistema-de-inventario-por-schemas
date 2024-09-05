from .models import Carrito, RegistroTurno
from empleados.models import Empleado

def obtener_carrito(usuario):
    """
    Obtiene el carrito asociado al usuario actual.
    """
    try:
        # Buscar el empleado correspondiente al usuario
        empleado = Empleado.objects.get(usuario=usuario)
        
        # Buscar el turno activo para ese empleado
        turno_activo = RegistroTurno.objects.filter(empleado=empleado, fin_turno__isnull=True).first()

        if turno_activo:
            # Obtener los elementos del carrito asociados con el turno activo
            return Carrito.objects.filter(turno=turno_activo)
        
    except Empleado.DoesNotExist:
        # Si no existe el empleado o turno, retornar un queryset vacío
        return Carrito.objects.none()


def vaciar_carrito(usuario):
    """
    Vacia el carrito asociado al usuario actual después de procesar la factura.
    """
    try:
        # Buscar el empleado correspondiente al usuario
        empleado = Empleado.objects.get(usuario=usuario)
        
        # Buscar el turno activo para ese empleado
        turno_activo = RegistroTurno.objects.filter(empleado=empleado, fin_turno__isnull=True).first()
        
        if turno_activo:
            # Obtener todos los elementos del carrito asociados con el turno activo
            carrito_items = Carrito.objects.filter(turno=turno_activo)
            
            # Eliminar los elementos del carrito
            carrito_items.delete()

    except Empleado.DoesNotExist:
        # Si el empleado no existe, no se hace nada
        pass
