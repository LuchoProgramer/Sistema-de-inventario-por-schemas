from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from decimal import Decimal


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
        presentacion_nombre = detalle.presentacion.nombre_presentacion

        # Verificar si es "Unidad" o un "paquete"
        if presentacion_nombre != "Unidad":
            # Usar la cantidad de paquetes directamente
            cantidad_paquetes = detalle.cantidad // detalle.presentacion.cantidad  
            precio_unitario = detalle.precio_unitario
            total = precio_unitario * cantidad_paquetes

            print(f"Producto: {detalle.producto.nombre}, Presentación: {presentacion_nombre}, "
                  f"Paquetes: {cantidad_paquetes}, Precio por paquete: {precio_unitario:.2f}, Total: {total:.2f}")

            # Formatear la línea de detalle en el PDF
            c.drawString(
                MARGEN_X, y,
                f"{detalle.producto.nombre} - {presentacion_nombre} - {cantidad_paquetes} paquete(s) x {precio_unitario:.2f} = {total:.2f}"
            )
        else:
            # Si es "Unidad", usar la cantidad y precio por unidad
            cantidad = detalle.cantidad
            precio_unitario = detalle.precio_unitario
            total = cantidad * precio_unitario

            print(f"Producto: {detalle.producto.nombre}, Presentación: {presentacion_nombre}, "
                  f"Unidades: {cantidad}, Precio unitario: {precio_unitario:.2f}, Total: {total:.2f}")

            # Formatear la línea de detalle en el PDF
            c.drawString(
                MARGEN_X, y,
                f"{detalle.producto.nombre} - {presentacion_nombre} - {cantidad} x {precio_unitario:.2f} = {total:.2f}"
            )

        y -= 20

        # Verificar si se necesita un salto de página
        if y < 100:
            c.showPage()
            agregar_cabecera(c, factura)
            y = 800
            c.setFont("Helvetica", 10)

    return c


def agregar_totales(c, factura):
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGEN_X, 200, "Totales:")
    c.setFont("Helvetica", 10)

    total_sin_impuestos = Decimal('0.00')
    total_iva = Decimal('0.00')
    total_con_impuestos = Decimal('0.00')

    # Iterar sobre los detalles para sumar correctamente los totales
    for detalle in factura.detalles.all():
        presentacion = detalle.presentacion
        cantidad = detalle.cantidad  # En este caso, es la cantidad de paquetes

        if presentacion.nombre_presentacion == "Unidad":
            # Si es "Unidad", multiplicamos por la cantidad
            subtotal = detalle.precio_unitario * cantidad
        else:
            # Si es un paquete, usamos directamente el precio del paquete
            subtotal = detalle.precio_unitario  # Precio total del paquete

        # Calcular IVA (por ejemplo, 15%)
        iva_item = subtotal * Decimal('0.15')

        total_sin_impuestos += subtotal
        total_iva += iva_item
        total_con_impuestos += subtotal + iva_item

    print(f"Subtotal calculado: {total_sin_impuestos}, Total con IVA: {total_con_impuestos}, IVA: {total_iva}")

    # Mostrar los totales en el PDF
    c.drawString(MARGEN_X, 180, f"Subtotal sin impuestos: {total_sin_impuestos:.2f}")
    c.drawString(MARGEN_X, 160, f"Impuestos (IVA 15%): {total_iva:.2f}")
    c.drawString(MARGEN_X, 140, f"Total con impuestos: {total_con_impuestos:.2f}")

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
