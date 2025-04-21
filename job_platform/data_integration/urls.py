# data_integration/urls.py
from django.urls import path
from .views import scrape_index
from .scrapers.linkedin import scrape_linkedin
from .scrapers.tecnoempleo import scrape_tecnoempleo

urlpatterns = [
    path('', scrape_index, name='scrape_index'),
    path('linkedin/', scrape_linkedin, name='scrape_linkedin'),
    path('tecnoempleo/', scrape_tecnoempleo, name='scrape_tecnoempleo'),
]