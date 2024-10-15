from django.shortcuts import render, redirect, get_object_or_404
from .models import Compra, Proveedor, DetalleCompra, Inventario, Producto, MovimientoInventario, Presentacion,Categoria
from sucursales.models import Sucursal
from .forms import CompraForm, DetalleCompraForm, CompraXMLForm
from django.forms import inlineformset_factory
from django.http import JsonResponse
import pandas as pd
from django import forms


def lista_compras(request):
    compras = Compra.objects.all()
    return render(request, 'compras/lista_compras.html', {'compras': compras})

def crear_compra_con_productos(request):
    # Especificamos el prefijo 'detalles' al crear el formset
    DetalleCompraFormSet = inlineformset_factory(
        Compra, DetalleCompra, form=DetalleCompraForm, extra=1
    )
    
    if request.method == 'POST':
        print("Método POST recibido")
        print(f"Datos POST: {request.POST}")
        
        compra_form = CompraForm(request.POST)
        # Añadimos el prefijo al instanciar el formset con los datos POST
        formset = DetalleCompraFormSet(request.POST, prefix='detalles')
        
        if compra_form.is_valid() and formset.is_valid():
            print("Formulario de compra válido")
            compra = compra_form.save()
            
            detalles = formset.save(commit=False)
            print(f"Se están procesando {len(detalles)} detalles")
            for detalle in detalles:
                print(f"Guardando detalle: Producto {detalle.producto}, Cantidad: {detalle.cantidad}")
                detalle.compra = compra
                detalle.save()
            
            return redirect('compras:lista_compras')
        else:
            print("Errores en la validación de los formularios")
            print(f"Errores en el formulario de compra: {compra_form.errors}")
            print(f"Errores en el formset: {formset.errors}")
    
    else:
        print("Método GET recibido")
        compra_form = CompraForm()
        # Añadimos el prefijo al instanciar el formset vacío
        formset = DetalleCompraFormSet(prefix='detalles')

    return render(request, 'compras/crear_compra_con_productos.html', {
        'compra_form': compra_form,
        'formset': formset
    })




def detalle_compra(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)
    detalles = compra.detalles.all()  # Relación con los DetalleCompra
    return render(request, 'compras/detalle_compra.html', {'compra': compra, 'detalles': detalles})


import xml.etree.ElementTree as ET
from django.shortcuts import render, redirect
from .models import Compra, Proveedor, DetalleCompra
from django.utils import timezone


def procesar_compra_xml(request):
    if request.method == 'POST':
        form = CompraXMLForm(request.POST, request.FILES)
        if form.is_valid():
            sucursal = form.cleaned_data['sucursal']
            archivo_xml = request.FILES['archivo_xml']

            # Leer el archivo XML
            tree = ET.parse(archivo_xml)
            root = tree.getroot()

            # Obtener información del proveedor
            razon_social_element = root.find('.//razonSocial')
            razon_social = razon_social_element.text if razon_social_element is not None else "Sin razón social"
            
            ruc_element = root.find('.//ruc')
            ruc = ruc_element.text if ruc_element is not None else "0000000000"

            proveedor, created = Proveedor.objects.get_or_create(
                nombre=razon_social,
                ruc=ruc
            )

            # Obtener la fecha de emisión o usar la fecha actual
            fecha_emision_element = root.find('.//fechaEmision')
            fecha_emision = fecha_emision_element.text if fecha_emision_element is not None else timezone.now()

            # Obtener los totales de la compra
            total_sin_impuestos_element = root.find('.//totalSinImpuestos')
            total_sin_impuestos = float(total_sin_impuestos_element.text) if total_sin_impuestos_element is not None else 0.0

            total_con_impuestos_element = root.find('.//importeTotal')
            total_con_impuestos = float(total_con_impuestos_element.text) if total_con_impuestos_element is not None else 0.0

            # Crear la compra (una sola compra para varios productos)
            compra = Compra.objects.create(
                proveedor=proveedor,
                sucursal=sucursal,
                fecha_emision=fecha_emision,
                total_sin_impuestos=total_sin_impuestos,
                total_con_impuestos=total_con_impuestos,
            )

            # Procesar los productos y agregarlos a la misma compra
            for detalle in root.findall('.//detalle'):
                # Extraer los valores del producto
                codigo_producto_element = detalle.find('codigoPrincipal')
                codigo_producto = codigo_producto_element.text if codigo_producto_element is not None else "Sin código"

                descripcion_element = detalle.find('descripcion')
                descripcion = descripcion_element.text if descripcion_element is not None else "Sin descripción"

                cantidad_element = detalle.find('cantidad')
                cantidad = float(cantidad_element.text) if cantidad_element is not None else 0

                precio_unitario_element = detalle.find('precioUnitario')
                precio_unitario = float(precio_unitario_element.text) if precio_unitario_element is not None else 0.0

                precio_total_sin_impuesto_element = detalle.find('precioTotalSinImpuesto')
                precio_total_sin_impuesto = float(precio_total_sin_impuesto_element.text) if precio_total_sin_impuesto_element is not None else 0.0

                descuento_element = detalle.find('descuento')
                descuento = float(descuento_element.text) if descuento_element is not None else 0.0

                # Buscar o crear el producto en la base de datos
                producto, created = Producto.objects.get_or_create(
                    codigo=codigo_producto,
                    nombre=descripcion
                )

                # Crear el detalle de compra
                DetalleCompra.objects.create(
                    compra=compra,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    total_por_producto=precio_total_sin_impuesto - descuento
                )

                print(f"Producto {codigo_producto} procesado: {cantidad} unidades a {precio_unitario} cada una.")

            print("Compra procesada exitosamente.")
            return redirect('compras:lista_compras')
        else:
            print("Formulario no es válido:", form.errors)

    else:
        form = CompraXMLForm()

    return render(request, 'compras/subir_xml.html', {'form': form})



