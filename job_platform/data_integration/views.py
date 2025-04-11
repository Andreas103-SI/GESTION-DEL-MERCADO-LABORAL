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

    soup = BeautifulSoup(response.text, 'html.parser')
    offers = []
    one_month_ago = datetime.now().date() - timedelta(days=30)

    for offer in soup.select('.col-10.col-md-9.col-lg-7'):
        title_elem = offer.select_one('h3.fs-5.mb-2 a')
        company_elem = offer.select_one('a.text-primary.link-muted')
        location_elem = offer.select_one('span.d-block.d-lg-none b')
        skills_elems = offer.select('span.badge.bg-gray-500')[:10]  # Límite de 10
        date_elem = offer.select_one('span.text-muted')

        if title_elem and company_elem and location_elem:
            title = title_elem.text.strip()
            company = company_elem.text.strip()
            location = location_elem.text.strip()
            pub_date = datetime.strptime(date_elem.text.strip(), '%d/%m/%Y').date() if date_elem else datetime.now().date()
            salary = None

            if pub_date < one_month_ago:
                continue

            job, created = JobOffer.objects.get_or_create(
                title=title,
                company=company,
                source="Tecnoempleo",
                defaults={
                    'location': location,
                    'publication_date': pub_date,
                    'salary': salary
                }
            )
            if created:  # Solo añadir skills si es nueva
                for skill_elem in skills_elems:
                    skill_name = skill_elem.text.strip()
                    skill, _ = Skill.objects.get_or_create(name=skill_name)
                    job.skills.add(skill)
            offers.append(job)

    messages.success(request, f"Se encontraron {len(offers)} ofertas de Tecnoempleo.")
    return render(request, 'data_integration/scrape_results.html', {'offers': offers})

@has_role_decorator('admin')
def scrape_linkedin(request):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.linkedin.com/login")
        messages.info(request, "Inicia sesión en LinkedIn manualmente. Tienes 40 segundos.")
        time.sleep(40)

        driver.get("https://www.linkedin.com/jobs/search/?keywords=desarrollador&location=Asturias%2C%20España")
        messages.info(request, "Esperando 40 segundos para que cargue.")
        time.sleep(40)

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
        one_month_ago = datetime.now().date() - timedelta(days=30)

        offers = []
        for job in jobs:
            title_elem = job.find("a", class_="job-card-list__title--link")
            company_elem = job.find("div", class_="artdeco-entity-lockup__subtitle")
            location_elem = job.find("ul", class_="job-card-container__metadata-wrapper").find("li") if job.find("ul") else None
            date_elem = job.find("time")

            title_text = title_elem.text.strip() if title_elem else "Sin título"
            company_text = company_elem.text.strip() if company_elem else "Sin compañía"
            location_text = location_elem.text.strip() if location_elem else "Sin ubicación"
            pub_date = datetime.strptime(date_elem['datetime'], '%Y-%m-%d').date() if date_elem and 'datetime' in date_elem.attrs else datetime.now().date()
            salary = None

            if "Asturias" not in location_text or pub_date < one_month_ago:
                continue

            job_obj, created = JobOffer.objects.get_or_create(
                title=title_text,
                company=company_text,
                source="LinkedIn",
                defaults={
                    'location': location_text,
                    'publication_date': pub_date,
                    'salary': salary
                }
            )
            if created:  # Solo si es nueva
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
        pass

    return render(request, 'data_integration/scrape_results.html', {'offers': offers})

@has_role_decorator('admin')
def scrape_infojobs(request):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.infojobs.net/ofertas-trabajo/asturias?keyword=desarrollador")
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))).click()
        except Exception:
            pass

        WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ij-OfferCardContent-description")))
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(20):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser")
        jobs = soup.find_all("div", class_="ij-OfferCardContent-description")
        one_month_ago = datetime.now().date() - timedelta(days=30)

        offers = []
        for job in jobs:
            title_elem = job.find("a", class_="ij-OfferCardContent-description-title-link")
            company_elem = job.find("a", class_="ij-OfferCardContent-description-subtitle-link")
            location_elem = job.find("span", class_="ij-OfferCardContent-description-list-item-truncate")
            date_elem = job.find("span", class_="ij-OfferCardContent-date")
            skills_elems = job.find_all("span", class_="ij-Skill")[:10]  # Límite de 10

            title_text = title_elem.text.strip() if title_elem else "Sin título"
            company_text = company_elem.text.strip() if company_elem else "Sin compañía"
            location_text = location_elem.text.strip() if location_elem else "Sin ubicación"
            pub_date = datetime.strptime(date_elem.text.strip(), '%d/%m/%Y').date() if date_elem else datetime.now().date()
            salary = None

            if not any(x in location_text for x in ["Asturias", "Oviedo", "Gijón", "Avilés"]) or pub_date < one_month_ago:
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
            if created:  # Solo si es nueva
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
        pass

    return render(request, 'data_integration/scrape_results.html', {'offers': offers})