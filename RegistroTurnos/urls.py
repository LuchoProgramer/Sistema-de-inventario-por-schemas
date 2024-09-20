from django.urls import path
from django.contrib.auth.views import LoginView
from .views import dashboard, usuario_creado_exitosamente, crear_usuario  # Eliminamos `registrar_empleado` si no es necesario

urlpatterns = [
    path('crear-usuario/', crear_usuario, name='crear_usuario'),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('usuario-creado/', usuario_creado_exitosamente, name='usuario_creado_exitosamente'),
]