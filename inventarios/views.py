from django.shortcuts import render, redirect
from .models import Producto, Inventario, Compra, Categoria, Transferencia, MovimientoInventario, Presentacion
from django.shortcuts import get_object_or_404
from .forms import CompraForm, ProductoForm, CategoriaForm, TransferenciaForm
from sucursales.models import Sucursal
from django.core.paginator import Paginator
from django.contrib import messages
import pandas as pd
from django.http import HttpResponse
from facturacion.models import Impuesto
from .forms import UploadFileForm
from django.urls import reverse
from .forms import PresentacionMultipleForm
from django.forms import inlineformset_factory
from django.http import JsonResponse

# Creamos el formset para las presentaciones
PresentacionFormSet = inlineformset_factory(
    Producto, 
    Presentacion, 
    form=PresentacionMultipleForm, 
    extra=1,
    fields=['nombre_presentacion', 'cantidad', 'precio', 'sucursal']
)

# @login_required
def agregar_presentaciones_multiples(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = PresentacionMultipleForm(request.POST)
        if form.is_valid():
            sucursales = form.cleaned_data['sucursales']
            nombre_presentacion = form.cleaned_data['nombre_presentacion']

            # Almacenar errores si alguna presentación ya existe
            errores = []

            # Iterar sobre las sucursales seleccionadas
            presentaciones_creadas = []  # Guardar las presentaciones que se crearon

            for sucursal in sucursales:
                print(f"Procesando sucursal: {sucursal.nombre}")

                # Verificar si ya existe la presentación en la misma sucursal
                if Presentacion.objects.filter(
                    producto=producto,
                    nombre_presentacion=nombre_presentacion,
                    sucursal=sucursal
                ).exists():
                    error = f'La presentación "{nombre_presentacion}" ya existe en {sucursal.nombre}.'
                    print(error)
                    errores.append(error)
                    continue  # Saltar esta iteración si ya existe

                # Crear la nueva presentación si no existe
                nueva_presentacion = Presentacion(
                    producto=producto,
                    nombre_presentacion=nombre_presentacion,
                    cantidad=form.cleaned_data['cantidad'],
                    precio=form.cleaned_data['precio'],
                    sucursal=sucursal
                )
                nueva_presentacion.save()
                print(f"Presentación creada en sucursal: {sucursal.nombre}")
                presentaciones_creadas.append(nueva_presentacion)

            # Si hubo errores, devolverlos como respuesta
            if errores:
                return JsonResponse({
                    'success': False,
                    'error': ' | '.join(errores)  # Mostrar todos los errores encontrados
                }, status=400)

            # Devolver una respuesta exitosa con los datos de todas las presentaciones creadas
            presentaciones_data = [
                {
                    'id': p.id,
                    'nombre_presentacion': p.nombre_presentacion,
                    'cantidad': p.cantidad,
                    'precio': p.precio,
                    'sucursal': p.sucursal.nombre
                }
                for p in presentaciones_creadas
            ]

            return JsonResponse({
                'success': True,
                'presentaciones': presentaciones_data  # Devolver las presentaciones creadas
            })

        else:
            print(f"Errores en el formulario: {form.errors}")
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    # Lógica para el método GET
    presentaciones_existentes = Presentacion.objects.filter(producto=producto)
    form = PresentacionMultipleForm()

    return render(request, 'inventarios/agregar_presentaciones_multiples.html', {
        'form': form,
        'producto': producto,
        'presentaciones_existentes': presentaciones_existentes,
    })

def eliminar_presentacion(request, presentacion_id):
    if request.method == 'POST':
        try:
            presentacion = Presentacion.objects.get(id=presentacion_id)
            presentacion.delete()
            return JsonResponse({'success': True})
        except Presentacion.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Presentación no encontrada.'})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})


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


from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

def ver_inventario(request, sucursal_id):
    # Obtener la sucursal seleccionada
    sucursal = get_object_or_404(Sucursal, id=sucursal_id)

    # Obtener el inventario para esa sucursal, con el producto relacionado precargado
    inventarios = Inventario.objects.filter(sucursal=sucursal).select_related('producto')

    # Paginación del inventario, 10 elementos por página
    paginator = Paginator(inventarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventarios/ver_inventario.html', {
        'sucursal': sucursal,
        'inventarios': page_obj,  # Cambié 'inventario' a 'inventarios' y añadí paginación
    })



