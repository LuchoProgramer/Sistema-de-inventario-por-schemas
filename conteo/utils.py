import openpyxl
from openpyxl.utils import get_column_letter
from django.core.mail import EmailMessage
from .models import ConteoDiario
import tempfile
import os

def generar_y_enviar_excel(sucursal, empleado, email_destino):
    # Crear un nuevo libro de trabajo
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = f"Conteo de {sucursal}"

    # Agregar la sucursal y el empleado en las primeras filas
    sheet['A1'] = 'Sucursal:'
    sheet['B1'] = sucursal
    sheet['A2'] = 'Empleado:'
    sheet['B2'] = empleado.get_full_name()  # Usamos el nombre completo del empleado

    # Crear los encabezados
    headers = ['Producto', 'Cantidad Contada', 'Fecha de Conteo']
    for col_num, header in enumerate(headers, 1):
        col_letter = get_column_letter(col_num)
        sheet[f'{col_letter}4'] = header  # Los encabezados comienzan en la fila 4

    # Obtener los datos del conteo para la sucursal y empleado específicos
    conteos = ConteoDiario.objects.filter(sucursal=sucursal, empleado=empleado)

    # Llenar el archivo Excel con los datos
    for row_num, conteo in enumerate(conteos, start=5):  # Los datos comienzan en la fila 5
        sheet[f'A{row_num}'] = conteo.producto.nombre
        sheet[f'B{row_num}'] = conteo.cantidad_contada
        sheet[f'C{row_num}'] = conteo.fecha_conteo.strftime('%Y-%m-%d')

    # Usar un archivo temporal para guardar el Excel
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        workbook.save(tmp.name)
        tmp_path = tmp.name

    # Enviar el archivo Excel por correo electrónico
    email = EmailMessage(
        subject=f'Reporte de Conteo Diario - {sucursal}',
        body=f'Adjunto encontrarás el reporte del conteo diario realizado por {empleado.get_full_name()}.',
        from_email='tucorreo@example.com',
        to=[email_destino],
    )
    email.attach_file(tmp_path)
    email.send()

    # Eliminar los registros de conteo después de enviar el correo
    conteos.delete()

    # Asegurarse de eliminar el archivo temporal después de enviar el correo
    os.remove(tmp_path)
