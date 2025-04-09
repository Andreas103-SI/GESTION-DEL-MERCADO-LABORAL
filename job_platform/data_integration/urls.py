from django.urls import path
from .views import scrape_tecnoempleo
from .views import scrape_linkedin

urlpatterns = [
    path('scrape/', scrape_tecnoempleo, name='scrape_tecnoempleo'),
    path('scrape-linkedin/', scrape_linkedin, name='scrape_linkedin'),
]