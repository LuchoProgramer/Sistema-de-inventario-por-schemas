from django.shortcuts import render, redirect
from django.contrib import messages  # Importar para usar mensajes de alerta
from .forms import ConteoProductoForm
from .models import ConteoDiario
from inventarios.models import Producto, Categoria
from .utils import generar_y_enviar_excel  # Asegúrate de importar la función

def registrar_conteo(request):
    categoria_seleccionada = request.GET.get('categoria')
    productos = Producto.objects.all()

    if categoria_seleccionada:
        productos = productos.filter(categoria_id=categoria_seleccionada)

    if request.method == 'POST':
        form = ConteoProductoForm(request.POST, productos=productos)
        if form.is_valid():
            sucursal = request.POST.get('sucursal')
            todos_marcados = True  # Variable para verificar si todos los productos están marcados

            for producto in productos:
                if not form.cleaned_data.get(f'producto_{producto.id}'):
                    todos_marcados = False
                    break  # Salir del bucle si se encuentra un producto no marcado

            if not todos_marcados:
                messages.error(request, "Todos los productos deben estar marcados y tener una cantidad.")
                return redirect('conteo_incompleto')

            # Si todos los productos están marcados, proceder con el conteo
            for producto in productos:
                cantidad = form.cleaned_data.get(f'cantidad_{producto.id}', 0)
                ConteoDiario.objects.create(
                    sucursal=sucursal,
                    empleado=request.user,  # Guardamos el usuario logueado como empleado
                    producto=producto,
                    cantidad_contada=cantidad
                )
            
            # Generar y enviar el archivo Excel
            generar_y_enviar_excel(sucursal=sucursal, empleado=request.user, email_destino='luchoviteri1990@gmail.com')
            
            return redirect('conteo_exitoso')  # Redirigir a una página de éxito o similar
    else:
        form = ConteoProductoForm(productos=productos)
    
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
    }

    return render(request, 'conteo/registrar_conteo.html', context)


# Vista de Conteo Exitoso

def conteo_exitoso(request):
    return render(request, 'conteo/conteo_exitoso.html')

# Vista Conteo Incompleto

def conteo_incompleto(request):
    return render(request, 'conteo/conteo_incompleto.html')
