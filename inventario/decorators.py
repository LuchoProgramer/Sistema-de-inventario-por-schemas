from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from RegistroTurnos.models import RegistroTurno
from functools import wraps

def empleado_o_admin_con_turno_y_sucursal_required(view_func):
    """
    Decorador que permite acceso solo a empleados o administradores
    con un turno activo en la sucursal correcta. Los superusuarios tienen acceso total.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Permitir acceso inmediato si es superusuario
        if request.user.is_superuser:
            print(f"{request.user.username} es superusuario, acceso permitido.")
            return view_func(request, *args, **kwargs)

        # Verificar si el usuario tiene un turno activo
        turno_activo = RegistroTurno.objects.filter(
            usuario=request.user, fin_turno__isnull=True
        ).first()

        if not turno_activo:
            print("No tienes un turno activo.")
            raise PermissionDenied("No tienes un turno activo.")

        # Verificar si pertenece al grupo 'Empleados' o 'Administrador'
        es_empleado_o_admin = request.user.groups.filter(
            name__in=['Empleados', 'Administrador']
        ).exists()

        print(f"¿Es empleado o admin?: {es_empleado_o_admin}")

        # Verificar que se reciba correctamente 'sucursal_id'
        sucursal_id = request.GET.get('sucursal_id')
        if not sucursal_id:
            print("No se proporcionó sucursal_id en la solicitud.")
            raise PermissionDenied("Acceso denegado: No se proporcionó sucursal_id.")

        # Asegurar que la comparación sea entre enteros
        try:
            sucursal_id = int(sucursal_id)
        except ValueError:
            print("sucursal_id no es un número válido.")
            raise PermissionDenied("Acceso denegado: sucursal_id inválido.")

        print(f"sucursal_id recibido: {sucursal_id}")
        print(f"Sucursal del turno: {turno_activo.sucursal.id}")

        if sucursal_id != turno_activo.sucursal.id:
            print("Sucursal incorrecta.")
            raise PermissionDenied("Acceso denegado: Sucursal incorrecta.")

        # Si todo está correcto, continuar con la vista
        return view_func(request, *args, **kwargs)

    return _wrapped_view
