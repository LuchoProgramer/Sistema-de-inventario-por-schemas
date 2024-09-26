from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch

# Constantes de márgenes
MARGEN_X = 50
MARGEN_Y = 50

def configurar_documento(nombre_archivo):
    c = canvas.Canvas(nombre_archivo, pagesize=A4)
    c.setTitle("Factura")
    return c

def agregar_cabecera(c, factura):
    # Información del emisor (Sucursal)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGEN_X, 800, f"Nombre Comercial: {factura.sucursal.nombre}")
    c.setFont("Helvetica", 10)
    c.drawString(MARGEN_X, 780, f"Razón Social: {factura.sucursal.razon_social}")
    c.drawString(MARGEN_X, 760, f"RUC: {factura.sucursal.ruc}")
    c.drawString(MARGEN_X, 740, f"Dirección: {factura.sucursal.direccion}")
    
    # Información de la factura
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGEN_X, 720, f"Factura: {factura.numero_autorizacion}")
    c.setFont("Helvetica", 10)
    c.drawString(MARGEN_X, 700, f"Fecha de Emisión: {factura.fecha_emision.strftime('%d/%m/%Y')}")
    
    # Información del cliente
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGEN_X, 680, f"Cliente: {factura.cliente.razon_social}")
    c.setFont("Helvetica", 10)
    c.drawString(MARGEN_X, 660, f"Tipo Identificación: {factura.cliente.tipo_identificacion}")
    c.drawString(MARGEN_X, 640, f"Identificación: {factura.cliente.identificacion}")
    c.drawString(MARGEN_X, 620, f"Dirección Cliente: {factura.cliente.direccion if factura.cliente.direccion else 'N/A'}")
    
    return c

def agregar_detalles_productos(c, factura):
    y = 580
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGEN_X, y, "Detalles de los productos/servicios:")
    y -= 20
    c.setFont("Helvetica", 10)

    for detalle in factura.detalles.all():
        # Formatear la línea de detalle
        c.drawString(MARGEN_X, y, f"{detalle.producto.nombre} - {detalle.cantidad} x {detalle.precio_unitario:.2f} = {detalle.total:.2f}")
        y -= 20

        # Comprobar si es necesario un salto de página
        if y < 100:
            c.showPage()  # Añadir una nueva página
            agregar_cabecera(c, factura)  # Reagregar la cabecera en la nueva página
            y = 800  # Reiniciar la posición y
            c.setFont("Helvetica", 10)

    return c

def agregar_totales(c, factura):
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGEN_X, 200, "Totales:")
    c.setFont("Helvetica", 10)
    
    iva = factura.total_con_impuestos - factura.total_sin_impuestos
    c.drawString(MARGEN_X, 180, f"Subtotal sin impuestos: {factura.total_sin_impuestos:.2f}")
    c.drawString(MARGEN_X, 160, f"Impuestos (IVA 12%): {iva:.2f}")
    c.drawString(MARGEN_X, 140, f"Total con impuestos: {factura.total_con_impuestos:.2f}")
    
    return c

def agregar_mensaje_legal(c):
    c.setFont("Helvetica", 8)
    c.drawString(MARGEN_X, 120, "Este documento no tiene derecho a crédito tributario.")
    return c

def generar_pdf_factura(factura, nombre_archivo):
    c = configurar_documento(nombre_archivo)
    c = agregar_cabecera(c, factura)
    c = agregar_detalles_productos(c, factura)
    c = agregar_totales(c, factura)
    c = agregar_mensaje_legal(c)
    c.showPage()
    c.save()
