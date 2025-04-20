# data_integration/views.py
from django.shortcuts import render
from .scrapers.linkedin import scrape_linkedin
from .scrapers.tecnoempleo import scrape_tecnoempleo

def scrape_index(request):
    """Vista principal que muestra los botones para ejecutar los diferentes scrapers."""
    return render(request, "data_integration/scrape_index.html") 