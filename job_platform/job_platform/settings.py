"""
Configuración de Django para el proyecto job_platform.

Generado por 'django-admin startproject'.

Para más información sobre este archivo, visita
https://docs.djangoproject.com/en/5.1/topics/settings/

Para la lista completa de configuraciones y sus valores, visita
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

# Importaciones necesarias para la configuración
from pathlib import Path
import os

# Construye rutas dentro del proyecto como BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuraciones de inicio rápido para desarrollo - no aptas para producción
# Ver https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# ADVERTENCIA DE SEGURIDAD: mantén la clave secreta usada en producción en secreto!
SECRET_KEY = 'django-insecure-(pf9$^f@#dyfyzowwz2yp*g7t*+cxh1kf4ti7bt$y=)zag79nj'

# ADVERTENCIA DE SEGURIDAD: no ejecutes con debug activado en producción!
DEBUG = True

ALLOWED_HOSTS = []  # Lista de hosts permitidos

# Definición de aplicaciones
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'projects',
    'market_analysis',
    'ai_module',
    'rolepermissions',
    'data_integration',
]

# Middleware de la aplicación
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'job_platform.urls'  # Configuración de URLs raíz

# Configuración de plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Directorio de plantillas
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

WSGI_APPLICATION = 'job_platform.wsgi.application'  # Configuración de WSGI

# Configuración de la base de datos
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'job_platform_db',  
        'USER': 'postgres',  
        'PASSWORD': 'andre103',  
        'HOST': 'localhost', 
        'PORT': '5432', 
    }
}

# Validación de contraseñas
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internacionalización
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = 'en-us'  # Código de idioma
TIME_ZONE = 'UTC'  # Zona horaria
USE_I18N = True  # Habilitar internacionalización
USE_TZ = True  # Usar zonas horarias

# Archivos estáticos (CSS, JavaScript, Imágenes)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = '/static/'  # URL para archivos estáticos
STATICFILES_DIRS = [BASE_DIR / 'static']  # Directorios de archivos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Directorio raíz para archivos estáticos

# Configuración del modelo de usuario personalizado
AUTH_USER_MODEL = 'users.CustomUser'

# Tipo de campo de clave primaria por defecto
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'  # Redirige a home tras login
LOGOUT_REDIRECT_URL = '/'  # Redirige a home tras logout

# Configuración de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}