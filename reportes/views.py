from django.shortcuts import render
from .models import Reporte
from django.shortcuts import render, get_object_or_404
from ventas.models import Venta
from django.db.models import Sum


def reporte_ventas(request):
    reportes = Reporte.objects.all()  # Obtén todos los reportes
    return render(request, 'reportes/lista_reportes.html', {'reportes': reportes})



def detalle_reporte(request, id):
    # Obtener el reporte específico por su ID
    reporte = get_object_or_404(Reporte, id=id)
    return render(request, 'reportes/detalle_reporte.html', {'reporte': reporte})


from django.utils import timezone
from django.db.models import Sum
from .models import Reporte
from facturacion.models import Pago  # Asegúrate de importar el modelo Pago

def actualizar_reporte(sucursal, turno):
    # Obtener la fecha actual (para referencia)
    fecha_hoy = timezone.now().date()

    # Obtener todas las ventas de la sucursal y el turno actual
    ventas_hoy = Venta.objects.filter(sucursal=sucursal, turno=turno)

    # Calcular el total de ventas
    total_ventas = ventas_hoy.aggregate(Sum('total_venta'))['total_venta__sum'] or 0

    # Calcular el total de efectivo utilizando el modelo Pago
    total_efectivo = Pago.objects.filter(
        factura__in=ventas_hoy.values('factura'),  # Relacionar pagos con facturas de las ventas
        descripcion__icontains='efectivo'  # Suponiendo que la descripción del pago incluye 'efectivo'
    ).aggregate(Sum('total'))['total__sum'] or 0

    # Calcular el total de otros métodos de pago (lo que no es en efectivo)
    otros_metodos_pago = total_ventas - total_efectivo

    # Actualizar o crear el reporte para el turno actual
    reporte, created = Reporte.objects.update_or_create(
        sucursal=sucursal,
        turno=turno,  # Asegurarte de que estamos creando el reporte para el turno específico
        defaults={
            'total_ventas': total_ventas,
            'total_efectivo': total_efectivo,
            'otros_metodos_pago': otros_metodos_pago,
            'total_facturas': ventas_hoy.count(),
            'fecha': fecha_hoy,  # Esto es solo una referencia si deseas mantener la fecha
        }
    )

    print(f"Reporte actualizado para la sucursal: {sucursal.nombre}, Turno: {turno.id}, Fecha: {fecha_hoy}")