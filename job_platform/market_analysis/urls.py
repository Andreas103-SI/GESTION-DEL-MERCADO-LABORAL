# market_analysis/urls.py
from django.urls import path
from .views import dashboard, update_scraper

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('update/', update_scraper, name='update_scraper'),
]