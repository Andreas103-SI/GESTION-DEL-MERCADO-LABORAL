# data_integration/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.scrape_index, name='scrape_index'),
    path('scrape-linkedin/', views.scrape_linkedin, name='scrape_linkedin'),
    path('scrape-infojobs/', views.scrape_infojobs, name='scrape_infojobs'),
    path('scrape-tecnoempleo/', views.scrape_tecnoempleo, name='scrape_tecnoempleo'),
]