def agregar_producto_inventario(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        sucursal_id = request.POST.get('sucursal_id')
        cantidad = request.POST.get('cantidad')

        # Validar que 'cantidad' no sea nulo ni vacío
        if not cantidad:
            messages.error(request, 'La cantidad es requerida.')
            return redirect('inventarios:agregar_producto_inventario')

        # Intentar convertir 'cantidad' a entero y manejar el error si no es válido
        try:
            cantidad = int(cantidad)
        except ValueError:
            messages.error(request, 'La cantidad debe ser un número válido.')
            return redirect('inventarios:agregar_producto_inventario')

        # Ahora puedes proceder a guardar la cantidad en el inventario
        try:
            inventario, created = Inventario.objects.get_or_create(
                producto_id=producto_id, 
                sucursal_id=sucursal_id,
                defaults={'cantidad': cantidad}
            )
            if not created:
                inventario.cantidad += cantidad  # Sumar cantidad si ya existe el producto
                inventario.save()

            messages.success(request, 'Producto agregado al inventario.')
        except Exception as e:
            messages.error(request, f'Error al agregar el producto: {e}')
        
        return redirect('inventarios:ver_inventario', sucursal_id=sucursal_id)

    # Si el request es GET, mostramos el formulario de agregar producto
    else:
        # Aquí puedes cargar cualquier dato necesario para el formulario, como la lista de productos o sucursales
        productos = Producto.objects.all()
        sucursales = Sucursal.objects.all()
        return render(request, 'inventarios/agregar_producto.html', {'productos': productos, 'sucursales': sucursales})



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


def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            form.save_m2m()  # Guarda las relaciones Many-to-Many
            messages.success(request, 'Producto agregado exitosamente.')
            return redirect('inventarios:lista_productos')
        else:
            messages.error(request, 'Por favor, corrige los errores a continuación.')
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
    presentaciones = Presentacion.objects.filter(producto=producto)  # Obtener presentaciones asociadas
    return render(request, 'inventarios/ver_producto.html', {
        'producto': producto,
        'presentaciones': presentaciones,  # Pasar las presentaciones al template
    })


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

#OJO
# Cargar productos con Excel
def cargar_productos(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                # Leer el archivo Excel
                df = pd.read_excel(file)

                # Definir los campos obligatorios y opcionales
                required_columns = ['Nombre', 'Precio Compra', 'Precio Venta', 'Nombre Presentación', 'Cantidad Presentación']
                optional_columns = ['Descripción', 'Unidad de Medida', 'Categoria', 'Sucursal', 'Código Producto', 'Stock Mínimo']
                allowed_columns = required_columns + optional_columns

                # Verifica que los campos obligatorios estén presentes
                for column in required_columns:
                    if column not in df.columns:
                        return HttpResponse(f"El archivo debe contener la columna obligatoria: {column}")

                # Filtrar solo las columnas permitidas (ignorar las que no correspondan al modelo)
                df = df[[col for col in df.columns if col in allowed_columns]]

                # Procesar cada fila del DataFrame
                for index, row in df.iterrows():
                    try:
                        # Asignar automáticamente el impuesto del 15%
                        impuesto = Impuesto.objects.get(porcentaje=15.0)

                        # Obtener o crear categoría
                        categoria = None
                        if row.get('Categoria'):
                            categoria, _ = Categoria.objects.get_or_create(nombre=row['Categoria'])

                        # Obtener o crear sucursal
                        sucursal = None
                        if row.get('Sucursal'):
                            sucursal = Sucursal.objects.filter(nombre=row['Sucursal']).first()
                            if not sucursal:
                                return HttpResponse(f"Error: La sucursal {row['Sucursal']} no existe.")

                        # Crear el producto sin precio
                        producto = Producto.objects.create(
                            nombre=row['Nombre'],  # Campo obligatorio
                            precio_compra=row['Precio Compra'],  # Campo obligatorio
                            impuesto=impuesto,  # Se asigna automáticamente el 15%
                            descripcion=row.get('Descripción', ''),  # Si no está, se asigna una cadena vacía
                            unidad_medida=row.get('Unidad de Medida', ''),  # Si no está, se asigna una cadena vacía
                            categoria=categoria,  # Asociar a la categoría
                            sucursal=sucursal,  # Asociar a la sucursal
                            codigo_producto=row.get('Código Producto', None),  # Si no está, se asigna None
                            stock_minimo=row.get('Stock Mínimo', 0),  # Si no está, se asigna 0 como valor por defecto
                        )

                        # Crear la presentación del producto
                        Presentacion.objects.create(
                            producto=producto,
                            nombre_presentacion=row['Nombre Presentación'],  # Nombre de la presentación (Ej. Unidad, Caja de 10)
                            cantidad=row['Cantidad Presentación'],  # Cantidad de unidades en la presentación
                            precio=row['Precio Venta'],  # Precio asignado a la presentación
                        )
                    except Exception as e:
                        return HttpResponse(f"Error al procesar la fila {index + 1}: {e}")

                return HttpResponse("Productos y presentaciones cargados con éxito")
            except Exception as e:
                return HttpResponse(f"Error al cargar productos: {e}")
    else:
        form = UploadFileForm()
    return render(request, 'inventarios/cargar_productos.html', {'form': form})

from .forms import InventarioForm

def agregar_inventario_manual(request):
    sucursal_id = request.GET.get('sucursal')  # Obtener la sucursal desde el query string
    sucursal = get_object_or_404(Sucursal, id=sucursal_id)

    if request.method == 'POST':
        form = InventarioForm(request.POST)
        if form.is_valid():
            inventario, created = Inventario.objects.get_or_create(
                producto=form.cleaned_data['producto'],
                sucursal=sucursal,
                defaults={'cantidad': form.cleaned_data['cantidad']}
            )
            if not created:
                inventario.cantidad += form.cleaned_data['cantidad']
            inventario.save()
            return redirect('ver_inventario', sucursal_id=sucursal.id)
    else:
        form = InventarioForm()

    return render(request, 'inventarios/agregar_inventario_manual.html', {'form': form, 'sucursal': sucursal})


def cargar_inventario_excel(request):
    sucursal_id = request.GET.get('sucursal')  # Obtener la sucursal desde el query string
    sucursal = get_object_or_404(Sucursal, id=sucursal_id)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file)

            required_columns = ['Producto', 'Cantidad']
            for column in required_columns:
                if column not in df.columns:
                    return HttpResponse(f"El archivo debe contener la columna: {column}")

            for index, row in df.iterrows():
                producto = Producto.objects.get(nombre=row['Producto'])
                inventario, created = Inventario.objects.get_or_create(
                    producto=producto,
                    sucursal=sucursal,
                    defaults={'cantidad': row['Cantidad']}
                )
                # Si el inventario ya existe, sobrescribe la cantidad en lugar de sumarla
                if not created:
                    inventario.cantidad = row['Cantidad']
                inventario.save()

            return redirect(reverse('inventarios:ver_inventario', args=[sucursal.id]))
    else:
        form = UploadFileForm()

    return render(request, 'inventarios/cargar_inventario_excel.html', {'form': form, 'sucursal': sucursal})


