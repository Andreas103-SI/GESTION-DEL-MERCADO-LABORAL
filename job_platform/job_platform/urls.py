# job_platform/urls.py
from django.contrib import admin
from django.urls import path, include
from .views import home, restricted_view

urlpatterns = [
    path('', home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('data-integration/', include('data_integration.urls', namespace='data_integration')),  # URL actualizada
    path('market-analysis/', include('market_analysis.urls', namespace='market_analysis')),
    path('projects/', include('projects.urls')),
    path('restricted/', restricted_view, name='restricted'),
    path('users/', include('users.urls')),
    path('ai/', include('ai_module.urls', namespace='ai_module')),  # Nuevo módulo AI
]