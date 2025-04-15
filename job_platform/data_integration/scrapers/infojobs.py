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
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os
import re
import random

@has_role_decorator('admin')
def scrape_infojobs(request):
    """
    Extrae 10 ofertas de empleo de InfoJobs en España.
    Optimizado para ejecutarse en menos de 1 minuto.
    """
    # PASO 1: Configurar el navegador Chrome para el scraping
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--dns-prefetch-disable")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("detach", True)
    driver = None
    offers = []
    processed_urls = set()

    try:
        # PASO 2: Iniciar el navegador y comenzar el scraping
        print("[DEBUG] Iniciando scraper de InfoJobs")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # PASO 3: Cargar la página de búsqueda (toda España)
        search_url = "https://www.infojobs.net/jobsearch/search-results/list.xhtml?keyword=desarrollador&sortBy=RELEVANCE"
        driver.get(search_url)
        print("[DEBUG] Cargando página de búsqueda...")

        # Manejar el popup de cookies
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            ).click()
            print("[DEBUG] Popup de cookies aceptado")
        except:
            print("[DEBUG] No se encontró popup de cookies o ya fue aceptado")

        # PASO 4: Detectar y manejar CAPTCHA manualmente
        try:
            captcha = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='captcha']"))
            )
            if captcha:
                print("[DEBUG] CAPTCHA detectado. Por favor, resuelve el CAPTCHA manualmente en el navegador.")
                messages.warning(request, "Se detectó un CAPTCHA. Por favor, resuelve el CAPTCHA en el navegador que se abrió y espera 30 segundos para que el scraper continúe.")
                time.sleep(30)  # Pausar para que resuelvas el CAPTCHA
                print("[DEBUG] Continuando después de 30 segundos...")
        except:
            print("[DEBUG] No se detectó CAPTCHA, continuando...")

        # PASO 5: Recolectar URLs de ofertas
        all_offer_urls = set()
        max_urls = 20  # Recolectar hasta 20 URLs para asegurar suficientes ofertas
        page = 1
        max_pages = 2  # Limitar a 2 páginas para mantener el tiempo bajo

        while page <= max_pages and len(all_offer_urls) < max_urls:
            print(f"[DEBUG] Procesando página {page}...")
            try:
                # Esperar a que las ofertas sean visibles
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/ofertas-trabajo/']"))
                )
                print(f"[DEBUG] Ofertas cargadas en página {page}")
            except Exception as e:
                print(f"[DEBUG] Error al cargar ofertas en página {page}: {e}")
                break

            # Desplazarse hasta el final de la página
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(0.2, 0.3))

            # Parsear la página actual
            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_links = soup.select("a[href*='/ofertas-trabajo/']")
            for link in job_links:
                href = link.get("href")
                if href and "/ofertas-trabajo/" in href:
                    full_url = f"https://www.infojobs.net{href.split('?')[0]}"
                    if full_url not in processed_urls:
                        all_offer_urls.add(full_url)
                        processed_urls.add(full_url)
                        print(f"[DEBUG] URL encontrada: {full_url}")
                        if len(all_offer_urls) >= max_urls:
                            break

            # Intentar cargar más resultados o ir a la siguiente página
            try:
                next_button = driver.find_element(By.CLASS_NAME, "ij-ShowMoreResults-button")
                if next_button:
                    next_button.click()
                    time.sleep(random.uniform(0.2, 0.3))
                    page += 1
                else:
                    break
            except:
                print("[DEBUG] No se encontró botón de 'Mostrar más' o fin de páginas")
                break

        all_offer_urls = list(all_offer_urls)
        print(f"[DEBUG] Total URLs únicas recolectadas: {len(all_offer_urls)}")

        # PASO 6: Procesar cada oferta para extraer detalles
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
                    soup = BeautifulSoup(driver.page_source, "html.parser")

                    # Extraer título
                    title_tag = soup.select_one("h1.ij-OfferDetail-title")
                    title = title_tag.get_text(strip=True)[:255] if title_tag else "Sin título"

                    # Extraer compañía
                    company_tag = soup.select_one("a.ij-OfferDetail-companyName")
                    company = company_tag.get_text(strip=True)[:255] if company_tag else "Sin compañía"

                    # Extraer ubicación
                    location_tag = soup.select_one("span[data-test='job-detail-location']")
                    description_tag = soup.select_one("div.ij-OfferDetail-description")
                    description = description_tag.get_text(strip=True).lower() if description_tag else "No especificada"

                    if location_tag:
                        location_text = location_tag.get_text(strip=True)
                        location = location_text[:255]
                        modality = ""
                        # Intentar detectar modalidad (remoto/híbrido) en la descripción
                        remote_terms = ["remoto", "remote", "teletrabajo", "100% remoto", "telecommute", "work from home", "híbrido", "hybrid"]
                        is_remote = any(term in description for term in remote_terms)
                        final_location = location
                        if is_remote:
                            final_location = f"{location} (Remoto/Híbrido)"
                    else:
                        location = "Ubicación no especificada"
                        final_location = location

                    # Verificar si la oferta es en Asturias
                    location_lower = location.lower()
                    is_asturias = any(loc in location_lower for loc in ["asturias", "gijón", "oviedo", "principado de asturias"])

                    # Extraer habilidades
                    skills_list = []
                    skills_section = soup.select("li[data-test='job-detail-skill']")
                    if skills_section:
                        skills_list = [skill.get_text(strip=True) for skill in skills_section if skill.get_text(strip=True)]
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

                    # Extraer fecha de publicación
                    date_tag = soup.select_one("span[data-test='job-detail-publication-date']")
                    one_month_ago = datetime.now().date() - timedelta(days=30)
                    if date_tag:
                        date_text = date_tag.get_text(strip=True)
                        try:
                            pub_date = datetime.strptime(date_text, '%d/%m/%Y').date()
                        except (ValueError, TypeError):
                            # Intentar parsear fechas relativas como "hace X días"
                            match = re.search(r'hace (\d+) (día|días)', date_text.lower())
                            if match:
                                days_ago = int(match.group(1))
                                pub_date = datetime.now().date() - timedelta(days=days_ago)
                            else:
                                pub_date = one_month_ago
                    else:
                        print("[DEBUG] Fecha no encontrada, usando fecha de hace un mes.")
                        pub_date = one_month_ago
                    print(f"[DEBUG] Fecha final para '{title}': {pub_date}")

                    # Filtrar ofertas mayores a un mes
                    if pub_date < one_month_ago:
                        print(f"[DEBUG] Oferta descartada (muy antigua): {title}")
                        continue

                    # Guardar la oferta
                    job_obj, created = JobOffer.objects.get_or_create(
                        source="InfoJobs",
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

            if len(offers) >= 10:  # Limitar a 10 ofertas
                print("[DEBUG] Se han recolectado 10 ofertas, deteniendo procesamiento.")
                break

        # PASO 7: Guardar el HTML de la página para depuración
        debug_path = os.path.join(os.getcwd(), "infojobs_debug.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"[DEBUG] HTML guardado en {debug_path}")

        # PASO 8: Mostrar mensajes con los resultados
        if offers:
            min_date = min(o.publication_date for o in offers).strftime("%d/%m/%Y")
            max_date = max(o.publication_date for o in offers).strftime("%d/%m/%Y")
            messages.success(request, f"Esta actualización incluye ofertas desde {min_date} hasta {max_date}.")
            messages.success(request, f"Se han extraído {len(offers)} ofertas de InfoJobs.")
            remote_count = sum(1 for o in offers if "remoto" in o.location.lower() or "híbrido" in o.location.lower())
            if remote_count > 0:
                messages.info(request, f"{remote_count} de las ofertas son remotas o híbridas.")
            if asturias_offers:
                messages.info(request, f"Se encontraron {len(asturias_offers)} ofertas en Asturias.")
            else:
                messages.info(request, "No se encontraron ofertas específicas en Asturias.")
        else:
            messages.warning(request, "No se encontraron ofertas. Revisa 'infojobs_debug.html'.")
            driver.save_screenshot("no_offers_infojobs.png")

    except Exception as e:
        print(f"[DEBUG] Error general: {e}")
        messages.error(request, f"Error al scrapear InfoJobs: {e}")
        if driver:
            driver.save_screenshot("general_error_infojobs.png")

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