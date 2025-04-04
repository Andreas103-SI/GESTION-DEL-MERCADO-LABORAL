#data_integration/views.py
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from market_analysis.models import JobOffer, Skill

def scrape_tecnoempleo(request):
    url = "https://www.tecnoempleo.com/ofertas-trabajo/"  # Ejemplo, ajusta según la página
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    offers = []
    for offer in soup.select('.job-offer'):  # Ajusta el selector según la estructura real
        title = offer.find('h2').text.strip()
        company = offer.find(class_='company').text.strip()
        location = offer.find(class_='location').text.strip()

        job = JobOffer(
            title=title,
            company=company,
            location=location,
            source="Tecnoempleo",
            publication_date="2025-04-04"  # Fecha fija por ahora
        )
        job.save()
        offers.append(job)

    return render(request, 'data_integration/scrape_results.html', {'offers': offers})