"""
Django settings for inventario project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-r17i1lu%najs3-&%$sz1uu6ty0q4dlkyjck96lkn7ts&t)e(7^"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'sucursales',
    'RegistroTurnos',
    'inventarios',
    'ventas',
    'conteo',
    'facturacion',
    'reportes.apps.ReportesConfig',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "inventario.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Le indicamos a Django que busque aquí las plantillas
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = "inventario.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventario_db',  # El nombre de la base de datos que creaste
        'USER': 'postgres',  # El usuario que creaste (o 'postgres' si decides usar el predeterminado)
        'PASSWORD': 'Camilucho1990',  # La contraseña del usuario
        'HOST': 'localhost',  # Mantén 'localhost' si estás trabajando localmente
        'PORT': '5432',  # El puerto por defecto de PostgreSQL
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Guayaquil"  # Cambia UTC por America/Guayaquil

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'

# Este ajuste le dice a Django dónde buscar archivos estáticos adicionales
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Aquí define la carpeta estática en la raíz del proyecto
]

# Para producción, define STATIC_ROOT. Aquí es donde Django almacenará todos los archivos estáticos recopilados.
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Configuración de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'luchoviteri1990@gmail.com'
EMAIL_HOST_PASSWORD = 'ytjriexvpwadrjtd'

# Configuración de Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # URL del broker de Redis
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Backend opcional para almacenar los resultados de las tareas
CELERY_ACCEPT_CONTENT = ['json']  # Aceptar solo formatos de contenido JSON
CELERY_TASK_SERIALIZER = 'json'  # Serializador de tareas
CELERY_RESULT_SERIALIZER = 'json'  # Serializador de resultados
CELERY_TIMEZONE = 'America/Guayaquil'  # Ajusta según tu zona horaria, si es necesario


LOGIN_URL = '/empleados/dashboard/'
LOGIN_REDIRECT_URL = '/empleados/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'


import os

# La URL que se usará para acceder a los archivos multimedia en tu aplicación.
MEDIA_URL = '/media/'

# La ruta absoluta en el sistema de archivos donde se guardarán los archivos cargados por los usuarios.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


from logging.handlers import RotatingFileHandler

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'ERROR',  # Solo mostrar errores graves en la consola
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',  # Registrar desde 'INFO' en adelante en el archivo
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 3,  # Máximo 3 MB por archivo
            'backupCount': 2,  # Mantener un máximo de 2 archivos (1 actual y 1 de respaldo)
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',  # Solo registrar eventos importantes
            'propagate': True,
        },
    },
}
