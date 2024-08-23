# conteo/views.py
from django.http import HttpResponse
from .models import ConteoDiario
from .utils import enviar_conteo_por_correo

def enviar_conteo(request):
    # Filtrar los registros de ConteoDiario que se desean incluir en el Excel
    conteos = ConteoDiario.objects.all()  # Puedes aplicar filtros aquí si lo deseas

    # Enviar el correo utilizando la función utilitaria
    enviar_conteo_por_correo(conteos, ['luchoviteri1990@gmail.com'])
    
    # Devolver una respuesta HTTP para confirmar el envío
    return HttpResponse("El conteo diario se ha enviado por correo electrónico.")
