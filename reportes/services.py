# reportes/services.py
from ventas.models import Venta
from empleados.models import RegistroTurno
from django.db.models import Sum

def generar_reporte_ventas_por_turno(turno_id):
    turno = RegistroTurno.objects.get(id=turno_id)
    ventas = turno.ventas.all()  # Obtener todas las ventas asociadas al turno
    
    total_ventas = ventas.aggregate(total=Sum('total_venta'))['total']
    total_ventas = total_ventas if total_ventas is not None else 0

    return ventas, total_ventas