import pandas as pd
from django.shortcuts import render, redirect
from inventarios.models import Producto, Presentacion
from sucursales.models import Sucursal

import traceback  # Para capturar el stack trace en caso de error

from django.db import transaction


def normalizar_clave(clave):
    """Elimina espacios y normaliza los nombres de las claves."""
    return str(clave).strip().lower()

import unicodedata

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import unicodedata

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import unicodedata

def normalizar_texto(texto):
    """Elimina acentos, convierte a minúsculas y elimina espacios extra."""
    texto = texto.strip().lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto

class UploadFileForm(forms.Form):
    archivo = forms.FileField(label='Seleccionar archivo (.xlsx)', help_text='El archivo debe ser .xlsx')

def cargar_productos(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data['archivo']

            if not archivo.name.endswith('.xlsx'):
                return render(request, 'compras/cargar_productos.html', {'form': form, 'error': 'El archivo debe ser .xlsx'})

            try:
                df = pd.read_excel(archivo)
                print("Columnas detectadas:", df.columns.tolist())

                columnas_sucursales = [
                    col for col in df.columns if col.lower().startswith('sucursal: ')
                ]

                if not columnas_sucursales:
                    print("No se detectaron columnas de sucursales.")
                    return render(request, 'compras/cargar_productos.html', {'form': form, 'error': 'No se detectaron columnas de sucursales.'})

                for index, row in df.iterrows():
                    print(f"\nProcesando fila {index + 1}...")
                    print(f"Valores de la fila {index + 1}: {row.to_dict()}")

                    codigo = row.get('Código')
                    nombre = row.get('Nombre')
                    categoria = row.get('Categoría')

                    if pd.isna(codigo) or pd.isna(nombre) or pd.isna(categoria):
                        print(f"Fila {index + 1} ignorada: Falta Código, Nombre o Categoría.")
                        continue

                    categoria_obj, _ = Categoria.objects.get_or_create(nombre=categoria)
                    producto, _ = Producto.objects.update_or_create(
                        codigo_producto=codigo,
                        defaults={'nombre': nombre, 'categoria': categoria_obj}
                    )
                    print(f"Producto actualizado: {producto.nombre}")

                    for sucursal_col in columnas_sucursales:
                        if row[sucursal_col].strip().lower() == 'si':
                            nombre_sucursal = sucursal_col.replace('Sucursal: ', '').strip()

                            try:
                                sucursal = Sucursal.objects.get(nombre__icontains=nombre_sucursal)
                                print(f"  Sucursal encontrada: {sucursal.nombre}")
                            except ObjectDoesNotExist:
                                print(f"  Error: La sucursal '{nombre_sucursal}' no existe en la base de datos.")
                                continue

                            with transaction.atomic():
                                for precio_tipo in ['Precio1', 'Precio2', 'Precio4']:
                                    if precio_tipo in row:
                                        print(f"    Verificando {precio_tipo}...")
                                        precio = row.get(precio_tipo)
                                        if pd.notna(precio):
                                            cantidad = row.get('Cantidad', 1)
                                            print(f"    {precio_tipo} válido: {precio}, Cantidad: {cantidad}")

                                            try:
                                                presentacion = Presentacion(
                                                    producto=producto,
                                                    nombre_presentacion=precio_tipo.replace('Precio', 'Precio '),
                                                    sucursal=sucursal,
                                                    cantidad=cantidad,
                                                    precio=precio
                                                )
                                                presentacion.save()
                                                print(f"    Presentación creada: {presentacion.nombre_presentacion}")

                                                if Presentacion.objects.filter(
                                                        producto=producto,
                                                        nombre_presentacion=precio_tipo.replace('Precio', 'Precio '),
                                                        sucursal=sucursal).exists():
                                                    print(f"    Confirmación: Presentación guardada correctamente.")
                                                else:
                                                    print(f"    Error: La presentación no se encuentra en la base de datos.")
                                            except Exception as e:
                                                print(f"    Error al guardar la presentación: {str(e)}")
                                        else:
                                            print(f"    {precio_tipo} es NaN o no válido.")
                                    else:
                                        print(f"    {precio_tipo} no encontrado en la fila.")

                return render(request, 'compras/cargar_productos.html', {'form': form, 'mensaje': 'Archivo cargado exitosamente.'})

            except Exception as e:
                print(f"Error al procesar el archivo: {str(e)}")
                traceback.print_exc()
                return render(request, 'compras/cargar_productos.html', {'form': form, 'error': f'Error al procesar el archivo: {str(e)}'})

    else:
        form = UploadFileForm()

    return render(request, 'compras/cargar_productos.html', {'form': form})