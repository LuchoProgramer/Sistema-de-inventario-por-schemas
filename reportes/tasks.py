from celery import shared_task
from django.utils import timezone
from ventas.models import Venta
from facturacion.models import Factura, Pago
from django.db.models import Sum
from reportes.models import Reporte

@shared_task
def actualizar_reporte_ventas():
    # Obtener la fecha actual
    fecha_actual = timezone.now().date()

    # Obtener todas las ventas del día
    ventas = Venta.objects.filter(fecha__date=fecha_actual)

    # Agrupar por sucursal
    sucursales = ventas.values('sucursal_id').distinct()

    # Procesar las ventas por sucursal
    for sucursal_data in sucursales:
        sucursal_id = sucursal_data['sucursal_id']

        # Filtrar ventas para esta sucursal
        ventas_sucursal = ventas.filter(sucursal_id=sucursal_id)

        # Calcular el total de ventas
        total_ventas = ventas_sucursal.aggregate(Sum('total_venta'))['total_venta__sum'] or 0

        # Obtener las facturas generadas para esta sucursal
        facturas_sucursal = Factura.objects.filter(ventas__in=ventas_sucursal).distinct()

        # Calcular el total de facturas y los pagos por método
        total_facturas = facturas_sucursal.count()
        total_efectivo = Pago.objects.filter(factura__in=facturas_sucursal, descripcion__icontains='efectivo').aggregate(Sum('total'))['total__sum'] or 0
        otros_metodos_pago = Pago.objects.filter(factura__in=facturas_sucursal).exclude(descripcion__icontains='efectivo').aggregate(Sum('total'))['total__sum'] or 0

        # Crear o actualizar el reporte para la sucursal
        reporte, created = Reporte.objects.get_or_create(sucursal_id=sucursal_id, fecha=fecha_actual, defaults={
            'total_ventas': total_ventas,
            'total_facturas': total_facturas,
            'total_efectivo': total_efectivo,
            'otros_metodos_pago': otros_metodos_pago
        })

        if not created:
            # Actualizar si el reporte ya existe
            reporte.total_ventas = total_ventas
            reporte.total_facturas = total_facturas
            reporte.total_efectivo = total_efectivo
            reporte.otros_metodos_pago = otros_metodos_pago
            reporte.save()
