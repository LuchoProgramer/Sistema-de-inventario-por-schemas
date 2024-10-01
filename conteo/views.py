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

@login_required
def registrar_conteo(request):
    # Verificar si el usuario tiene un turno activo
    turno_activo = RegistroTurno.objects.filter(usuario=request.user, fin_turno__isnull=True).first()
    if not turno_activo:
        return redirect('dashboard')  # Redirigir a iniciar turno si no hay turno activo

    # Obtener la sucursal activa
    sucursal_activa = turno_activo.sucursal

    # Filtrar productos a través del inventario de la sucursal activa
    inventarios = Inventario.objects.filter(sucursal=sucursal_activa)
    productos = [inventario.producto for inventario in inventarios]

    # Obtener todas las categorías para el filtro
    categorias = Categoria.objects.all()

    # Filtrar productos por categoría si se seleccionó alguna
    categoria_seleccionada = request.GET.get('categoria')
    if categoria_seleccionada:
        productos = [producto for producto in productos if str(producto.categoria.id) == categoria_seleccionada]

    # Crear el formulario dinámico
    if request.method == 'POST':
        form = ConteoProductoForm(request.POST, productos=productos)
        if form.is_valid():
            # Verificar si todos los productos están marcados
            todos_marcados = True
            for producto in productos:
                if not form.cleaned_data.get(f'producto_{producto.id}'):
                    todos_marcados = False
                    break

            if not todos_marcados:
                messages.error(request, "Todos los productos deben estar marcados y tener una cantidad.")
                return redirect('conteo_incompleto')

            # Proceder con el conteo y almacenar la información
            conteo_detalles = []
            for producto in productos:
                cantidad = form.cleaned_data.get(f'cantidad_{producto.id}', 0)
                ConteoDiario.objects.create(
                    sucursal=sucursal_activa,
                    usuario=request.user,
                    fecha_conteo=date.today(),
                    producto=producto,
                    cantidad_contada=cantidad
                )
                conteo_detalles.append(f"{producto.nombre}: {cantidad} unidades")

            # Enviar el correo al usuario con el respaldo del conteo si tiene un correo registrado
            if request.user.email:
                asunto = "Resumen del Conteo Diario de Productos"
                mensaje = f"Hola {request.user.username},\n\nEste es el resumen del conteo que realizaste el día {date.today()}:\n\n"
                mensaje += "\n".join(conteo_detalles)
                mensaje += "\n\nGracias por tu trabajo.\n\nSaludos,\nEquipo de Gestión de Inventario"

                send_mail(
                    asunto,
                    mensaje,
                    'luchoviteri1990@gmail.com',  # Cambia esto al correo desde el que se enviará
                    [request.user.email],
                    fail_silently=False,
                )

            return redirect('conteo_exitoso')
    else:
        form = ConteoProductoForm(productos=productos)

    # Preparar el contexto para la plantilla
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
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
    }

    return render(request, 'conteo/registrar_conteo.html', context)


# Vista de Conteo Exitoso

def conteo_exitoso(request):
    return render(request, 'conteo/conteo_exitoso.html')

# Vista Conteo Incompleto

def conteo_incompleto(request):
    return render(request, 'conteo/conteo_incompleto.html')
