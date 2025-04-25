# job_platform/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

# Decorador para restringir el acceso a vistas según el rol del usuario.
# Solo permite el acceso a usuarios con roles específicos.
def role_required(*roles):
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para acceder.")
        return wrapper
    return decorator

# Vista para la página de inicio.
# Muestra un mensaje de bienvenida en la página principal.
def home(request):
    return render(request, 'home.html', {'message': '¡Hola, mundo!'})

# Vista restringida a ciertos roles de usuario.
# Solo accesible para usuarios con roles de 'admin' o 'manager'.
@role_required('admin', 'manager')
def restricted_view(request):
    return render(request, 'restricted.html', {'message': 'Solo para Admins y Gestores'})