# job_platform/urls.py
from django.contrib import admin
from django.urls import path, include
from .views import home, restricted_view

urlpatterns = [
    path('', home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('data/', include('data_integration.urls')),
    path('market-analysis/', include('market_analysis.urls', namespace='market_analysis')),
    path('projects/', include('projects.urls')),
    path('restricted/', restricted_view, name='restricted'),
    path('users/', include('users.urls')),
]