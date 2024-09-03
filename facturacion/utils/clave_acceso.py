import random
import datetime
from .verificador import calcular_digito_verificador

def generar_clave_acceso(fecha_emision, tipo_comprobante, ruc, ambiente, estab, pto_emi, secuencial, tipo_emision):
    # Validaciones preventivas
    if fecha_emision is None:
        raise ValueError("La fecha de emisión no puede ser None")
    
    # Formatear la fecha de emisión si es un objeto datetime
    if isinstance(fecha_emision, datetime.datetime):
        fecha_emision = fecha_emision.strftime('%d%m%Y')
    
    # Verifica que todos los componentes sean cadenas y no None
    if None in [tipo_comprobante, ruc, ambiente, estab, pto_emi, secuencial, tipo_emision]:
        print("tipo_comprobante:", tipo_comprobante)
        print("ruc:", ruc)
        print("ambiente:", ambiente)
        print("estab:", estab)
        print("pto_emi:", pto_emi)
        print("secuencial:", secuencial)
        print("tipo_emision:", tipo_emision)
        raise ValueError("Uno de los componentes para generar la clave de acceso es None")

    # Asegurarse de que todos los valores sean cadenas
    tipo_comprobante = str(tipo_comprobante)
    ruc = str(ruc)
    ambiente = str(ambiente)
    estab = str(estab)
    pto_emi = str(pto_emi)
    secuencial = str(secuencial)
    tipo_emision = str(tipo_emision)

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
