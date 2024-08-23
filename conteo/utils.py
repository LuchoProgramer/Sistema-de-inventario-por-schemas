# conteo/utils.py
import openpyxl
from openpyxl.utils import get_column_letter
from django.core.mail import EmailMessage

def generar_excel_conteo(queryset):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Conteo Diario'

    # Establecer las cabeceras
    headers = ['Sucursal', 'Empleado', 'Fecha', 'Producto', 'Cantidad Contada']
    for col_num, header in enumerate(headers, 1):
        col_letter = get_column_letter(col_num)
        worksheet[f'{col_letter}1'] = header

    # Agregar los datos
    for row_num, conteo in enumerate(queryset, 2):
        worksheet[f'A{row_num}'] = conteo.sucursal.nombre
        worksheet[f'B{row_num}'] = conteo.empleado.username
        worksheet[f'C{row_num}'] = conteo.fecha_conteo
        worksheet[f'D{row_num}'] = conteo.producto.nombre
        worksheet[f'E{row_num}'] = conteo.cantidad_contada

    # Guardar el archivo
    file_path = 'conteo_diario.xlsx'
    workbook.save(file_path)
    return file_path

def enviar_conteo_por_correo(conteos, destinatarios):
    # Generar el archivo Excel
    file_path = generar_excel_conteo(conteos)
    
    # Configurar el correo electrónico
    email = EmailMessage(
        'Conteo Diario de Productos',
        'Adjunto se encuentra el reporte de conteo diario de productos.',
        'luchoviteri1990@gmail.com',  # Remitente
        destinatarios,  # Lista de destinatarios
    )
    email.attach_file(file_path)
    email.send()
