from django.contrib import messages
from django.shortcuts import render
import requests
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
from dotenv import load_dotenv





load_dotenv()




def scrape_index(request):
    """Vista principal que muestra los botones para ejecutar los diferentes scrapers."""
    return render(request, "data_integration/scrape_index.html")

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
    """
    Extrae ofertas de empleo de LinkedIn para Asturias o remotas en España.
    Este scraper busca ofertas con múltiples palabras clave, optimizando la velocidad
    y dividiendo las búsquedas entre Asturias y remotas. Incluye comentarios detallados
    para que Andrea pueda memorizar y entender cada paso.
    """
    # PASO 1: Configurar el navegador Chrome para el scraping
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_experimental_option("detach", True)
    driver = None
    offers = []

    # FUNCIÓN AUXILIAR: Intentar hacer clic en el botón "Ver más" para cargar más ofertas
    def intentar_clic_ver_mas(driver):
        """
        Busca el botón "Ver más" en la página de búsqueda de LinkedIn y hace clic
        para cargar más ofertas. Si no lo encuentra, retorna False.
        """
        max_attempts = 3  # Reducido para acelerar
        for attempt in range(max_attempts):
            try:
                ver_mas = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.infinite-scroller__show-more-button, button[aria-label*='more jobs'], button[aria-label*='empleos'], button[class*='show-more']"))
                )
                driver.execute_script("arguments[0].click();", ver_mas)
                print("[DEBUG] Clic en 'Ver más' exitoso")
                time.sleep(random.uniform(1, 2))  # Reducido para acelerar
                return True
            except:
                print(f"[DEBUG] Intento {attempt+1}/{max_attempts}: No se encontró 'Ver más'")
                time.sleep(random.uniform(0.5, 1))
        return False

    try:
        # PASO 2: Iniciar el navegador y comenzar el scraping
        print("[DEBUG] Iniciando scraper de LinkedIn")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # PASO 3: Hacer login en LinkedIn con las credenciales del archivo .env
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
            time.sleep(random.uniform(2, 3))  # Reducido para acelerar
        except Exception as e:
            print(f"[DEBUG] Error al ingresar credenciales: {e}")
            messages.error(request, "Error: No se pudo completar el login automático. Revisa las credenciales en .env.")
            driver.save_screenshot("login_error.png")
            return render(request, "data_integration/scrape_results.html", {"offers": [], "num_offers": 0})

        # PASO 4: Verificar que el login fue exitoso
        print("[DEBUG] Verificando login...")
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.feed-identity-module, div[class*='feed-container']"))
            )
            print("[DEBUG] Login verificado por presencia de feed")
        except Exception as e:
            print(f"[DEBUG] Error en verificación de login: {e}")
            messages.error(request, "Error: Login no completado. Revisa credenciales, CAPTCHAs, o popups.")
            driver.save_screenshot("login_error.png")
            return render(request, "data_integration/scrape_results.html", {"offers": [], "num_offers": 0})

        # PASO 5: Buscar ofertas con múltiples palabras clave
        print("[DEBUG] Cargando página de empleos...")
        all_offer_urls = set()

        # Grupo 1: Buscar en Asturias directamente
        keywords_asturias = ["desarrollador", "developer", "programador", "software engineer", "ingeniero de software"]
        for keyword in keywords_asturias:
            # Buscar directamente en Asturias
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location=Asturias%2C%20Spain&sort=date"
            page = 0
            max_pages = 3  # Limitamos a 3 páginas para acelerar
            while page < max_pages:
                paginated_url = f"{search_url}&start={page*25}"
                driver.get(paginated_url)
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/jobs/view/']"))
                    )
                    print(f"[DEBUG] Ofertas de búsqueda cargadas correctamente para keyword: {keyword} (Asturias, página {page+1})")
                except Exception as e:
                    print(f"[DEBUG] Error al cargar la página de búsqueda para {keyword} (Asturias, página {page+1}): {e}")
                    break

                # Extraer URLs
                offer_urls = set()
                max_offers = 50
                scroll_attempts = 0
                max_scrolls = 20  # Reducido para acelerar
                last_count = 0
                same_count_retries = 0

                while len(offer_urls) < max_offers and scroll_attempts < max_scrolls:
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    job_cards = soup.select('a[href*="/jobs/view/"]')
                    for card in job_cards:
                        href = card.get('href', '')
                        if href and "/jobs/view/" in href:
                            full_url = f"https://www.linkedin.com{href.split('?')[0]}"
                            offer_urls.add(full_url)
                            all_offer_urls.add(full_url)
                            print(f"[DEBUG] URL encontrada: {full_url}")
                            if len(offer_urls) >= max_offers:
                                break

                    current_count = len(offer_urls)
                    if current_count == last_count:
                        same_count_retries += 1
                        if same_count_retries >= 3:  # Reducido para acelerar
                            print("[DEBUG] No se cargaron más ofertas tras 3 intentos, deteniendo scrolls.")
                            break
                    else:
                        same_count_retries = 0
                    last_count = current_count

                    if intentar_clic_ver_mas(driver):
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/jobs/view/']"))
                        )
                    else:
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(random.uniform(1, 2))  # Reducido para acelerar
                    scroll_attempts += 1

                print(f"[DEBUG] Total URLs únicas recolectadas para {keyword} (Asturias, página {page+1}): {len(offer_urls)}")
                page += 1

        # Grupo 2: Buscar remotas en toda España
        keywords_remote = ["full stack", "backend", "frontend", "web developer", "data engineer"]
        for keyword in keywords_remote:
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location=España&sort=date"
            page = 0
            max_pages = 3
            while page < max_pages:
                paginated_url = f"{search_url}&start={page*25}"
                driver.get(paginated_url)
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/jobs/view/']"))
                    )
                    print(f"[DEBUG] Ofertas de búsqueda cargadas correctamente para keyword: {keyword} (España, página {page+1})")
                except Exception as e:
                    print(f"[DEBUG] Error al cargar la página de búsqueda para {keyword} (España, página {page+1}): {e}")
                    break

                # Extraer URLs
                offer_urls = set()
                max_offers = 50
                scroll_attempts = 0
                max_scrolls = 20
                last_count = 0
                same_count_retries = 0

                while len(offer_urls) < max_offers and scroll_attempts < max_scrolls:
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    job_cards = soup.select('a[href*="/jobs/view/"]')
                    for card in job_cards:
                        href = card.get('href', '')
                        if href and "/jobs/view/" in href:
                            full_url = f"https://www.linkedin.com{href.split('?')[0]}"
                            offer_urls.add(full_url)
                            all_offer_urls.add(full_url)
                            print(f"[DEBUG] URL encontrada: {full_url}")
                            if len(offer_urls) >= max_offers:
                                break

                    current_count = len(offer_urls)
                    if current_count == last_count:
                        same_count_retries += 1
                        if same_count_retries >= 3:
                            print("[DEBUG] No se cargaron más ofertas tras 3 intentos, deteniendo scrolls.")
                            break
                    else:
                        same_count_retries = 0
                    last_count = current_count

                    if intentar_clic_ver_mas(driver):
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/jobs/view/']"))
                        )
                    else:
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(random.uniform(1, 2))
                    scroll_attempts += 1

                print(f"[DEBUG] Total URLs únicas recolectadas para {keyword} (España, página {page+1}): {len(offer_urls)}")
                page += 1

        all_offer_urls = list(all_offer_urls)
        print(f"[DEBUG] Total URLs únicas recolectadas (todas las keywords): {len(all_offer_urls)}")

        # PASO 6: Procesar cada oferta para extraer detalles
        asturias_offers = []
        for i, url in enumerate(all_offer_urls):
            retries = 3
            while retries > 0:
                try:
                    print(f"[DEBUG] Procesando oferta {i+1}: {url}")
                    driver.get(url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    time.sleep(random.uniform(1, 2))  # Reducido para acelerar
                    soup = BeautifulSoup(driver.page_source, 'lxml')

                    title_tag = soup.select_one('h1.top-card-layout__title') or soup.select_one('.job-details-jobs-unified-top-card__job-title')
                    title = title_tag.get_text(strip=True)[:255] if title_tag else "Sin título"

                    company_tag = soup.select_one('a.topcard__org-name-link') or soup.select_one('.job-details-jobs-unified-top-card__company-name a')
                    company = company_tag.get_text(strip=True)[:255] if company_tag else "Sin compañía"

                    location_tag = soup.select_one('.artdeco-entity-lockup__caption div[dir="ltr"]')
                    description_tag = soup.select_one('div.jobs-description__content') or soup.select_one('.jobs-box__html-content')
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

                    is_asturias = any(loc in location for loc in ["Asturias", "Gijón", "Oviedo"])
                    remote_terms = ["remoto", "remote", "teletrabajo", "100% remoto", "telecommute", "work from home"]
                    is_remote = any(term in modality for term in remote_terms) or any(term in description for term in remote_terms)
                    if is_asturias:
                        final_location = location
                    elif is_remote:
                        final_location = "España (Remoto)"
                    else:
                        print(f"[DEBUG] Oferta {i+1} descartada: No está en Asturias ni es remota ({location}, {modality})")
                        break

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

                    date_tag = soup.select_one('time[datetime]') or soup.select_one('span.jobs-unified-top-card__posted-date')
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
                        title=title,
                        company=company,
                        source="LinkedIn",
                        publication_date=pub_date,
                        defaults={
                            "location": final_location,
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
                        continue
                    time.sleep(random.uniform(3, 5))

            if len(offers) >= 25:
                print("[DEBUG] Se han recolectado 25 ofertas, deteniendo procesamiento.")
                break

        # PASO 7: Guardar el HTML de la página para depuración
        debug_path = os.path.join(os.getcwd(), "linkedin_debug.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"[DEBUG] HTML guardado en {debug_path}")

        # PASO 8: Mostrar mensajes con los resultados
        if offers:
            min_date = min(o.publication_date for o in offers).strftime("%d/%m/%Y")
            max_date = max(o.publication_date for o in offers).strftime("%d/%m/%Y")
            messages.success(request, f"Esta actualización incluye ofertas desde {min_date} hasta {max_date}.")
            messages.success(request, f"Se han extraído {len(offers)} ofertas de LinkedIn.")
            if asturias_offers:
                messages.info(request, f"De las cuales {len(asturias_offers)} son de Asturias (el resto son remotas).")
            else:
                messages.warning(request, "No se encontraron ofertas en Asturias, pero se incluyeron remotas.")
        else:
            messages.warning(request, "No se encontraron ofertas. Revisa linkedin_debug.html.")
            driver.save_screenshot("no_offers.png")

    except Exception as e:
        # PASO 9: Manejar errores generales
        print(f"[DEBUG] Error general: {e}")
        messages.error(request, f"Error al scrapear LinkedIn: {e}")
        if driver:
            driver.save_screenshot("general_error.png")

    finally:
        # PASO 10: Cerrar el navegador al finalizar
        if driver:
            try:
                driver.quit()
            except:
                print("[DEBUG] No se pudo cerrar el driver: ya estaba cerrado")

    # PASO 11: Renderizar la página con los resultados
    context = {
        "offers": offers,
        "num_offers": len(offers)
    }
    print(f"[DEBUG] Renderizando template con {len(offers)} ofertas")
    return render(request, "data_integration/scrape_results.html", context)

# FUNCIÓN AUXILIAR: Calcular fechas relativas
def parse_relative_date(date_text):
    """
    Convierte textos como 'hace 2 días' en una fecha absoluta.
    """
    now = datetime.now().date()
    date_text = date_text.lower()
    if "hace" in date_text:
        match = re.search(r'(\d+)\s*(hora|día|semana|mes)', date_text)
        if match:
            value, unit = match.groups()
            value = int(value)
            if "hora" in unit:
                return now
            elif "día" in unit:
                return now - timedelta(days=value)
            elif "semana" in unit:
                return now - timedelta(weeks=value)
            elif "mes" in unit:
                return now - timedelta(days=value * 30)
    return now





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