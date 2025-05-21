# data_integration/urls.py
from django.urls import path
from . import views

app_name = 'data_integration'

urlpatterns = [
    path('', views.scrape_index, name='scrape_index'),
    path('linkedin/', views.scrape_linkedin_view, name='scrape_linkedin'),
    path('tecnoempleo/', views.scrape_tecnoempleo_view, name='scrape_tecnoempleo'),
    path('scrape-results/', views.scrape_results, name='scrape_results'),
    path('data-dashboard/', views.dashboard_view, name='data_dashboard'),  # Renombrado según tu instrucción
]