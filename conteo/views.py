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

    # Obtener los productos de la sucursal activa sin incluir el stock
    inventarios = Inventario.objects.filter(sucursal=sucursal_activa)
    productos = [inventario.producto for inventario in inventarios]

    # Filtrar por categoría si está seleccionada
    categoria_seleccionada = request.GET.get('categoria')
    if categoria_seleccionada:
        productos = [producto for producto in productos if str(producto.categoria.id) == categoria_seleccionada]

    if request.method == 'POST':
        form = ConteoProductoForm(request.POST, productos=productos)
        if form.is_valid():
            # Verificar si todos los productos están marcados con cantidad contada
            todos_marcados = all(form.cleaned_data.get(f'producto_{producto.id}') for producto in productos)
            if not todos_marcados:
                messages.error(request, "Todos los productos deben estar marcados y tener una cantidad.")
                return redirect('conteo_incompleto')

            # Guardar los registros de conteo
            for producto in productos:
                cantidad = form.cleaned_data.get(f'cantidad_{producto.id}', 0)
                ConteoDiario.objects.create(
                    sucursal=sucursal_activa,
                    usuario=request.user,
                    fecha_conteo=now().date(),
                    producto=producto,
                    cantidad_contada=cantidad
                )

            # Notificar al usuario sobre el éxito del conteo
            messages.success(request, "El conteo se ha registrado correctamente.")
            return redirect('conteo_exitoso')
    else:
        form = ConteoProductoForm(productos=productos)

    # Estructura de productos con campos de formulario
    productos_con_campos = [
        {
            'producto': producto,
            'producto_field': form[f'producto_{producto.id}'],
            'cantidad_field': form[f'cantidad_{producto.id}']
        }
        for producto in productos
    ]

    context = {
        'form': form,
        'productos_con_campos': productos_con_campos,
        'categorias': Categoria.objects.all(),
        'categoria_seleccionada': categoria_seleccionada,
    }

    return render(request, 'conteo/registrar_conteo.html', context)
# Vista de Conteo Exitoso

def conteo_exitoso(request):
    return render(request, 'conteo/conteo_exitoso.html')

# Vista Conteo Incompleto

def conteo_incompleto(request):
    return render(request, 'conteo/conteo_incompleto.html')
