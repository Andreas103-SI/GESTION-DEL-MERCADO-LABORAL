#user/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .models import CustomUser

# Este módulo define las vistas para la gestión de usuarios.
# Incluye funciones para el registro de usuarios y vistas restringidas por roles.

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

# Vista para el registro de nuevos usuarios.
# Permite a los usuarios crear una cuenta y acceder al sistema.
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Vista para listar todos los usuarios.
# Solo accesible para usuarios con rol de 'admin'.
@role_required('admin')
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

# Vista para mostrar los detalles de un usuario específico.
# Solo accesible para usuarios con rol de 'admin'.
@role_required('admin')
def user_detail(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    return render(request, 'users/user_detail.html', {'user': user})

# Vista restringida a ciertos roles de usuario.
# Solo accesible para usuarios con roles de 'admin' o 'manager'.
@role_required('admin', 'manager')
def restricted_view(request):
    return render(request, 'restricted.html', {'message': 'Solo para Admins y Gestores'})

# Create your views here.
