# data_integration/scrapers/linkedin.py
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
from .utils import parse_relative_date

@has_role_decorator('admin')
def scrape_linkedin(request):
    """
    Extrae 22-25 ofertas de empleo de LinkedIn en España.
    Optimizado para ejecutarse en menos de 2 minutos.
    """
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--dns-prefetch-disable")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_experimental_option("detach", True)
    driver = None
    offers = []
    processed_urls = set()

    try:
        print("[DEBUG] Iniciando scraper de LinkedIn")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        load_dotenv()
        driver.get("https://www.linkedin.com/login")
        print("[DEBUG] Cargando página de login...")
        email = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")
        if not email or not password:
            messages.error(request, "Error: No se encontraron credenciales en el archivo .env.")
            return render(request, "data_integration/scrape_results.html", {"offers": [], "num_offers": 0})

        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(email)
            password_field = driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            print("[DEBUG] Credenciales enviadas")
            time.sleep(random.uniform(0.2, 0.4))
        except Exception as e:
            print(f"[DEBUG] Error al ingresar credenciales: {e}")
            messages.error(request, "Error: No se pudo completar el login automático. Revisa las credenciales en .env.")
            driver.save_screenshot("login_error.png")
            return render(request, "data_integration/scrape_results.html", {"offers": [], "num_offers": 0})

        print("[DEBUG] Verificando login...")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.feed-identity-module, div[class*='feed-container']"))
            )
            print("[DEBUG] Login verificado por presencia de feed")
        except Exception as e:
            print(f"[DEBUG] Error en verificación de login: {e}")
            messages.error(request, "Error: Login no completado. Revisa credenciales, CAPTCHAs, o popups.")
            driver.save_screenshot("login_error.png")
            return render(request, "data_integration/scrape_results.html", {"offers": [], "num_offers": 0})

        print("[DEBUG] Cargando página de empleos...")
        all_offer_urls = set()

        keywords = [
            "desarrollador", "programador", "software engineer", "full stack developer", "backend developer"
        ]
        for keyword in keywords:
            if len(all_offer_urls) >= 40:
                break

            search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location=España&sort=date"
            page = 0
            max_pages = 2
            while page < max_pages:
                paginated_url = f"{search_url}&start={page*25}"
                driver.get(paginated_url)
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/jobs/view/']"))
                    )
                    print(f"[DEBUG] Ofertas de búsqueda cargadas correctamente para keyword: {keyword} (España, página {page+1})")
                except Exception as e:
                    print(f"[DEBUG] Error al cargar la página de búsqueda para {keyword} (España, página {page+1}): {e}")
                    break

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(0.2, 0.3))

                soup = BeautifulSoup(driver.page_source, 'lxml')
                job_cards = soup.select('a[href*="/jobs/view/"]')
                offer_urls = set()
                max_offers = 10
                for card in job_cards:
                    href = card.get('href', '')
                    if href and "/jobs/view/" in href:
                        full_url = f"https://www.linkedin.com{href.split('?')[0]}"
                        if full_url not in processed_urls:
                            offer_urls.add(full_url)
                            all_offer_urls.add(full_url)
                            processed_urls.add(full_url)
                            print(f"[DEBUG] URL encontrada: {full_url}")
                            if len(offer_urls) >= max_offers:
                                break

                print(f"[DEBUG] Total URLs únicas recolectadas para {keyword} (España, página {page+1}): {len(offer_urls)}")
                page += 1

        all_offer_urls = list(all_offer_urls)
        print(f"[DEBUG] Total URLs únicas recolectadas (todas las keywords): {len(all_offer_urls)}")

        asturias_offers = []
        for i, url in enumerate(all_offer_urls):
            retries = 3
            while retries > 0:
                try:
                    print(f"[DEBUG] Procesando oferta {i+1}: {url}")
                    driver.get(url)
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    time.sleep(random.uniform(0.1, 0.2))
                    soup = BeautifulSoup(driver.page_source, 'lxml')

                    title_tag = soup.select_one('h1.top-card-layout__title') or soup.select_one('.job-details-jobs-unified-top-card__job-title h1') or soup.select_one('.topcard__title')
                    title = title_tag.get_text(strip=True)[:255] if title_tag else "Sin título"

                    company_tag = soup.select_one('a.topcard__org-name-link') or soup.select_one('.job-details-jobs-unified-top-card__company-name a') or soup.select_one('.topcard__flavor a')
                    company = company_tag.get_text(strip=True)[:255] if company_tag else "Sin compañía"

                    location_tag = soup.select_one('.job-details-jobs-unified-top-card__primary-description-container') or soup.select_one('.topcard__flavor--bullet')
                    description_tag = soup.select_one('div.jobs-description__content') or soup.select_one('.jobs-box__html-content') or soup.select_one('#job-details')
                    description = description_tag.get_text(strip=True).lower() if description_tag else "No especificada"

                    if location_tag:
                        location_text = location_tag.get_text(strip=True)
                        if '(' in location_text and ')' in location_text:
                            location = location_text.split('(')[0].strip()[:255]
                            modality = location_text[location_text.find('(')+1:location_text.find(')')].strip().lower()
                        else:
                            location = location_text[:255]
                            modality = ""
                    else:
                        location = "Ubicación no especificada"
                        modality = ""

                    remote_terms = ["remoto", "remote", "teletrabajo", "100% remoto", "telecommute", "work from home", "híbrido", "hybrid"]
                    is_remote = any(term in modality for term in remote_terms) or any(term in description for term in remote_terms)
                    final_location = location
                    if is_remote:
                        final_location = f"{location} (Remoto/Híbrido)"

                    location_lower = location.lower()
                    is_asturias = any(loc in location_lower for loc in ["asturias", "gijón", "oviedo", "principado de asturias"])

                    skills_list = []
                    skills_link = soup.select_one('a[href*="#HYM"][data-test-app-aware-link]')
                    skills_section = soup.select('ul span li')
                    if skills_link and "Aptitudes:" in skills_link.get_text():
                        skills_text = skills_link.get_text(strip=True).replace("Aptitudes:", "").split(" y ")[0].split(", ")
                        skills_list = [skill.strip() for skill in skills_text if skill.strip() and "desarrollo" not in skill.lower()]
                    elif skills_section:
                        skills_list = [skill.get_text(strip=True) for skill in skills_section if skill.get_text(strip=True) and "desarrollo" not in skill.lower()]
                    elif description:
                        known_skills = [
                            'python', 'javascript', 'java', 'sql', 'node.js', 'react', 'django', 'html', 'css',
                            'git', 'docker', 'agile', 'scrum', 'teamwork', 'communication', 'problem-solving',
                            'leadership', 'adaptability', 'typescript', 'aws', 'mongodb', 'postgresql', 'linux',
                            'microservicios', '.net framework', 'asp.net mvc', 'hibernate', 'kubernetes', 'php',
                            'laravel', 'react.js', '.net core'
                        ]
                        skills_list = [skill for skill in known_skills if skill.lower() in description]
                    print(f"[DEBUG] Habilidades encontradas para '{title}': {skills_list}")

                    date_tag = soup.select_one('time[datetime]') or soup.select_one('span.jobs-unified-top-card__posted-date') or soup.select_one('span.topcard__flavor--metadata') or soup.select_one('.job-details-jobs-unified-top-card__primary-description-container')
                    if date_tag:
                        if date_tag.has_attr('datetime'):
                            try:
                                pub_date = datetime.strptime(date_tag['datetime'], "%Y-%m-%d").date()
                                print(f"[DEBUG] Fecha (desde datetime): {pub_date}")
                            except:
                                date_text = date_tag.get_text(strip=True).lower()
                                pub_date = parse_relative_date(date_text)
                        else:
                            date_text = date_tag.get_text(strip=True).lower()
                            pub_date = parse_relative_date(date_text)
                    else:
                        print("[DEBUG] Fecha no encontrada, usando fecha actual.")
                        pub_date = datetime.now().date()
                    print(f"[DEBUG] Fecha final para '{title}': {pub_date}")

                    job_obj, created = JobOffer.objects.get_or_create(
                        source="LinkedIn",
                        url=url,
                        defaults={
                            "title": title,
                            "company": company,
                            "location": final_location,
                            "publication_date": pub_date,
                            "salary": None
                        }
                    )

                    if created:
                        for skill_name in skills_list:
                            if skill_name:
                                skill, _ = Skill.objects.get_or_create(name=skill_name)
                                job_obj.skills.add(skill)
                        offers.append(job_obj)
                        if is_asturias:
                            asturias_offers.append(job_obj)
                        print(f"[DEBUG] Oferta {i+1} guardada: {title} - {company} - {final_location} - {pub_date} - Habilidades: {skills_list}")
                    break

                except Exception as e:
                    print(f"[DEBUG] Error procesando oferta {i+1} (Intento {3-retries}): {e}")
                    retries -= 1
                    if retries == 0:
                        print(f"[DEBUG] Oferta {i+1} descartada tras 3 intentos")
                        break
                    time.sleep(random.uniform(0.1, 0.2))

            if len(offers) >= 25:
                print("[DEBUG] Se han recolectado 25 ofertas, deteniendo procesamiento.")
                break

        debug_path = os.path.join(os.getcwd(), "linkedin_debug.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"[DEBUG] HTML guardado en {debug_path}")

        if offers:
            min_date = min(o.publication_date for o in offers).strftime("%d/%m/%Y")
            max_date = max(o.publication_date for o in offers).strftime("%d/%m/%Y")
            messages.success(request, f"Esta actualización incluye ofertas desde {min_date} hasta {max_date}.")
            messages.success(request, f"Se han extraído {len(offers)} ofertas de LinkedIn.")
            remote_count = sum(1 for o in offers if "remoto" in o.location.lower() or "híbrido" in o.location.lower())
            if remote_count > 0:
                messages.info(request, f"{remote_count} de las ofertas son remotas o híbridas.")
            if asturias_offers:
                messages.info(request, f"Se encontraron {len(asturias_offers)} ofertas en Asturias.")
            else:
                messages.info(request, "No se encontraron ofertas específicas en Asturias.")
        else:
            messages.warning(request, "No se encontraron ofertas. Revisa linkedin_debug.html.")
            driver.save_screenshot("no_offers.png")

    except Exception as e:
        print(f"[DEBUG] Error general: {e}")
        messages.error(request, f"Error al scrapear LinkedIn: {e}")
        if driver:
            driver.save_screenshot("general_error.png")

    finally:
        if driver:
            try:
                driver.quit()
            except:
                print("[DEBUG] No se pudo cerrar el driver: ya estaba cerrado")

    context = {
        "offers": offers,
        "num_offers": len(offers)
    }
    print(f"[DEBUG] Renderizando template con {len(offers)} ofertas")
    return render(request, "data_integration/scrape_results.html", context)