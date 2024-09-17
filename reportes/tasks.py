from celery import shared_task
from django.utils import timezone
from reportes.models import MovimientoReporte, Reporte
from django.db.models import Sum

@shared_task
def actualizar_reporte_ventas():
    # Obtener la fecha actual
    fecha_actual = timezone.now().date()

    # Obtener los movimientos de ventas del día
    movimientos = MovimientoReporte.objects.filter(fecha=fecha_actual)

    # Agrupar por sucursal
    sucursales = movimientos.values('sucursal_id').distinct()

    # Procesar los reportes por cada sucursal
    for sucursal_data in sucursales:
        sucursal_id = sucursal_data['sucursal_id']
        movimientos_sucursal = movimientos.filter(sucursal_id=sucursal_id)

        # Calcular los totales
        total_ventas = movimientos_sucursal.aggregate(Sum('total_venta'))['total_venta__sum'] or 0
        total_facturas = movimientos_sucursal.values('venta__factura').distinct().count()
        total_efectivo = movimientos_sucursal.filter(pago__descripcion__icontains='efectivo').aggregate(Sum('pago__total'))['pago__total__sum'] or 0
        otros_metodos_pago = movimientos_sucursal.exclude(pago__descripcion__icontains='efectivo').aggregate(Sum('pago__total'))['pago__total__sum'] or 0

        # Crear o actualizar el reporte
        reporte, created = Reporte.objects.get_or_create(sucursal_id=sucursal_id, fecha=fecha_actual, defaults={
            'total_ventas': total_ventas,
            'total_facturas': total_facturas,
            'total_efectivo': total_efectivo,
            'otros_metodos_pago': otros_metodos_pago
        })

        if not created:
            reporte.total_ventas = total_ventas
            reporte.total_facturas = total_facturas
            reporte.total_efectivo = total_efectivo
            reporte.otros_metodos_pago = otros_metodos_pago
            reporte.save()
