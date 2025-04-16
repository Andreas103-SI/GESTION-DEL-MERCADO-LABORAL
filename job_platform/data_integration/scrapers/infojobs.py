# data_integration/scrapers/infojobs.py
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
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os
import re
import random
import logging
import socket

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constantes para el scraper
SEARCH_KEYWORDS = ["desarrollador", "programador", "developer", "software engineer"]
MAX_OFFERS = 25
MAX_PAGES = 5
WAIT_AFTER_CAPTCHA = 40
RETRY_ATTEMPTS = 3
PAGE_LOAD_TIMEOUT = 60
CONNECTION_RETRIES = 3
CHROME_TIMEOUT = 180

def check_internet_connection():
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        return True
    except OSError:
        return False

@has_role_decorator('admin')
def scrape_infojobs(request):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--dns-prefetch-disable")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--disable-features=UserAgentClientHint")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-webgl")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    
    driver = None
    offers = []
    processed_urls = set()
    captcha_detected = False

    try:
        logger.info("Iniciando scraper de InfoJobs")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.set_page_load_timeout(CHROME_TIMEOUT)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        all_offer_urls = set()
        
        for keyword in SEARCH_KEYWORDS:
            if len(all_offer_urls) >= MAX_OFFERS * 2:
                break
                
            search_url = f"https://www.infojobs.net/jobsearch/search-results/list.xhtml?keyword={keyword}&country=esp&sortBy=PUBLICATION_DATE"
            logger.info(f"Buscando ofertas con palabra clave: {keyword}")
            
            page_loaded = False
            for attempt in range(RETRY_ATTEMPTS):
                if not check_internet_connection():
                    logger.error(f"No hay conexión a internet en intento {attempt + 1}. Reintentando...")
                    time.sleep(5)
                    continue
                
                try:
                    driver.get(search_url)
                    WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    page_loaded = True
                    break
                except Exception as e:
                    logger.warning(f"Intento {attempt + 1} fallido al cargar página: {e}")
                    if "net::ERR_INTERNET_DISCONNECTED" in str(e):
                        logger.error("Error de conexión detectado. Verificando conexión a internet...")
                        if not check_internet_connection():
                            logger.error("Sin conexión a internet. Reintentando...")
                            time.sleep(5)
                            continue
                    if attempt == RETRY_ATTEMPTS - 1:
                        logger.error("No se pudo cargar la página después de varios intentos. Abortando.")
                        messages.error(request, "No se pudo cargar la página de InfoJobs. Revisa tu conexión o intenta más tarde.")
                        return render(request, "data_integration/scrape_results.html", {"offers": [], "num_offers": 0})
                    time.sleep(random.uniform(2.0, 3.0))
            
            if not page_loaded:
                logger.error("No se pudo cargar la página de búsqueda. Abortando.")
                messages.error(request, "No se pudo cargar la página de búsqueda de InfoJobs. Revisa tu conexión o intenta más tarde.")
                return render(request, "data_integration/scrape_results.html", {"offers": [], "num_offers": 0})
            
            time.sleep(random.uniform(2.0, 3.0))
            
            try:
                cookie_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
                )
                driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", cookie_button)
                time.sleep(random.uniform(0.2, 0.5))
                ActionChains(driver).move_to_element(cookie_button).pause(random.uniform(0.1, 0.3)).click().perform()
                logger.info("Popup de cookies aceptado")
            except Exception as e:
                logger.info(f"No se encontró popup de cookies o ya fue aceptado: {e}")
            
            captcha_detected = detect_and_handle_captcha(driver, request)
            if captcha_detected:
                logger.info("Esperando a que el usuario resuelva el CAPTCHA...")
                time.sleep(WAIT_AFTER_CAPTCHA)
                if not is_captcha_resolved(driver):
                    logger.warning("CAPTCHA no resuelto después de esperar. Abortando.")
                    messages.warning(request, "No se pudo resolver el CAPTCHA. Por favor, intenta de nuevo.")
                    return render(request, "data_integration/scrape_results.html", {"offers": [], "num_offers": 0})
                
                for conn_attempt in range(CONNECTION_RETRIES):
                    if check_internet_connection():
                        driver.get(search_url)
                        logger.info("Página recargada después de resolver el CAPTCHA")
                        time.sleep(random.uniform(2.0, 3.0))
                        break
                    else:
                        logger.warning(f"No hay conexión a internet en intento {conn_attempt + 1} después de resolver CAPTCHA. Reintentando...")
                        time.sleep(5)
                        if conn_attempt == CONNECTION_RETRIES - 1:
                            logger.error("No se pudo restablecer la conexión después de resolver el CAPTCHA. Abortando.")
                            messages.error(request, "No se pudo conectar a InfoJobs después de resolver el CAPTCHA. Revisa tu conexión.")
                            return render(request, "data_integration/scrape_results.html", {"offers": [], "num_offers": 0})
            
            offer_urls = collect_offer_urls(driver, MAX_PAGES, MAX_OFFERS * 2)
            all_offer_urls.update(offer_urls)
            logger.info(f"Recolectadas {len(offer_urls)} URLs con palabra clave '{keyword}'")
            
            time.sleep(random.uniform(2.0, 3.0))
        
        all_offer_urls = list(all_offer_urls)
        logger.info(f"Total URLs únicas recolectadas: {len(all_offer_urls)}")
        
        for i, url in enumerate(all_offer_urls):
            if len(offers) >= MAX_OFFERS:
                break
                
            try:
                job_offer = process_job_offer(driver, url, i, RETRY_ATTEMPTS)
                if job_offer:
                    try:
                        job_obj, created = JobOffer.objects.get_or_create(
                            source="InfoJobs",
                            url=url,
                            defaults={
                                "title": job_offer["title"],
                                "company": job_offer["company"],
                                "location": job_offer["location"],
                                "publication_date": job_offer["publication_date"],
                                "salary": None
                            }
                        )
                        
                        if created:
                            for skill_name in job_offer["skills"]:
                                if skill_name:
                                    skill, _ = Skill.objects.get_or_create(name=skill_name)
                                    job_obj.skills.add(skill)
                            offers.append(job_obj)
                            logger.info(f"Oferta {i+1} guardada: {job_offer['title']} - {job_offer['company']}")
                    except Exception as e:
                        logger.error(f"Error al guardar oferta en la base de datos: {e}")
                        continue
                else:
                    logger.warning(f"Oferta {i+1} no procesada correctamente, continuando con la siguiente...")
            except Exception as e:
                logger.error(f"Error crítico al procesar oferta {i+1}: {e}")
                continue
        
        debug_path = os.path.join(os.getcwd(), "infojobs_debug.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info(f"HTML guardado en {debug_path}")
        
        show_results_messages(request, offers)
        
    except Exception as e:
        logger.error(f"Error general: {e}")
        messages.error(request, f"Error al scrapear InfoJobs: {e}")
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                logger.info("No se pudo cerrar el driver: ya estaba cerrado")
    
    context = {
        "offers": offers,
        "num_offers": len(offers)
    }
    logger.info(f"Renderizando template con {len(offers)} ofertas")
    return render(request, "data_integration/scrape_results.html", context)

def detect_and_handle_captcha(driver, request):
    try:
        captcha_indicators = [
            "//h1[contains(text(), 'Eres humano o un robot')]",
            "//div[@id='captcha-box']",
            "//iframe[contains(@src, 'captcha')]",
            "//div[contains(@class, 'g-recaptcha')]"
        ]
        
        for indicator in captcha_indicators:
            try:
                captcha_element = driver.find_element(By.XPATH, indicator)
                if captcha_element.is_displayed():
                    logger.warning("CAPTCHA detectado utilizando selector: " + indicator)
                    return True
            except:
                continue
        
        return False
    except Exception as e:
        logger.error(f"Error al detectar CAPTCHA: {e}")
        return False

def is_captcha_resolved(driver):
    try:
        captcha_indicators = [
            "//h1[contains(text(), 'Eres humano o un robot')]",
            "//div[@id='captcha-box']",
            "//iframe[contains(@src, 'captcha')]",
            "//div[contains(@class, 'g-recaptcha')]"
        ]
        for indicator in captcha_indicators:
            try:
                captcha_element = driver.find_element(By.XPATH, indicator)
                if captcha_element.is_displayed():
                    return False
            except:
                continue
        return True
    except:
        return True

def collect_offer_urls(driver, max_pages, max_urls):
    offer_urls = set()
    page = 1

    while page <= max_pages and len(offer_urls) < max_urls:
        logger.info(f"Procesando página {page}...")
        
        try:
            WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ij-List"))
            )
            
            apply_human_like_scrolling(driver)
            
            for selector in [
                "a.ij-OfferCardContent-description-title-link",
                "a.ij-Offer-snippet-link",
                "a.ij-OfferCard-link",
                "a[data-test='link-offer']",
                "div.ij-OfferCardContent > a"
            ]:
                try:
                    logger.info(f"Buscando enlaces con selector: {selector}")
                    links = driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"Encontrados {len(links)} elementos con selector {selector}")
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "infojobs.net" in href and "/of-" in href:
                            offer_urls.add(href)
                            logger.info(f"URL encontrada: {href}")
                except Exception as e:
                    logger.warning(f"Error al buscar enlaces con selector '{selector}': {e}")
                    continue
            
            logger.info(f"URLs encontradas hasta ahora: {len(offer_urls)}")
            
            if len(offer_urls) < max_urls and page < max_pages:
                next_page = False
                
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'ij-Pagination-next') or contains(text(), 'Siguiente')]"))
                    )
                    if next_button.is_enabled() and next_button.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", next_button)
                        time.sleep(random.uniform(0.5, 1.0))
                        ActionChains(driver).move_to_element(next_button).pause(random.uniform(0.1, 0.3)).click().perform()
                        next_page = True
                        time.sleep(random.uniform(2.0, 3.0))
                except Exception as e:
                    logger.info(f"No se encontró botón 'Siguiente': {e}")
                
                if not next_page:
                    try:
                        more_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ver más') or contains(@class, 'ij-ShowMoreResults-button')]"))
                        )
                        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", more_button)
                        time.sleep(random.uniform(0.5, 1.0))
                        ActionChains(driver).move_to_element(more_button).pause(random.uniform(0.1, 0.3)).click().perform()
                        next_page = True
                        time.sleep(random.uniform(2.0, 3.0))
                    except Exception as e:
                        logger.info(f"No se encontró botón 'Ver más': {e}")
                
                if not next_page:
                    logger.info("No se encontraron más páginas")
                    break
            
            page += 1
            
        except Exception as e:
            logger.error(f"Error al recolectar URLs en página {page}: {e}")
            break
    
    return offer_urls

