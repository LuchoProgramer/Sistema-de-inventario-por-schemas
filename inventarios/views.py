from django.shortcuts import render, redirect
from .models import Producto, Inventario, Compra, Categoria, Transferencia, MovimientoInventario
from django.shortcuts import get_object_or_404
from .forms import CompraForm, ProductoForm, CategoriaForm, TransferenciaForm
from sucursales.models import Sucursal
from django.core.paginator import Paginator

def seleccionar_sucursal(request):
    # Obtener el usuario autenticado
    usuario = request.user

    # Asumiendo que el usuario está relacionado con sucursales directamente
    # Si tienes un campo de relación entre Usuario y Sucursal
    sucursales = usuario.sucursales.all()  # Obtener las sucursales del usuario

    if request.method == 'POST':
        sucursal_id = request.POST.get('sucursal_id')
        return redirect('inventarios:ver_inventario', sucursal_id=sucursal_id)  # Redirigir al inventario de la sucursal seleccionada

    return render(request, 'inventarios/seleccionar_sucursal.html', {'sucursales': sucursales})


def ver_inventario(request, sucursal_id):
    sucursal = get_object_or_404(Sucursal, id=sucursal_id)

    # Obtener los inventarios solo para la sucursal seleccionada
    inventarios = Inventario.objects.filter(sucursal=sucursal)

    return render(request, 'inventarios/ver_inventario.html', {'inventarios': inventarios, 'sucursal': sucursal})


def agregar_producto_inventario(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        sucursal_id = request.POST.get('sucursal_id')
        cantidad = int(request.POST.get('cantidad'))

        producto = Producto.objects.get(id=producto_id)
        sucursal = Sucursal.objects.get(id=sucursal_id)

        # Buscar si ya existe el inventario para ese producto y sucursal
        inventario, created = Inventario.objects.get_or_create(
            producto=producto,
            sucursal=sucursal
        )

        # Actualizamos la cantidad en el inventario
        inventario.cantidad += cantidad
        inventario.save()

        # Redirigir al inventario de la sucursal seleccionada, pasando el sucursal_id
        return redirect('inventarios:ver_inventario', sucursal_id=sucursal_id)

    productos = Producto.objects.all()
    sucursales = Sucursal.objects.all()
    return render(request, 'inventarios/agregar_producto_inventario.html', {'productos': productos, 'sucursales': sucursales})


def ajustar_inventario(request, producto_id, sucursal_id):
    producto = get_object_or_404(Producto, id=producto_id)
    sucursal = get_object_or_404(Sucursal, id=sucursal_id)
    inventario = get_object_or_404(Inventario, producto=producto, sucursal=sucursal)

    if request.method == 'POST':
        nueva_cantidad = request.POST.get('nueva_cantidad')

        # Validar que la nueva cantidad es un número entero válido
        try:
            nueva_cantidad = int(nueva_cantidad)
            if nueva_cantidad < 0:
                raise ValueError("La cantidad no puede ser negativa")
        except ValueError:
            # Si la cantidad no es válida, podrías mostrar un mensaje de error
            return render(request, 'inventarios/ajustar_inventario.html', {
                'inventario': inventario,
                'producto': producto,
                'sucursal': sucursal,
                'error': 'La cantidad debe ser un número entero válido y no negativo.'
            })

        # Actualizamos la cantidad en el inventario
        inventario.cantidad = nueva_cantidad
        inventario.save()

        # Redirigir al inventario de la sucursal, pasando el sucursal_id correctamente
        return redirect('inventarios:ver_inventario', sucursal_id=sucursal.id)

    return render(request, 'inventarios/ajustar_inventario.html', {
        'inventario': inventario,
        'producto': producto,
        'sucursal': sucursal
    })


def agregar_compra(request):
    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            compra = form.save(commit=False)
            compra.save()
            # Redirigir al inventario de la sucursal después de la compra
            return redirect('inventarios:ver_inventario', sucursal_id=compra.sucursal.id)
        else:
            # Si el formulario no es válido, mostrar los errores
            return render(request, 'inventarios/agregar_compra.html', {'form': form, 'errors': form.errors})

    else:
        form = CompraForm()

    return render(request, 'inventarios/agregar_compra.html', {'form': form})


def ver_compras(request):
    compras = Compra.objects.all().order_by('-fecha')  # Ordenar por fecha más reciente

    # Agregar paginación
    paginator = Paginator(compras, 10)  # Muestra 10 compras por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventarios/ver_compras.html', {'page_obj': page_obj})

def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('inventarios:lista_productos')  # Redirige a la lista de productos después de guardar
    else:
        form = ProductoForm()

    return render(request, 'inventarios/agregar_producto.html', {'form': form})


def lista_productos(request):
    productos = Producto.objects.all()  # Obtén todos los productos
    return render(request, 'inventarios/lista_productos.html', {'productos': productos})


def agregar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventarios:lista_categorias')  # Redirigir a la lista de categorías después de guardar
    else:
        form = CategoriaForm()
    
    return render(request, 'inventarios/agregar_categoria.html', {'form': form})



def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'inventarios/lista_categorias.html', {'categorias': categorias})


def productos_por_categoria(request, categoria_id):
    categoria = Categoria.objects.get(id=categoria_id)
    productos = Producto.objects.filter(categoria=categoria)  # Filtrar productos por categoría
    return render(request, 'inventarios/productos_por_categoria.html', {'productos': productos, 'categoria': categoria})

def ver_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'inventarios/ver_producto.html', {'producto': producto})


def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('inventarios:lista_productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'inventarios/editar_producto.html', {'form': form, 'producto': producto})


def crear_transferencia(request):
    if request.method == 'POST':
        form = TransferenciaForm(request.POST)
        if form.is_valid():
            # Obtener los datos del formulario
            transferencia = form.save(commit=False)
            
            # Verificar si hay suficiente inventario en la sucursal de origen
            inventario_origen = Inventario.objects.get(sucursal=transferencia.sucursal_origen, producto=transferencia.producto)
            if inventario_origen.cantidad < transferencia.cantidad:
                form.add_error('cantidad', 'No hay suficiente inventario en la sucursal de origen.')
            else:
                # Guardar la transferencia y actualizar inventarios
                transferencia.save()  # Esto ejecuta el método save personalizado en el modelo Transferencia
                return redirect('inventarios:lista_transferencias')  # Redirigir a una lista de transferencias o donde prefieras
    else:
        form = TransferenciaForm()

    return render(request, 'inventarios/crear_transferencia.html', {'form': form})

def lista_transferencias(request):
    transferencias = Transferencia.objects.all()
    return render(request, 'inventarios/lista_transferencias.html', {'transferencias': transferencias})

def lista_movimientos_inventario(request):
    movimientos = MovimientoInventario.objects.all().order_by('-fecha')  # Ordenados por fecha descendente
    return render(request, 'inventarios/lista_movimientos_inventario.html', {'movimientos': movimientos})