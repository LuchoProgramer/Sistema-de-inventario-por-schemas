from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
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
    print(f"Generando cabecera para la factura: {factura.numero_autorizacion}")
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
        # Acceder a la presentación desde el modelo DetalleFactura
        presentacion_nombre = detalle.presentacion.nombre_presentacion

        # Si la presentación es "Unidad", se multiplica por la cantidad; si es un paquete ("Media" o "Entera"), se usa el precio total del paquete
        if presentacion_nombre == "Unidad":
            precio_unitario = detalle.precio_unitario
            total = detalle.cantidad * detalle.precio_unitario
        else:
            precio_unitario = detalle.precio_unitario  # Precio global por paquete
            total = precio_unitario  # Total es el precio del paquete por la cantidad de paquetes

        # Añadir print para verificar los datos
        print(f"Producto: {detalle.producto.nombre}, Presentación: {presentacion_nombre}, "
              f"Cantidad: {detalle.cantidad}, Precio unitario: {precio_unitario:.2f}, Total: {total:.2f}")

        # Formatear la línea de detalle en el PDF
        c.drawString(MARGEN_X, y, f"{detalle.producto.nombre} - {presentacion_nombre} - {detalle.cantidad} x {precio_unitario:.2f} = {total:.2f}")
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
    
    # Cálculo dinámico del IVA
    iva = factura.total_con_impuestos - factura.total_sin_impuestos
    porcentaje_iva = factura.impuesto.porcentaje if hasattr(factura, 'impuesto') else 15
    
    print(f"Subtotal: {factura.total_sin_impuestos}, Total con impuestos: {factura.total_con_impuestos}, IVA: {iva:.2f} ({porcentaje_iva}%)")
    
    c.drawString(MARGEN_X, 180, f"Subtotal sin impuestos: {factura.total_sin_impuestos:.2f}")
    c.drawString(MARGEN_X, 160, f"Impuestos (IVA {porcentaje_iva}%): {iva:.2f}")
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