def process_job_offer(driver, url, index, max_retries):
    retries = max_retries
    
    while retries > 0:
        try:
            if not check_internet_connection():
                logger.warning(f"No hay conexión a internet al procesar oferta {index+1}. Reintentando...")
                retries -= 1
                time.sleep(5)
                continue
            
            logger.info(f"Procesando oferta {index+1}: {url}")
            driver.get(url)
            
            WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            apply_human_like_scrolling(driver)
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # Extraer título
            title = extract_with_multiple_selectors(soup, [
                "h1.ij-OfferDetail-title-mainTitle",
                "h1[data-test='job-detail-title']",
                "h1"
            ], "Sin título")
            
            # Extraer compañía con nuevos selectores
            company = extract_with_multiple_selectors(soup, [
                "a[data-testid='header-company-link']",  # Selector más moderno
                "a.link.header-subtitle",  # Enlace típico
                "span.header-subtitle",    # Si no es un enlace
                "div.ij-OfferDetail-header-subtitle",
                "p.header-subtitle",       # Nuevo selector
                "p[data-testid='header-company']",  # Selector más genérico
                "div.header-subtitle"      # Selector genérico
            ], "Sin compañía")
            
            # Extraer ubicación con enfoque similar al de LinkedIn
            location = extract_with_multiple_selectors(soup, [
                "span.topcard__flavor--bullet",  # Inspirado en LinkedIn
                "span.location",                 # Genérico
                "li[data-testid='job-detail-location'] span",  # Nuevo selector
                "li[data-test='job-detail-location'] span",
                "li.ij-OfferDetail-jobDetailsList-item span",
                "span.ij-OfferDetail-location",
                "div.ij-OfferDetail-jobDetailsList-item:nth-child(1) span",
                "div.job-details li:nth-child(1) span"  # Genérico
            ], "Ubicación no especificada")
            
            # Extraer descripción
            description = extract_with_multiple_selectors(soup, [
                "div.ij-OfferDetail-description-content",
                "div[data-test='job-detail-description']",
                "div.container-indent",
                "div.job-description"  # Genérico
            ], "").lower()
            
            remote_terms = ["remoto", "remote", "teletrabajo", "100% remoto", "telecommute", 
                           "work from home", "híbrido", "hybrid", "a distancia"]
            
            is_remote = any(term in description.lower() for term in remote_terms)
            
            modalidad = ""
            if is_remote:
                if any(term in description.lower() for term in ["100% remoto", "full remote", "completamente remoto"]):
                    modalidad = "Teletrabajo"
                elif any(term in description.lower() for term in ["híbrido", "hybrid", "semipresencial"]):
                    modalidad = "Híbrido"
                else:
                    modalidad = "Remoto"
                
                if location != "Ubicación no especificada":
                    final_location = f"{location} ({modalidad})"
                else:
                    final_location = f"España ({modalidad})"
            else:
                final_location = location
            
            # Extraer habilidades con enfoque similar al de LinkedIn
            skills_list = extract_skills(soup, description)
            
            # Extraer fecha de publicación
            pub_date = extract_publication_date(soup)
            
            one_month_ago = datetime.now().date() - timedelta(days=30)
            if pub_date < one_month_ago:
                logger.info(f"Oferta descartada (muy antigua): {title}")
                return None
            
            job_offer = {
                "title": title[:255],
                "company": company[:255],
                "location": final_location[:255],
                "publication_date": pub_date,
                "skills": skills_list
            }
            
            return job_offer
            
        except Exception as e:
            logger.error(f"Error procesando oferta {index+1} (Intento {max_retries-retries+1}): {e}")
            retries -= 1
            if retries == 0:
                logger.error(f"Oferta {index+1} descartada tras {max_retries} intentos")
                return None
            time.sleep(random.uniform(0.5, 1.0))
    
    return None

