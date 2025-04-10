import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.contrib import messages
from market_analysis.models import JobOffer, Skill
from job_platform.views import role_required
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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

    for offer in soup.select('.col-10.col-md-9.col-lg-7'):
        title_elem = offer.select_one('h3.fs-5.mb-2 a')
        company_elem = offer.select_one('a.text-primary.link-muted')
        location_elem = offer.select_one('span.d-block.d-lg-none b')
        skills_elems = offer.select('span.badge.bg-gray-500')

        if title_elem and company_elem and location_elem:
            title = title_elem.text.strip()
            company = company_elem.text.strip()
            location = location_elem.text.strip()

            job, created = JobOffer.objects.get_or_create(
                title=title,
                company=company,
                source="Tecnoempleo",
                defaults={'location': location, 'publication_date': datetime.now().date()}
            )
            for skill_elem in skills_elems:
                skill_name = skill_elem.text.strip()
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                job.skills.add(skill)
            offers.append(job)

    messages.success(request, f"Se encontraron {len(offers)} ofertas de Tecnoempleo.")
    return render(request, 'data_integration/scrape_results.html', {'offers': offers})

@role_required('admin')
def scrape_linkedin(request):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.linkedin.com/login")
        messages.info(request, "Inicia sesión en LinkedIn manualmente en la ventana que se abrió. Tienes 40 segundos.")
        time.sleep(40)  # Aumentado a 40 segundos para login

        driver.get("https://www.linkedin.com/jobs/search/?keywords=desarrollador%20python&location=Asturias%2C%20España")
        messages.info(request, "Esperando 40 segundos para que la página de empleos cargue completamente.")
        time.sleep(40)  # Aumentado a 40 segundos para carga

        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(20):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser")
        jobs = soup.find_all("div", class_="job-card-list__entity-lockup")
        
        offers = []
        for job in jobs:
            title_elem = job.find("a", class_="job-card-list__title--link")
            company_elem = job.find("div", class_="artdeco-entity-lockup__subtitle")
            location_elem = job.find("ul", class_="job-card-container__metadata-wrapper").find("li") if job.find("ul", class_="job-card-container__metadata-wrapper") else None

            title_text = title_elem.text.strip() if title_elem else "Sin título"
            title_span = title_elem.find("span", {"aria-hidden": "true"}) if title_elem else None
            title_text = title_span.text.strip() if title_span else title_text
            company_text = company_elem.text.strip() if company_elem else "Sin compañía"
            location_text = location_elem.text.strip() if location_elem else "Sin ubicación"

            job_obj, created = JobOffer.objects.get_or_create(
                title=title_text,
                company=company_text,
                source="LinkedIn",
                defaults={'location': location_text, 'publication_date': datetime.now().date()}
            )
            offers.append(job_obj)

        messages.success(request, f"Se encontraron {len(offers)} ofertas de LinkedIn.")
    
    except Exception as e:
        messages.error(request, f"Error al scrapear LinkedIn: {e}")
        offers = []
    
    finally:
        pass

    return render(request, 'data_integration/scrape_results.html', {'offers': offers})

@role_required('admin')
def scrape_infojobs(request):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Navegar y manejar cookies
        driver.get("https://www.infojobs.net/ofertas-trabajo/asturias")
        try:
            # Aceptar cookies si aparece
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))).click()
            print("Cookies aceptadas.")
        except TimeoutException:
            print("No se encontró popup de cookies.")

        # Esperar carga de ofertas
        WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ij-OfferCardContent-description")))
        print("Página de InfoJobs cargada.")

        # Scroll
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(20):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Extraer
        soup = BeautifulSoup(driver.page_source, "html.parser")
        jobs = soup.find_all("div", class_="ij-OfferCardContent-description")
        print(f"Jobs found: {len(jobs)}")

        offers = []
        for job in jobs:
            title_elem = job.find("a", class_="ij-OfferCardContent-description-title-link")
            company_elem = job.find("a", class_="ij-OfferCardContent-description-subtitle-link")
            location_elem = job.find("span", class_="ij-OfferCardContent-description-list-item-truncate")

            title_text = title_elem.text.strip() if title_elem else "Sin título"
            company_text = company_elem.text.strip() if company_elem else "Sin compañía"
            location_text = location_elem.text.strip() if location_elem else "Sin ubicación"

            job_obj, created = JobOffer.objects.get_or_create(
                title=title_text,
                company=company_text,
                source="InfoJobs",
                defaults={'location': location_text, 'publication_date': datetime.now().date()}
            )
            offers.append(job_obj)

        messages.success(request, f"Se encontraron {len(offers)} ofertas de InfoJobs.")
        if len(offers) == 0:
            with open("infojobs_debug.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            messages.warning(request, "No se encontraron ofertas. Revisa 'infojobs_debug.html'.")
    except Exception as e:
        messages.error(request, f"Error al scrapear InfoJobs: {e}")
        with open("infojobs_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        offers = []
    finally:
        pass

    return render(request, 'data_integration/scrape_results.html', {'offers': offers})