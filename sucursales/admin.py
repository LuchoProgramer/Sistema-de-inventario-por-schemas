from django.contrib import admin
from .models import Sucursal, RazonSocial

admin.site.register(Sucursal)

@admin.register(RazonSocial)
class RazonSocialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc')
    search_fields = ('nombre', 'ruc')
    list_filter = ('nombre',)
    ordering = ('nombre',)