def extract_with_multiple_selectors(soup, selectors, default_value):
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            text = element.get_text(strip=True)
            if text and text != "":
                return text
    return default_value

def extract_skills(soup, description):
    skills_list = []
    
    # Intentar extraer habilidades de una sección específica (similar a LinkedIn)
    for selector in [
        "div.job-details-skill-match-section__content li",  # Inspirado en LinkedIn
        "ul.tag-list li span",  # Lista de etiquetas
        "li[data-testid='job-detail-skill']",  # Nuevo selector
        "li[data-test='job-detail-skill']",
        "div.ij-OfferDetail-skillsSection ul li",
        "div.panel-skills ul li",
        "span.tag",  # Selector genérico
        "span.skill-tag"  # Genérico
    ]:
        skills_section = soup.select(selector)
        if skills_section:
            skills_list = [skill.get_text(strip=True).lower() for skill in skills_section if skill.get_text(strip=True)]
            break
    
    # Si no se encontraron habilidades en la sección específica, buscar en la descripción
    if not skills_list and description:
        known_skills = [
            'python', 'javascript', 'java', 'sql', 'node.js', 'react', 'django', 'html', 'css',
            'git', 'docker', 'agile', 'scrum', 'teamwork', 'communication', 'problem-solving',
            'leadership', 'adaptability', 'typescript', 'aws', 'mongodb', 'postgresql', 'linux',
            'microservicios', '.net framework', 'asp.net mvc', 'hibernate', 'kubernetes', 'php',
            'laravel', 'react.js', '.net core', 'azure', 'c#', 'c++', 'ruby', 'ruby on rails',
            'spring', 'swift', 'angular', 'vue.js', 'flutter', 'react native', 'ios', 'android',
            'jenkins', 'ci/cd', 'testing', 'machine learning', 'data science', 'blockchain',
            'terraform', 'ansible', 'devops', 'cloud computing', 'rest api', 'graphql', 'redux',
            'sass', 'less', 'bootstrap', 'tailwind', 'figma', 'ux/ui', 'mobile development'
        ]
        
        # Buscar habilidades en la descripción con una expresión regular más precisa
        skills_list = [skill for skill in known_skills if re.search(r'\b' + re.escape(skill) + r'\b', description, re.IGNORECASE)]
    
    return skills_list[:10]

