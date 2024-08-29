# empleados/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView
from .views import registrar_empleado, dashboard, usuario_creado_exitosamente

urlpatterns = [
    path('registro/', registrar_empleado, name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('usuario-creado/', usuario_creado_exitosamente, name='usuario_creado_exitosamente'),
]