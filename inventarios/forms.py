from django import forms
from .models import Compra, Producto

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
        fields = ['nombre', 'descripcion', 'precio_compra', 'precio_venta', 'unidad_medida', 'categoria', 'sucursal', 'codigo_producto', 'impuesto', 'image']