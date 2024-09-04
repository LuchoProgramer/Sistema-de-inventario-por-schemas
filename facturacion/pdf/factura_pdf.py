from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def configurar_documento(nombre_archivo):
    c = canvas.Canvas(nombre_archivo, pagesize=A4)
    c.setTitle("Factura")
    return c

def agregar_cabecera(c, factura):
    # Información del emisor
    c.drawString(100, 800, f"Nombre Comercial: {factura.sucursal.nombre}")
    c.drawString(100, 780, f"Razón Social: {factura.sucursal.razon_social}")
    c.drawString(100, 760, f"RUC: {factura.sucursal.ruc}")
    c.drawString(100, 740, f"Dirección: {factura.sucursal.direccion}")
    
    # Información de la factura
    c.drawString(100, 720, f"Factura: {factura.numero_autorizacion}")
    c.drawString(100, 700, f"Fecha de Emisión: {factura.fecha_emision.strftime('%d/%m/%Y')}")
    
    # Información del cliente
    c.drawString(100, 680, f"Cliente: {factura.cliente.razon_social}")
    c.drawString(100, 660, f"Tipo Identificación: {factura.cliente.tipo_identificacion}")
    c.drawString(100, 640, f"Identificación: {factura.cliente.identificacion}")
    c.drawString(100, 620, f"Dirección Cliente: {factura.cliente.direccion if factura.cliente.direccion else 'N/A'}")
    
    return c

def agregar_detalles_productos(c, factura):
    y = 580
    c.drawString(100, y, "Detalles de los productos/servicios:")
    y -= 20
    for detalle in factura.detalles.all():
        c.drawString(100, y, f"{detalle.producto.nombre} - {detalle.cantidad} x {detalle.precio_unitario} = {detalle.total}")
        y -= 20
    return c

def agregar_totales(c, factura):
    c.drawString(100, 200, f"Subtotal sin impuestos: {factura.total_sin_impuestos}")
    c.drawString(100, 180, f"Impuestos (IVA 12%): {factura.total_con_impuestos - factura.total_sin_impuestos}")
    c.drawString(100, 160, f"Total con impuestos: {factura.total_con_impuestos}")
    return c

def agregar_mensaje_legal(c):
    c.drawString(100, 120, "Este documento no tiene derecho a crédito tributario.")
    return c

def generar_pdf_factura(factura, nombre_archivo):
    c = configurar_documento(nombre_archivo)
    c = agregar_cabecera(c, factura)
    c = agregar_detalles_productos(c, factura)
    c = agregar_totales(c, factura)
    c = agregar_mensaje_legal(c)
    c.showPage()
    c.save()
