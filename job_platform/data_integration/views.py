import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.contrib import messages
from market_analysis.models import JobOffer, Skill
from job_platform.views import role_required
from datetime import datetime

@role_required('admin')
def scrape_tecnoempleo(request):
    url = "https://www.tecnoempleo.com/ofertas-trabajo/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        messages.error(request, f"Error al conectar con Tecnoempleo: {e}")
        return render(request, 'data_integration/scrape_results.html', {'offers': []})

    soup = BeautifulSoup(response.text, 'html.parser')
    offers = []

    for offer in soup.select('.col-10.col-md-9.col-lg-7'):  # Contenedor de cada oferta
        title_elem = offer.select_one('h3.fs-5.mb-2 a')  # Título dentro de <h3><a>
        company_elem = offer.select_one('a.text-primary.link-muted')  # Empresa
        location_elem = offer.select_one('span.d-block.d-lg-none b')  # Ubicación dentro de <b>
        skills_elems = offer.select('span.badge.bg-gray-500')  # Habilidades

        if title_elem and company_elem and location_elem:
            title = title_elem.text.strip()
            company = company_elem.text.strip()
            location = location_elem.text.strip()

            job, created = JobOffer.objects.get_or_create(
                title=title,
                company=company,
                source="Tecnoempleo",
                defaults={
                    'location': location,
                    'publication_date': datetime.now().date()
                }
            )
            # Añadir habilidades extraídas
            for skill_elem in skills_elems:
                skill_name = skill_elem.text.strip()
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                job.skills.add(skill)
            offers.append(job)

    messages.success(request, f"Se encontraron {len(offers)} ofertas.")
    return render(request, 'data_integration/scrape_results.html', {'offers': offers})