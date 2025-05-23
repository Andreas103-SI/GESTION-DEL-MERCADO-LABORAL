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
from dotenv import load_dotenv
from django.db.backends.postgresql.creation import DatabaseCreation

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Construye rutas dentro del proyecto como BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuraciones de inicio rápido para desarrollo - no aptas para producción
# Ver https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# ADVERTENCIA DE SEGURIDAD: mantén la clave secreta usada en producción en secreto!
SECRET_KEY = os.getenv('SECRET_KEY')

# ADVERTENCIA DE SEGURIDAD: no ejecutes con debug activado en producción!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # Lista de hosts permitidos

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
# job_platform/settings.py
class CustomDatabaseCreation(DatabaseCreation):
    def _create_test_db(self, verbosity, autoclobber, keepdb=False):
        # Llamar al método original de la clase base
        test_db_name = super()._create_test_db(verbosity, autoclobber, keepdb)
        # Habilitar la extensión citext en la base de datos de prueba
        with self.connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS citext;")
        return test_db_name

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'job_platform_db',
        'USER': 'postgres',
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME': 'test_job_platform_db',
        },
    }
}

from django.db import connections
connections.databases['default']['TEST']['CREATION_CLASS'] = CustomDatabaseCreation

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