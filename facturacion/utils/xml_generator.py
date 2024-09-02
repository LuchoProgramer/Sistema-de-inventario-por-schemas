from lxml import etree
from .clave_acceso import generar_clave_acceso

def generar_xml_para_sri(self):
    # Crear la estructura del XML según las especificaciones del SRI
    factura = etree.Element('factura', Id="comprobante", version="1.0.0")
        
    info_tributaria = etree.SubElement(factura, 'infoTributaria')
    etree.SubElement(info_tributaria, 'ambiente').text = '1'  # 1 para pruebas, 2 para producción
    etree.SubElement(info_tributaria, 'tipoEmision').text = '1'  # 1 para emisión normal
    etree.SubElement(info_tributaria, 'razonSocial').text = self.cliente.razon_social
    etree.SubElement(info_tributaria, 'nombreComercial').text = self.sucursal.nombre
    etree.SubElement(info_tributaria, 'ruc').text = '1790012345001'
        
    # Generar y asignar la clave de acceso
    clave_acceso = self.generar_clave_acceso()
    etree.SubElement(info_tributaria, 'claveAcceso').text = clave_acceso
        
    etree.SubElement(info_tributaria, 'codDoc').text = '01'  # Código de factura
    etree.SubElement(info_tributaria, 'estab').text = '001'  # Código del establecimiento
    etree.SubElement(info_tributaria, 'ptoEmi').text = '001'  # Código del punto de emisión
    etree.SubElement(info_tributaria, 'secuencial').text = '000000001'  # Secuencial
    etree.SubElement(info_tributaria, 'dirMatriz').text = self.sucursal.direccion

    info_factura = etree.SubElement(factura, 'infoFactura')
    etree.SubElement(info_factura, 'fechaEmision').text = self.fecha_emision.strftime('%d/%m/%Y')
    etree.SubElement(info_factura, 'dirEstablecimiento').text = self.sucursal.direccion
    etree.SubElement(info_factura, 'contribuyenteEspecial').text = '5368'  # Según tu configuración
    etree.SubElement(info_factura, 'obligadoContabilidad').text = 'SI'
    etree.SubElement(info_factura, 'tipoIdentificacionComprador').text = '04'  # RUC
    etree.SubElement(info_factura, 'razonSocialComprador').text = self.cliente.razon_social
    etree.SubElement(info_factura, 'identificacionComprador').text = self.cliente.identificacion
    etree.SubElement(info_factura, 'totalSinImpuestos').text = '100.00'  # Total sin impuestos
    etree.SubElement(info_factura, 'totalDescuento').text = '0.00'  # Descuento total
        
    # Bloque totalConImpuestos
    total_con_impuestos = etree.SubElement(info_factura, 'totalConImpuestos')
    total_impuesto = etree.SubElement(total_con_impuestos, 'totalImpuesto')
    etree.SubElement(total_impuesto, 'codigo').text = '2'
    etree.SubElement(total_impuesto, 'codigoPorcentaje').text = '2'
    etree.SubElement(total_impuesto, 'baseImponible').text = '100.00'
    etree.SubElement(total_impuesto, 'valor').text = '12.00'

    etree.SubElement(info_factura, 'propina').text = '0.00'
    etree.SubElement(info_factura, 'importeTotal').text = '112.00'
    etree.SubElement(info_factura, 'moneda').text = 'DOLAR'

    # Detalles de los productos o servicios
    detalles = etree.SubElement(factura, 'detalles')
    detalle = etree.SubElement(detalles, 'detalle')
    etree.SubElement(detalle, 'codigoPrincipal').text = '001'
    etree.SubElement(detalle, 'descripcion').text = 'Producto o Servicio'
    etree.SubElement(detalle, 'cantidad').text = '1'
    etree.SubElement(detalle, 'precioUnitario').text = '100.00'
    etree.SubElement(detalle, 'descuento').text = '0.00'
    etree.SubElement(detalle, 'precioTotalSinImpuesto').text = '100.00'
        
    # Impuestos aplicados a los detalles
    impuestos = etree.SubElement(detalle, 'impuestos')
    impuesto = etree.SubElement(impuestos, 'impuesto')
    etree.SubElement(impuesto, 'codigo').text = '2'
    etree.SubElement(impuesto, 'codigoPorcentaje').text = '2'
    etree.SubElement(impuesto, 'tarifa').text = '12'
    etree.SubElement(impuesto, 'baseImponible').text = '100.00'
    etree.SubElement(impuesto, 'valor').text = '12.00'

    # Información adicional
    info_adicional = etree.SubElement(factura, 'infoAdicional')
    campo_adicional = etree.SubElement(info_adicional, 'campoAdicional', nombre="Observacion")
    campo_adicional.text = "Factura de prueba"

    # Convertir el XML a cadena
    xml_str = etree.tostring(factura, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    return xml_str
