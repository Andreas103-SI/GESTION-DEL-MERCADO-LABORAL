# data_integration/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.scrape_index, name='scrape_index'),
    path('linkedin/', views.scrape_linkedin_view, name='scrape_linkedin'),
    path('tecnoempleo/', views.scrape_tecnoempleo_view, name='scrape_tecnoempleo'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]