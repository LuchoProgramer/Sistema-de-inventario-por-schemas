# conteo/tasks.py
from django.core.mail import EmailMessage
from .utils import generar_excel_conteo

def enviar_conteo_por_correo():
    file_path = generar_excel_conteo()
    email = EmailMessage(
        'Conteo Diario de Productos',
        'Adjunto se encuentra el reporte de conteo diario de productos.',
        'luchoviteri1990@gmail.com',
        ['luchoviteri1990@gmail.com'],
    )
    email.attach_file(file_path)
    email.send()
