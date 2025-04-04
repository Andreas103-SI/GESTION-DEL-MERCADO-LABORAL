from django.urls import path
from .views import scrape_tecnoempleo

urlpatterns = [
    path('scrape/', scrape_tecnoempleo, name='scrape_tecnoempleo'),
]