def extract_publication_date(soup):
    # Nuevos selectores para la fecha de publicación
    date_selectors = [
        "time[datetime]",  # Selector para fechas en formato ISO
        "li[data-testid='job-detail-publication-date'] span",  # Nuevo selector
        "li[data-test='job-detail-publication-date'] span",
        "div.ij-OfferDetail-jobDetailsList-item:nth-child(2) span",
        "span.ij-OfferDetail-datePosted",
        "div.ij-OfferDetail-jobDetailsList-item span",
        "div.ij-OfferDetail-distribution span",
        "time",
        "span.date",
        "span.posted-on"  # Genérico
    ]
    
    date_tag = None
    for selector in date_selectors:
        date_tag = soup.select_one(selector)
        if date_tag:
            break
    
    one_month_ago = datetime.now().date() - timedelta(days=30)
    
    if date_tag:
        # Si el elemento tiene un atributo datetime (formato ISO)
        if date_tag.get("datetime"):
            date_text = date_tag.get("datetime")
            logger.info(f"Fecha encontrada en atributo datetime: {date_text}")
            try:
                pub_date = datetime.strptime(date_text, "%Y-%m-%d").date()
                return pub_date
            except (ValueError, TypeError):
                pass
        
        # Si no, obtener el texto del elemento
        date_text = date_tag.get_text(strip=True).lower()
        logger.info(f"Texto de fecha encontrado: {date_text}")
        
        # Manejar diferentes formatos de fecha
        try:
            # Formato "dd/mm/yyyy"
            pub_date = datetime.strptime(date_text, '%d/%m/%Y').date()
            return pub_date
        except (ValueError, TypeError):
            pass
        
        try:
            # Formato "hace X días"
            match = re.search(r'hace (\d+) (día|días)', date_text)
            if match:
                days_ago = int(match.group(1))
                pub_date = datetime.now().date() - timedelta(days=days_ago)
                return pub_date
        except:
            pass
        
        try:
            # Formato "ayer"
            if "ayer" in date_text:
                pub_date = datetime.now().date() - timedelta(days=1)
                return pub_date
        except:
            pass
        
        try:
            # Formato "hoy"
            if "hoy" in date_text:
                pub_date = datetime.now().date()
                return pub_date
        except:
            pass
        
        try:
            # Formato "hace X horas"
            match = re.search(r'hace (\d+) (hora|horas)', date_text)
            if match:
                pub_date = datetime.now().date()
                return pub_date
        except:
            pass
    
    logger.warning("No se pudo determinar la fecha de publicación, usando fecha por defecto (hace 30 días)")
    return one_month_ago

