from RegistroTurnos.models import RegistroTurno

def turno_context(request):
    # Inicializar turno activo y sucursal como None
    turno_activo = None
    sucursal_activa = None

    # Verificar si el usuario está autenticado
    if request.user.is_authenticated:
        # Intentar recuperar un registro de turno activo para el usuario actual
        turno_activo = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()
        if turno_activo:
            # Si hay un turno activo, asociar la sucursal del turno
            sucursal_activa = turno_activo.sucursal

    # Devolver el turno activo y la sucursal activa en el contexto
    return {'turno_activo': turno_activo, 'sucursal_activa': sucursal_activa}
