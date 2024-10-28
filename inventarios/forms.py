from django import forms
from .models import Compra, Producto, Categoria, Transferencia, Presentacion, DetalleCompra, Proveedor
from sucursales.models import Sucursal
from facturacion.models import Impuesto

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['sucursal', 'proveedor', 'metodo_pago', 'estado', 'fecha_emision', 'total_sin_impuestos', 'total_con_impuestos']
        widgets = {
            'sucursal': forms.Select(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_emision': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_sin_impuestos': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'total_con_impuestos': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }


class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def clean_precio_unitario(self):
        precio_unitario = self.cleaned_data.get('precio_unitario')

        # Verificar que el precio_unitario no sea nulo o negativo
        if precio_unitario is None or precio_unitario <= 0:
            raise forms.ValidationError("El precio unitario debe ser un número positivo.")

        return precio_unitario




class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'descripcion', 'unidad_medida', 'categoria',
            'sucursales', 'codigo_producto', 'impuesto', 'image'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'sucursales': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'codigo_producto': forms.TextInput(attrs={'class': 'form-control'}),
            'impuesto': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_codigo_producto(self):
        codigo = self.cleaned_data.get('codigo_producto')
        if Producto.objects.filter(codigo_producto=codigo).exists():
            raise forms.ValidationError(f"El código '{codigo}' ya está en uso.")
        return codigo


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']

class TransferenciaForm(forms.ModelForm):
    class Meta:
        model = Transferencia
        fields = ['sucursal_origen', 'sucursal_destino', 'producto', 'cantidad']


class UploadFileForm(forms.Form):
    file = forms.FileField()

from .models import Inventario

class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['producto', 'sucursal', 'cantidad']


class PresentacionMultipleForm(forms.Form):
    nombre_presentacion = forms.CharField(max_length=100, label="Nombre de la Presentación")
    cantidad = forms.IntegerField(min_value=1, label="Cantidad por Presentación")
    precio = forms.DecimalField(max_digits=10, decimal_places=2, label="Precio")
    sucursales = forms.ModelMultipleChoiceField(queryset=Sucursal.objects.all(), label="Sucursales", widget=forms.CheckboxSelectMultiple)
    

class CompraXMLForm(forms.Form):
    sucursal = forms.ModelChoiceField(queryset=Sucursal.objects.all(), label="Sucursal")
    archivo_xml = forms.FileField(label="Subir archivo XML")



class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'ruc', 'direccion', 'telefono', 'email', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ruc': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }