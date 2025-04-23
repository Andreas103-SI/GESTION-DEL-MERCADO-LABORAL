# job_platform/urls.py
from django.contrib import admin
from django.urls import path, include
from .views import home, restricted_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
    path('restricted/', restricted_view, name='restricted'),
    path('projects/', include('projects.urls')),  # Cambié '' a 'projects/' para evitar conflictos
    path('data/', include('data_integration.urls')),
    path('market-analysis/', include('market_analysis.urls', namespace='market_analysis')),
]