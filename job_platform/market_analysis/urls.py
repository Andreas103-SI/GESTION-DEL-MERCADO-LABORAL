from django.urls import path
from .views import dashboard  # Cambiado de 'market_dashboard' a 'dashboard'

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
]