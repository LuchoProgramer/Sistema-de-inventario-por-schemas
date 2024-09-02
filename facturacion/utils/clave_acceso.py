import random
from .verificador import calcular_digito_verificador

def generar_clave_acceso(fecha_emision, tipo_comprobante, ruc, ambiente, estab, pto_emi, secuencial, tipo_emision):
    # Formatear la fecha de emisión
    fecha_emision = fecha_emision.strftime('%d%m%Y')
    
    # Generar un código numérico aleatorio de 8 dígitos
    codigo_numerico = str(random.randint(10000000, 99999999))
    
    # Concatenar todos los componentes para formar la clave de acceso
    clave_acceso_sin_dv = (
        fecha_emision +
        tipo_comprobante +
        ruc +
        ambiente +
        estab +
        pto_emi +
        secuencial +
        codigo_numerico +
        tipo_emision
    )
    
    # Calcular el dígito verificador usando el módulo 11
    digito_verificador = calcular_digito_verificador(clave_acceso_sin_dv)
    
    # Añadir el dígito verificador a la clave de acceso
    clave_acceso = clave_acceso_sin_dv + str(digito_verificador)
    
    return clave_acceso
