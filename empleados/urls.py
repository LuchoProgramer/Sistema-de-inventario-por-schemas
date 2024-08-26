# empleados/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView
from .views import registrar_empleado

urlpatterns = [
    path('registro/', registrar_empleado, name='registro'),
    path('login/', LoginView.as_view(template_name='empleados/login.html'), name='login'),
]
