#user/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .models import CustomUser

def role_required(*roles):
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para acceder.")
        return wrapper
    return decorator

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

@role_required('admin')
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

@role_required('admin')
def user_detail(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    return render(request, 'users/user_detail.html', {'user': user})

@role_required('admin', 'manager')
def restricted_view(request):
    return render(request, 'restricted.html', {'message': 'Solo para Admins y Gestores'})

# Create your views here.
