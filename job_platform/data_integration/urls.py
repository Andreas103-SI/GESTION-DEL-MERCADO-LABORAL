from django.urls import path
from .views import scrape_tecnoempleo, scrape_linkedin, scrape_index
from . import views


urlpatterns = [
    path('', scrape_index, name='scrape_index'),
    path('scrape/', scrape_tecnoempleo, name='scrape_tecnoempleo'),
    path('scrape-linkedin/', scrape_linkedin, name='scrape_linkedin'),
    path('scrape-infojobs/', views.scrape_infojobs, name='scrape_infojobs'),
]