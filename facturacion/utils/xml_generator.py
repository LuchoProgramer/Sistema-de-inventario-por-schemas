from lxml import etree
from .clave_acceso import generar_clave_acceso


def generar_xml_para_sri(factura):
    # Crear la estructura del XML según las especificaciones del SRI
    factura_xml = etree.Element('factura', Id="comprobante", version="1.0.0")
        
    info_tributaria = etree.SubElement(factura_xml, 'infoTributaria')
    etree.SubElement(info_tributaria, 'ambiente').text = '1'  # 1 para pruebas, 2 para producción
    etree.SubElement(info_tributaria, 'tipoEmision').text = '1'  # 1 para emisión normal
    etree.SubElement(info_tributaria, 'razonSocial').text = factura.cliente.razon_social
    etree.SubElement(info_tributaria, 'nombreComercial').text = factura.sucursal.nombre
    etree.SubElement(info_tributaria, 'ruc').text = factura.sucursal.ruc
    
    # Generar y asignar la clave de acceso
    clave_acceso = generar_clave_acceso(
        fecha_emision=factura.fecha_emision,
        tipo_comprobante='01',  # Código de factura
        ruc=factura.sucursal.ruc,
        ambiente='1',  # Asumiendo ambiente 1 para pruebas
        estab=factura.sucursal.codigo_establecimiento,
        pto_emi=factura.sucursal.punto_emision,
        secuencial=factura.numero_autorizacion,
        tipo_emision='1'  # Asumiendo tipo de emisión normal
    )
    etree.SubElement(info_tributaria, 'claveAcceso').text = clave_acceso
    
    etree.SubElement(info_tributaria, 'codDoc').text = '01'  # Código de factura
    etree.SubElement(info_tributaria, 'estab').text = factura.sucursal.codigo_establecimiento
    etree.SubElement(info_tributaria, 'ptoEmi').text = factura.sucursal.punto_emision
    etree.SubElement(info_tributaria, 'secuencial').text = factura.numero_autorizacion
    etree.SubElement(info_tributaria, 'dirMatriz').text = factura.sucursal.direccion

    info_factura = etree.SubElement(factura_xml, 'infoFactura')
    etree.SubElement(info_factura, 'fechaEmision').text = factura.fecha_emision.strftime('%d/%m/%Y')
    etree.SubElement(info_factura, 'dirEstablecimiento').text = factura.sucursal.direccion
    etree.SubElement(info_factura, 'contribuyenteEspecial').text = '5368'  # Según tu configuración
    etree.SubElement(info_factura, 'obligadoContabilidad').text = 'SI'
    etree.SubElement(info_factura, 'tipoIdentificacionComprador').text = factura.cliente.tipo_identificacion  # RUC, cédula, etc.
    etree.SubElement(info_factura, 'razonSocialComprador').text = factura.cliente.razon_social
    etree.SubElement(info_factura, 'identificacionComprador').text = factura.cliente.identificacion
    etree.SubElement(info_factura, 'totalSinImpuestos').text = str(factura.total_sin_impuestos)
    etree.SubElement(info_factura, 'totalDescuento').text = '0.00'  # Descuento total
    
    # Bloque totalConImpuestos
    total_con_impuestos = etree.SubElement(info_factura, 'totalConImpuestos')
    total_impuesto = etree.SubElement(total_con_impuestos, 'totalImpuesto')
    etree.SubElement(total_impuesto, 'codigo').text = '2'
    etree.SubElement(total_impuesto, 'codigoPorcentaje').text = '2'
    etree.SubElement(total_impuesto, 'baseImponible').text = str(factura.total_sin_impuestos)
    etree.SubElement(total_impuesto, 'valor').text = str(factura.total_con_impuestos - factura.total_sin_impuestos)

    etree.SubElement(info_factura, 'propina').text = '0.00'
    etree.SubElement(info_factura, 'importeTotal').text = str(factura.total_con_impuestos)
    etree.SubElement(info_factura, 'moneda').text = 'DOLAR'

    # Detalles de los productos o servicios
    detalles = etree.SubElement(factura_xml, 'detalles')
    for detalle in factura.detalles.all():  # Utilizando 'detalles'
        detalle_element = etree.SubElement(detalles, 'detalle')
        etree.SubElement(detalle_element, 'codigoPrincipal').text = str(detalle.producto.id)
        etree.SubElement(detalle_element, 'descripcion').text = detalle.producto.nombre
        etree.SubElement(detalle_element, 'cantidad').text = str(detalle.cantidad)
        etree.SubElement(detalle_element, 'precioUnitario').text = str(detalle.precio_unitario)
        etree.SubElement(detalle_element, 'descuento').text = str(detalle.descuento)
        etree.SubElement(detalle_element, 'precioTotalSinImpuesto').text = str(detalle.subtotal)
        
        # Impuestos aplicados a los detalles
        impuestos = etree.SubElement(detalle_element, 'impuestos')
        impuesto = etree.SubElement(impuestos, 'impuesto')
        etree.SubElement(impuesto, 'codigo').text = '2'
        etree.SubElement(impuesto, 'codigoPorcentaje').text = '2'
        etree.SubElement(impuesto, 'tarifa').text = '12'
        etree.SubElement(impuesto, 'baseImponible').text = str(detalle.subtotal)
        etree.SubElement(impuesto, 'valor').text = str(detalle.total - detalle.subtotal)

    # Convertir el XML a cadena
    xml_str = etree.tostring(factura_xml, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    return xml_str
