from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import dashboard, usuario_creado_exitosamente, crear_usuario, asignar_turno, turno_exito, sin_sucursales

urlpatterns = [
    path('crear-usuario/', crear_usuario, name='crear_usuario'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),  # Añadir esta línea para el logout
    path('dashboard/', dashboard, name='dashboard'),
    path('usuario-creado/', usuario_creado_exitosamente, name='usuario_creado_exitosamente'),
    path('turno-exito/<int:turno_id>/', turno_exito, name='turno_exito'),
    path('sin_sucursales/', sin_sucursales, name='sin_sucursales'),
]