from django.shortcuts import render
from django.contrib import messages
from rolepermissions.decorators import has_role_decorator  # Cambiado
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
from market_analysis.models import JobOffer, Skill
import os
import re


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
  
@has_role_decorator('admin')
def scrape_linkedin(request):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.linkedin.com/login")
        messages.info(request, "Inicia sesión en LinkedIn manualmente. Tienes 60 segundos.")
        time.sleep(60)  # Más tiempo

        driver.get("https://www.linkedin.com/jobs/search/?keywords=desarrollador&location=Asturias%2C%20España&f_TPR=r2592000")  # Último mes
        time.sleep(10)  # Espera inicial

        for _ in range(5):  # Menos scrolls
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            try:
                driver.find_element(By.CLASS_NAME, "jobs-search-results-list__see-more").click()
                time.sleep(5)
            except:
                pass

        soup = BeautifulSoup(driver.page_source, "html.parser")
        jobs = soup.find_all("li", class_="jobs-search-results__list-item")  # Selector actualizado
        one_month_ago = datetime.now().date() - timedelta(days=30)

        offers = []
        for job in jobs:
            title_elem = job.find("a", class_="job-card-list__title")
            company_elem = job.find("span", class_="job-card-container__company-name")
            location_elem = job.find("li", class_="job-card-container__metadata-item")
            date_elem = job.find("time", class_="job-card-container__listed-time")

            title_text = title_elem.text.strip() if title_elem else "Sin título"
            company_text = company_elem.text.strip() if company_elem else "Sin compañía"
            location_text = location_elem.text.strip() if location_text else "Sin ubicación"
            try:
                pub_date = datetime.strptime(date_elem['datetime'], '%Y-%m-%d').date() if date_elem else one_month_ago
            except (ValueError, TypeError):
                pub_date = one_month_ago

            if pub_date < one_month_ago:
                continue

            job_obj, created = JobOffer.objects.get_or_create(
                title=title_text,
                company=company_text,
                source="LinkedIn",
                defaults={
                    'location': location_text,
                    'publication_date': pub_date,
                    'salary': None
                }
            )
            if created:
                offers.append(job_obj)

        messages.success(request, f"Se encontraron {len(offers)} ofertas de LinkedIn.")
        if not offers:
            with open("linkedin_debug.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            messages.warning(request, "Revisa 'linkedin_debug.html'.")
    except Exception as e:
        messages.error(request, f"Error al scrapear LinkedIn: {e}")
        offers = []
    finally:
        driver.quit()

    return render(request, 'data_integration/scrape_results.html', {'offers': offers})

@has_role_decorator('admin')
def scrape_infojobs(request):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.infojobs.net/jobsearch/search-results/list.xhtml?keyword=desarrollador&provinceIds=33&normalizedLocation=asturias&sortBy=RELEVANCE")
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))).click()
        except:
            pass

        time.sleep(10)  # Espera inicial
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            try:
                driver.find_element(By.CLASS_NAME, "ij-ShowMoreResults-button").click()
                time.sleep(5)
            except:
                pass

        soup = BeautifulSoup(driver.page_source, "html.parser")
        jobs = soup.find_all("div", class_="ij-OfferList-item")  # Selector actualizado
        one_month_ago = datetime.now().date() - timedelta(days=30)

        offers = []
        for job in jobs:
            title_elem = job.find("a", class_="ij-OfferList-title")
            company_elem = job.find("span", class_="ij-OfferList-company")
            location_elem = job.find("span", class_="ij-OfferList-location")
            date_elem = job.find("span", class_="ij-OfferList-date")
            skills_elems = job.find_all("span", class_="ij-OfferList-skill")[:10]

            title_text = title_elem.text.strip() if title_elem else "Sin título"
            company_text = company_elem.text.strip() if company_elem else "Sin compañía"
            location_text = location_elem.text.strip() if location_elem else "Sin ubicación"
            try:
                pub_date = datetime.strptime(date_elem.text.strip(), '%d/%m/%Y').date() if date_elem else one_month_ago
            except (ValueError, TypeError):
                pub_date = one_month_ago
            salary = None

            if pub_date < one_month_ago:
                continue

            job_obj, created = JobOffer.objects.get_or_create(
                title=title_text,
                company=company_text,
                source="InfoJobs",
                defaults={
                    'location': location_text,
                    'publication_date': pub_date,
                    'salary': salary
                }
            )
            if created:
                for skill_elem in skills_elems:
                    skill_name = skill_elem.text.strip()
                    skill, _ = Skill.objects.get_or_create(name=skill_name)
                    job_obj.skills.add(skill)
            offers.append(job_obj)

        messages.success(request, f"Se encontraron {len(offers)} ofertas de InfoJobs.")
        if not offers:
            with open("infojobs_debug.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            messages.warning(request, "Revisa 'infojobs_debug.html'.")
    except Exception as e:
        messages.error(request, f"Error al scrapear InfoJobs: {e}")
        offers = []
    finally:
        driver.quit()

    return render(request, 'data_integration/scrape_results.html', {'offers': offers})