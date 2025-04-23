"""
Controlador base con funcionalidad común para todos los controladores.
"""
import os
import django
from django.conf import settings

def setup_django():
    """Configura el entorno de Django para uso independiente."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
    django.setup()

class BaseController:
    """Clase controlador base con funcionalidad común."""
    
    def __init__(self):
        """Inicializa el controlador."""
        setup_django()
    
    def validate_required_fields(self, data, required_fields):
        """Valida que todos los campos requeridos estén presentes en los datos."""
        return all(field in data and data[field] for field in required_fields)
    
    def handle_error(self, error):
        """Maneja y registra errores."""
        print(f"Error: {str(error)}")
        return str(error) 