def apply_human_like_scrolling(driver):
    try:
        total_height = driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        step = random.randint(300, 500)
        
        while current_position < total_height:
            next_position = min(current_position + step, total_height)
            driver.execute_script(f"window.scrollTo({current_position}, {next_position})")
            current_position = next_position
            time.sleep(random.uniform(0.05, 0.15))
        
        if random.random() < 0.5:
            driver.execute_script("window.scrollTo(0, 0)")
            time.sleep(random.uniform(0.3, 0.7))
    except Exception as e:
        logger.warning(f"Error al aplicar scroll humano: {e}")

def show_results_messages(request, offers):
    if offers:
        min_date = min(o.publication_date for o in offers).strftime("%d/%m/%Y")
        max_date = max(o.publication_date for o in offers).strftime("%d/%m/%Y")
        
        messages.success(request, f"Se han extraído {len(offers)} ofertas de InfoJobs.")
        messages.success(request, f"Esta actualización incluye ofertas desde {min_date} hasta {max_date}.")
        
        remote_count = sum(1 for o in offers if any(term in o.location.lower() for term in ["remoto", "híbrido", "teletrabajo"]))
        if remote_count > 0:
            messages.info(request, f"{remote_count} de las ofertas son remotas o híbridas.")
        
        locations = {}
        for offer in offers:
            location = offer.location.split("(")[0].strip()
            locations[location] = locations.get(location, 0) + 1
        
        top_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_locations:
            location_msg = "Principales ubicaciones: " + ", ".join([f"{loc} ({count})" for loc, count in top_locations])
            messages.info(request, location_msg)
    else:
        messages.warning(request, "No se encontraron ofertas. Revisa los logs y 'infojobs_debug.html' para depurar.")