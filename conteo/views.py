from django.shortcuts import render, redirect
from django.contrib import messages  # Importar para usar mensajes de alerta
from .forms import ConteoProductoForm
from .models import ConteoDiario
from inventarios.models import Producto, Categoria, Inventario
from .utils import generar_y_enviar_excel  # Asegúrate de importar la función
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from RegistroTurnos.models import RegistroTurno
from .models import ConteoDiario
from .forms import ConteoProductoForm
from datetime import date
from inventario.decorators import empleado_o_admin_con_turno_y_sucursal_required
from django.contrib.auth.models import Group
import tempfile
from django.core.mail import EmailMessage
from django.utils.timezone import now

@login_required
@empleado_o_admin_con_turno_y_sucursal_required
def registrar_conteo(request):
    # Obtener el turno activo del usuario
    turno_activo = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()
    if not turno_activo:
        return redirect('dashboard')

    sucursal_activa = turno_activo.sucursal

    # Obtener los productos de la sucursal activa
    inventarios = Inventario.objects.filter(sucursal=sucursal_activa)
    productos = [inventario.producto for inventario in inventarios]

    # Filtrar por categoría si está seleccionada
    categoria_seleccionada = None
    if request.method == 'POST':
        form = ConteoProductoForm(request.POST, productos=productos)
        if form.is_valid():
            # Guardar los registros de conteo
            for producto in productos:
                cantidad = form.cleaned_data.get(f'cantidad_{producto.id}', None)
                if cantidad is not None:
                    ConteoDiario.objects.create(
                        sucursal=sucursal_activa,
                        usuario=request.user,
                        fecha_conteo=now().date(),
                        producto=producto,
                        cantidad_contada=cantidad
                    )

            # Generar y enviar el archivo Excel
            email_destino = 'luchoviteri1990@gmail.com'  # Puedes cambiar esto al email deseado
            try:
                generar_y_enviar_excel(sucursal_activa, request.user, email_destino)
                messages.success(request, "El conteo se ha registrado y enviado correctamente.")
            except Exception as e:
                messages.error(request, f"El conteo se registró, pero no se pudo enviar el correo: {str(e)}")

            return redirect('conteo_exitoso')
    else:
        categoria_seleccionada = request.GET.get('categoria')
        if categoria_seleccionada:
            productos = [producto for producto in productos if str(producto.categoria.id) == categoria_seleccionada]
        form = ConteoProductoForm(productos=productos)
        form.fields['categoria'].initial = categoria_seleccionada

    context = {
        'form': form,
        'categorias': Categoria.objects.all(),
        'categoria_seleccionada': categoria_seleccionada,
        'turno': turno_activo,
        'sucursal_activa': sucursal_activa,
    }

    return render(request, 'conteo/registrar_conteo.html', context)


# Vista de Conteo Exitoso

def conteo_exitoso(request):
    return render(request, 'conteo/conteo_exitoso.html')

# Vista Conteo Incompleto

def conteo_incompleto(request):
    return render(request, 'conteo/conteo_incompleto.html')
