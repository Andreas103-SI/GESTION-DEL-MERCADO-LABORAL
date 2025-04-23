"""
Controlador para operaciones del modelo User y autenticación.
"""
from .base import BaseController
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

class UserController(BaseController):
    """Controlador para operaciones de usuarios."""
    
    def __init__(self):
        """Inicializa el controlador."""
        super().__init__()
        self.required_fields = ['username', 'email']
    
    def create(self, data):
        """Crea un nuevo usuario."""
        try:
            if not self.validate_required_fields(data, self.required_fields):
                return False, "Todos los campos son requeridos"
            
            if 'password' not in data:
                return False, "La contraseña es requerida"
            
            if User.objects.filter(username=data['username']).exists():
                return False, "El nombre de usuario ya existe"
            
            if User.objects.filter(email=data['email']).exists():
                return False, "El correo electrónico ya existe"
            
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            return True, user
        except Exception as e:
            return False, self.handle_error(e)
    
    def read(self, user_id=None):
        """Lee usuario(s)."""
        try:
            if user_id:
                return True, User.objects.get(id=user_id)
            return True, User.objects.all()
        except User.DoesNotExist:
            return False, "Usuario no encontrado"
        except Exception as e:
            return False, self.handle_error(e)
    
    def update(self, user_id, data):
        """Actualiza un usuario."""
        try:
            user = User.objects.get(id=user_id)
            
            if 'username' in data and data['username'] != user.username:
                if User.objects.filter(username=data['username']).exists():
                    return False, "El nombre de usuario ya existe"
            
            if 'email' in data and data['email'] != user.email:
                if User.objects.filter(email=data['email']).exists():
                    return False, "El correo electrónico ya existe"
            
            for key, value in data.items():
                if key == 'password':
                    user.set_password(value)
                else:
                    setattr(user, key, value)
            
            user.save()
            return True, user
        except User.DoesNotExist:
            return False, "Usuario no encontrado"
        except Exception as e:
            return False, self.handle_error(e)
    
    def delete(self, user_id):
        """Elimina un usuario."""
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return True, "Usuario eliminado exitosamente"
        except User.DoesNotExist:
            return False, "Usuario no encontrado"
        except Exception as e:
            return False, self.handle_error(e)
    
    def authenticate_user(self, username, password):
        """Autentica un usuario."""
        try:
            user = authenticate(username=username, password=password)
            if user is not None:
                return True, user
            return False, "Credenciales inválidas"
        except Exception as e:
            return False, self.handle_error(e)
    
    def login_user(self, request, user):
        """Inicia sesión de un usuario."""
        try:
            login(request, user)
            return True, "Inicio de sesión exitoso"
        except Exception as e:
            return False, self.handle_error(e)
    
    def logout_user(self, request):
        """Cierra sesión de un usuario."""
        try:
            logout(request)
            return True, "Cierre de sesión exitoso"
        except Exception as e:
            return False, self.handle_error(e) 