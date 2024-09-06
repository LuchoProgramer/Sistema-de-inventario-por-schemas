from django.shortcuts import render, redirect
from .models import Producto, Inventario, Sucursal, Compra, Categoria, Transferencia, MovimientoInventario
from django.shortcuts import get_object_or_404
from .forms import CompraForm, ProductoForm, CategoriaForm, TransferenciaForm


def seleccionar_sucursal(request):
    empleado = request.user.empleado
    sucursales = empleado.sucursales.all()  # Obtener todas las sucursales del empleado

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
        nueva_cantidad = int(request.POST.get('nueva_cantidad'))

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
        form = CompraForm()

    return render(request, 'inventarios/agregar_compra.html', {'form': form})


def ver_compras(request):
    compras = Compra.objects.all().order_by('-fecha')  # Ordenar por fecha más reciente
    return render(request, 'inventarios/ver_compras.html', {'compras': compras})

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