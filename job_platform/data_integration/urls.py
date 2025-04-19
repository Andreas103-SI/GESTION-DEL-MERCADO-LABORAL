# data_integration/urls.py
from django.urls import path
from .views import scrape_index, scrape_linkedin, scrape_tecnoempleo

urlpatterns = [
    path('', scrape_index, name='scrape_index'),
    path('scrape-linkedin/', scrape_linkedin, name='scrape_linkedin'),
    path('scrape-tecnoempleo/', scrape_tecnoempleo, name='scrape_tecnoempleo'),
]