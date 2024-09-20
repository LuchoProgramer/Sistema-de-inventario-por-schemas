from django.shortcuts import render
from .services import generar_reporte_ventas_por_turno
from RegistroTurnos.models import RegistroTurno
from django.contrib.auth.models import User

from django.shortcuts import render, get_object_or_404
from .services import generar_reporte_ventas_por_turno
from RegistroTurnos.models import RegistroTurno

def reporte_ventas_por_turno(request):
    turno_id = request.GET.get('turno_id')
    
    # Validar si se ha proporcionado un turno_id
    if not turno_id:
        context = {'error': 'No se ha proporcionado un ID de turno válido.'}
        return render(request, 'reportes/reporte_ventas.html', context)

    # Validar que el turno exista
    turno = get_object_or_404(RegistroTurno, id=turno_id)
    
    # Generar el reporte de ventas
    ventas, total_ventas = generar_reporte_ventas_por_turno(turno_id)
    
    context = {
        'ventas': ventas,
        'total_ventas': total_ventas,
        'turno': turno,
    }
    return render(request, 'reportes/reporte_ventas.html', context)



def seleccionar_turno_por_fechas(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    user_id = request.GET.get('user_id')  # Cambiado de empleado_id a user_id

    # Validar que las fechas son válidas
    if not fecha_inicio or not fecha_fin:
        context = {'error': 'Debes proporcionar ambas fechas: inicio y fin.'}
        return render(request, 'reportes/seleccionar_turno.html', context)

    # Asegurar que las fechas estén en formato válido
    fecha_inicio = parse_date(fecha_inicio)
    fecha_fin = parse_date(fecha_fin)
    
    if not fecha_inicio or not fecha_fin:
        context = {'error': 'El formato de las fechas debe ser válido (YYYY-MM-DD).'}
        return render(request, 'reportes/seleccionar_turno.html', context)

    # Verificar que fecha_fin es mayor o igual a fecha_inicio
    if fecha_fin < fecha_inicio:
        context = {'error': 'La fecha final debe ser posterior o igual a la fecha de inicio.'}
        return render(request, 'reportes/seleccionar_turno.html', context)

    # Filtrar turnos por rango de fechas
    turnos = RegistroTurno.objects.filter(inicio_turno__range=[fecha_inicio, fecha_fin])

    # Aplicar filtro por usuario si se seleccionó
    if user_id:
        turnos = turnos.filter(usuario_id=user_id)

    # Si no hay turnos, mostrar un mensaje
    if not turnos.exists():
        context = {'error': 'No se encontraron turnos para las fechas seleccionadas.'}
        return render(request, 'reportes/seleccionar_turno.html', context)

    context = {
        'turnos': turnos,
    }
    return render(request, 'reportes/seleccionar_turno.html', context)

def listar_empleados(request):
    empleados = User.objects.all()  # Cambiado a User
    return render(request, 'reportes/seleccionar_turno_fechas.html', {'empleados': empleados})


def buscar_turno_por_id(request):
    turno_id = request.GET.get('turno_id')

    # Validar que el turno_id es un número válido
    if turno_id and turno_id.isdigit():
        # Obtener el turno o devolver un 404 si no existe
        turno = get_object_or_404(RegistroTurno, id=turno_id)

        # Generar reporte de ventas
        ventas, total_ventas = generar_reporte_ventas_por_turno(turno_id)
        return render(request, 'reportes/reporte_ventas.html', {'ventas': ventas, 'total_ventas': total_ventas})

    # Si el turno_id no es válido o no se encuentra el turno
    if not turno_id:
        return render(request, 'reportes/buscar_turno.html')

    return render(request, 'reportes/error.html', {'error': 'ID de turno inválido o turno no encontrado.'})


from django.shortcuts import render
from RegistroTurnos.models import RegistroTurno
from django.utils.dateparse import parse_date

def seleccionar_turno_detallado(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    user_id = request.GET.get('user_id')  # Cambiado de empleado_id a user_id
    sucursal_id = request.GET.get('sucursal_id')

    # Empezar con una consulta base vacía
    turnos = RegistroTurno.objects.all()

    # Validar y aplicar filtro por rango de fechas
    if fecha_inicio and fecha_fin:
        fecha_inicio = parse_date(fecha_inicio)
        fecha_fin = parse_date(fecha_fin)
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                return render(request, 'reportes/seleccionar_turno_detallado.html', {
                    'error': 'La fecha de fin debe ser mayor o igual a la fecha de inicio.'
                })
            turnos = turnos.filter(inicio_turno__range=[fecha_inicio, fecha_fin])
        else:
            return render(request, 'reportes/seleccionar_turno_detallado.html', {
                'error': 'Las fechas proporcionadas no son válidas.'
            })

    # Validar y aplicar filtro por usuario
    if user_id and user_id.isdigit():
        turnos = turnos.filter(usuario_id=user_id)  # Cambiado a usuario_id
    elif user_id:
        return render(request, 'reportes/seleccionar_turno_detallado.html', {
            'error': 'ID de usuario no es válido.'
        })

    # Validar y aplicar filtro por sucursal
    if sucursal_id and sucursal_id.isdigit():
        turnos = turnos.filter(sucursal_id=sucursal_id)
    elif sucursal_id:
        return render(request, 'reportes/seleccionar_turno_detallado.html', {
            'error': 'ID de sucursal no es válido.'
        })

    # Manejar el caso donde no se encuentran turnos
    if not turnos.exists():
        context = {
            'error': 'No se encontraron turnos para los filtros seleccionados.',
            'turnos': None
        }
    else:
        context = {
            'turnos': turnos
        }

    return render(request, 'reportes/seleccionar_turno_detallado.html', context)