from django.shortcuts import render, redirect
from .models import Producto, Inventario, Sucursal, Compra
from django.shortcuts import get_object_or_404
from .forms import CompraForm, ProductoForm


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