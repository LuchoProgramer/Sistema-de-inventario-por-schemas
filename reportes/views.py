from django.shortcuts import render
from .models import Reporte
from django.shortcuts import render, get_object_or_404

def reporte_ventas(request):
    reportes = Reporte.objects.all()  # Obtén todos los reportes
    return render(request, 'reportes/lista_reportes.html', {'reportes': reportes})



def detalle_reporte(request, id):
    # Obtener el reporte específico por su ID
    reporte = get_object_or_404(Reporte, id=id)
    return render(request, 'reportes/detalle_reporte.html', {'reporte': reporte})
