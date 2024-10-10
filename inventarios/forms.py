from django import forms
from .models import Compra, Producto, Categoria, Transferencia, Presentacion
from sucursales.models import Sucursal

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['sucursal', 'producto', 'cantidad', 'precio_unitario']
        widgets = {
            'sucursal': forms.Select(attrs={'class': 'form-control'}),
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'unidad_medida', 'categoria', 'sucursal', 'codigo_producto', 'impuesto', 'image']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'sucursal': forms.Select(attrs={'class': 'form-control'}),
            'codigo_producto': forms.TextInput(attrs={'class': 'form-control'}),
            'impuesto': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


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
    
