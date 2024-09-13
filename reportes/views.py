from django.shortcuts import render
from ventas.models import Venta
from django.db.models import Sum

def reporte_ventas(request):
    ventas = Venta.objects.all()
    total_ventas = ventas.aggregate(Sum('total_venta'))
    
    return render(request, 'reportes/reporte_ventas.html', {
        'ventas': ventas,
        'total_ventas': total_ventas,
    })

def reporte_ventas_empleado(request):
    # Reporte de ventas agrupadas por empleado
    ventas_por_empleado = Venta.objects.values('empleado__username').annotate(total=Sum('total_venta'))
    
    return render(request, 'reportes/reporte_ventas_empleado.html', {
        'ventas_por_empleado': ventas_por_empleado,
    })

def reporte_ventas_sucursal(request):
    # Reporte de ventas agrupadas por sucursal
    ventas_por_sucursal = Venta.objects.values('sucursal__nombre').annotate(total=Sum('total_venta'))
    
    return render(request, 'reportes/reporte_ventas_sucursal.html', {
        'ventas_por_sucursal': ventas_por_sucursal,
    })
