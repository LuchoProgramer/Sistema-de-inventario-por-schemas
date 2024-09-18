# reportes/views.py
from django.shortcuts import render
from .services import generar_reporte_ventas_por_turno
from empleados.models import RegistroTurno, Empleado

def reporte_ventas_por_turno(request):
    turno_id = request.GET.get('turno_id')  # Obtener el ID del turno desde la URL
    
    ventas, total_ventas = generar_reporte_ventas_por_turno(turno_id)
    
    context = {
        'ventas': ventas,
        'total_ventas': total_ventas,
    }
    return render(request, 'reportes/reporte_ventas.html', context)


def seleccionar_turno_por_fechas(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    empleado_id = request.GET.get('empleado_id')

    turnos = RegistroTurno.objects.filter(
        inicio_turno__range=[fecha_inicio, fecha_fin], empleado_id=empleado_id
    )

    context = {
        'turnos': turnos,
    }
    return render(request, 'reportes/seleccionar_turno.html', context)

def listar_empleados(request):
    empleados = Empleado.objects.all()  # Para mostrar todos los empleados en el formulario
    return render(request, 'reportes/seleccionar_turno_fechas.html', {'empleados': empleados})


def buscar_turno_por_id(request):
    turno_id = request.GET.get('turno_id')

    if turno_id:
        turno = RegistroTurno.objects.filter(id=turno_id).first()
        if turno:
            ventas, total_ventas = generar_reporte_ventas_por_turno(turno_id)
            return render(request, 'reportes/reporte_ventas.html', {'ventas': ventas, 'total_ventas': total_ventas})
        else:
            return render(request, 'reportes/error.html', {'error': 'No se encontró el turno con el ID proporcionado'})
    else:
        return render(request, 'reportes/buscar_turno.html')
    

# reportes/views.py
def seleccionar_turno_detallado(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    empleado_id = request.GET.get('empleado_id')
    sucursal_id = request.GET.get('sucursal_id')

    turnos = RegistroTurno.objects.all()

    if fecha_inicio and fecha_fin:
        turnos = turnos.filter(inicio_turno__range=[fecha_inicio, fecha_fin])

    if empleado_id:
        turnos = turnos.filter(empleado_id=empleado_id)

    if sucursal_id:
        turnos = turnos.filter(sucursal_id=sucursal_id)

    context = {
        'turnos': turnos,
    }
    return render(request, 'reportes/seleccionar_turno_detallado.html', context)
