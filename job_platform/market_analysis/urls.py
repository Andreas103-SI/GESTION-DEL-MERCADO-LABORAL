# market_analysis/urls.py
from django.urls import path
from . import views

app_name = 'market_analysis'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update-scraper/', views.update_scraper, name='update_scraper'),
]