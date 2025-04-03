from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html', {'message': '¡Hola, mundo!'})

@login_required
def restricted_view(request):
    return render(request, 'restricted.html')