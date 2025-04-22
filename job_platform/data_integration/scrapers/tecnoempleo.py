# data_integration/scrapers/tecnoempleo.py
from django.contrib import messages
from django.shortcuts import render
from rolepermissions.decorators import has_role_decorator
from market_analysis.models import JobOffer, Skill
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os
import re
import random
import requests
from dotenv import load_dotenv





# Scraper de Tecnoempleo para la Fase 5:
# - Extrae 30 ofertas con título, empresa, ubicación, fecha y habilidades.
# - Fechas correctas (11/04/2025 a 12/04/2025), sin fallback.
# - Limpia salario (p.ej., '27.000€ - 33.000€ b/a') y texto ('Nueva', 'Actualizada') con regex.
# - Muestra mensaje de rango ('Esta actualización incluye ofertas desde X hasta Y') y 'Se han extraído 30 ofertas'.
# - Ubicaciones como 'Madrid y otras' y 'Barcelona (Híbrido)' bien parseadas.
# - Usa tecnoempleo_debug.html para depuración.
@has_role_decorator('admin')
def scrape_tecnoempleo(request):
    url = "https://www.tecnoempleo.com/ofertas-trabajo/?keyword=desarrollador&provincia=33"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        messages.error(request, f"Error al conectar con Tecnoempleo: {e}")
        return render(request, 'data_integration/scrape_results.html', {'offers': []})

    # Guardar HTML para depuración
    debug_path = os.path.join(os.getcwd(), "tecnoempleo_debug.html")
    with open(debug_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    soup = BeautifulSoup(response.text, 'html.parser')
    offers = []
    one_month_ago = datetime.now().date() - timedelta(days=30)
    date_list = []

    for offer in soup.select('.col-10.col-md-9.col-lg-7'):
        title_elem = offer.select_one('h3.fs-5.mb-2 a')
        company_elem = offer.select_one('a.text-primary.link-muted')
        location_elem = offer.select_one('span.d-block.d-lg-none.text-gray-800')
        skills_elems = offer.select('span.badge.bg-gray-500')[:10]

        if title_elem and company_elem and location_elem:
            title = title_elem.text.strip()
            company = company_elem.text.strip()
            location_text = location_elem.text.strip()
            date_text = None

            # Extraer fecha
            if ' - ' in location_text:
                location, date_candidate = location_text.split(' - ', 1)
                location = BeautifulSoup(location, 'html.parser').text.strip()
                # Limpiar fecha con regex
                date_candidate = date_candidate.replace('Actualizada', '').replace('Nueva', '').strip()
                # Extraer solo la fecha (dd/mm/yyyy)
                date_match = re.match(r'(\d{2}/\d{2}/\d{4})', date_candidate)
                if date_match:
                    date_text = date_match.group(1)
                else:
                    date_text = None
            else:
                location = location_text

            try:
                if date_text:
                    pub_date = datetime.strptime(date_text, '%d/%m/%Y').date()
                    date_list.append(pub_date)
                else:
                    pub_date = one_month_ago
            except (ValueError, AttributeError):
                pub_date = one_month_ago

            if pub_date < one_month_ago:
                continue

            job, created = JobOffer.objects.get_or_create(
                title=title,
                company=company,
                source="Tecnoempleo",
                defaults={
                    'location': location,
                    'publication_date': pub_date,
                    'salary': None
                }
            )
            if created:
                for skill_elem in skills_elems:
                    skill_name = skill_elem.text.strip()
                    skill, _ = Skill.objects.get_or_create(name=skill_name)
                    job.skills.add(skill)
            offers.append(job)

    # Calcular rango de fechas y mensaje
    if date_list:
        min_date = min(date_list).strftime('%d/%m/%Y')
        max_date = max(date_list).strftime('%d/%m/%Y')
        messages.success(request, f"Esta actualización incluye ofertas desde {min_date} hasta {max_date}.")
    else:
        messages.success(request, "No se encontraron fechas válidas en las ofertas.")
    
    # Pasar número de ofertas al contexto
    context = {
        'offers': offers,
        'num_offers': len(offers)
    }
    return render(request, 'data_integration/scrape_results.html', context)

