"""inventario URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include  # Asegúrate de importar include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView  # Importar RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('registro-turnos/', include('RegistroTurnos.urls')),
    path('conteo/', include('conteo.urls')),
    path('ventas/', include('ventas.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('facturacion/', include('facturacion.urls')),
    path('inventarios/', include('inventarios.urls', namespace='inventarios')),
    path('reportes/', include('reportes.urls')),
    path('sucursales/', include('sucursales.urls')),
    path('compras/', include('inventarios.compras_urls')),

    # Redirigir la raíz '/' a '/registro-turnos/login/'
    path('', RedirectView.as_view(url='/registro-turnos/login/')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]  # Añadir la ruta de debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
