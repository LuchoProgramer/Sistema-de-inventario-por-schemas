# conteo/admin.py
from django.contrib import admin
from .models import ConteoDiario

class ConteoDiarioAdmin(admin.ModelAdmin):
    list_display = ['sucursal', 'empleado', 'fecha_conteo', 'producto', 'cantidad_contada']
    list_filter = ['sucursal', 'fecha_conteo']
    search_fields = ['producto__nombre', 'empleado__username', 'sucursal__nombre']

admin.site.register(ConteoDiario, ConteoDiarioAdmin)
