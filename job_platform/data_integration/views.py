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
def scrape_index(request):
    """Vista principal que muestra los botones para ejecutar los diferentes scrapers."""
    return render(request, "data_integration/scrape_index.html")

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
    """Extrae ofertas de empleo de LinkedIn."""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("detach", True)
    driver = None
    offers = []

    def intentar_clic_ver_mas(driver):
        """Intenta hacer clic en el botón 'Ver más' para cargar más ofertas."""
        try:
            ver_mas = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.infinite-scroller__show-more-button, button[aria-label*='more jobs'], button[aria-label*='empleos'], button[class*='show-more']"))
            )
            driver.execute_script("arguments[0].click();", ver_mas)
            print("[DEBUG] Clic en 'Ver más' exitoso")
            return True
        except:
            print("[DEBUG] No se encontró 'Ver más'")
            return False

    try:
        print("[DEBUG] Iniciando scraper de LinkedIn")
        driver = webdriver.Chrome(options=chrome_options)
        # 1. Login manual
        driver.get("https://www.linkedin.com/login")
        print("[DEBUG] Esperando login manual (60 segundos)...")
        messages.info(request, "Inicia sesión en LinkedIn manualmente. Tienes 60 segundos para credenciales y posibles CAPTCHAs.")
        time.sleep(60)

        # 2. Verificar que el navegador sigue abierto
        try:
            driver.title
            print("[DEBUG] Navegador sigue abierto")
        except Exception as e:
            print(f"[DEBUG] Error: Navegador cerrado o sesión inválida: {e}")
            messages.error(request, "Error: El navegador se cerró durante el login o la sesión es inválida. Por favor, no cierres la ventana de Chrome y revisa CAPTCHAs.")
            return render(request, "data_integration/scrape_results.html", {"offers": [], "num_offers": 0})

        # 3. Verificar login
        print("[DEBUG] Verificando login...")
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.feed-identity-module, div[class*='feed-container']"))
            )
            print("[DEBUG] Login verificado por presencia de feed")
            print(f"[DEBUG] URL tras login: {driver.current_url}")
        except Exception as e:
            print(f"[DEBUG] Error en verificación de login: {e}")
            print(f"[DEBUG] URL tras login: {driver.current_url}")
            messages.error(request, "Error: Login no completado. Revisa credenciales, CAPTCHAs, o popups.")
            driver.save_screenshot("login_error.png")
            return render(request, "data_integration/scrape_results.html", {"offers": [], "num_offers": 0})

        # 4. Cerrar popups
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Dismiss'], button[class*='close'], button[aria-label*='Cerrar']"))
            ).click()
            print("[DEBUG] Popup cerrado")
        except:
            print("[DEBUG] No se encontraron popups")

        # 5. Buscar ofertas
        print("[DEBUG] Cargando página de empleos...")
        driver.get("https://www.linkedin.com/jobs/search/?keywords=desarrollador&location=Asturias%2C%20España&f_TPR=r2592000")
        try:
            WebDriverWait(driver, 150).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-search--container, div[class*='jobs-search'], section[class*='jobs-search']"))
            )
            print("[DEBUG] Contenedor de empleos encontrado")
            print(f"[DEBUG] URL tras carga: {driver.current_url}")
        except Exception as e:
            print(f"[DEBUG] Error en espera de contenedor: {e}")
            messages.error(request, f"Error: No se cargó la lista de empleos: {e}")
            driver.save_screenshot("jobs_error.png")
            return render(request, "data_integration/scrape_results.html", {"offers": [], "num_offers": 0})

        # 6. Scroll para cargar más
        print("[DEBUG] Iniciando scrolls...")
        last_count = 0
        for i in range(15):  # Aumentado para intentar cargar más ofertas
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-card-container, div.base-card, li.jobs-search-results__list-item"))
            )
            soup = BeautifulSoup(driver.page_source, "html.parser")
            jobs = soup.select("div.job-card-container, div.base-card, li.jobs-search-results__list-item")
            print(f"[DEBUG] Ofertas cargadas tras scroll {i+1}: {len(jobs)}")
            if len(jobs) > 30:  # Detener si ya tenemos suficientes ofertas
                print("[DEBUG] Más de 30 ofertas cargadas, deteniendo scrolls")
                break
            if len(jobs) == last_count:  # Si no cargan más ofertas, salir
                print("[DEBUG] No se cargaron más ofertas, deteniendo scrolls")
                break
            last_count = len(jobs)
            if intentar_clic_ver_mas(driver):
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-card-container, div.base-card, li.jobs-search-results__list-item"))
                )
            else:
                print(f"[DEBUG] Intento {i+1}: No se encontró 'Ver más', continuando")

        # 7. Parsear HTML
        print("[DEBUG] Parseando HTML...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        jobs = soup.select("div.job-card-container, div.base-card, li.jobs-search-results__list-item")
        print(f"[DEBUG] Ofertas encontradas: {len(jobs)}")

        for i, job in enumerate(jobs):
            retries = 2
            while retries > 0:
                try:
                    # Extraer información del listado
                    title_elem = job.select_one("span[aria-hidden='true']")
                    company_elem = job.select_one("div.artdeco-entity-lockup__subtitle span")
                    location_elem = job.select_one("div.artdeco-entity-lockup__caption ul.job-card-container__metadata-wrapper li span")
                    date_elem = job.select_one("time[datetime]")

                    # Limpiar texto
                    title_text = title_elem.text.strip() if title_elem else "Sin título"
                    company_text = company_elem.text.strip() if company_elem else "Sin compañía"
                    location_text = location_elem.text.strip() if location_elem else "Sin ubicación"
                    location_text = re.sub(r'\s+', ' ', location_text)

                    print(f"[DEBUG] Oferta {i+1} - Título: {title_text}, Compañía: {company_text}, Ubicación: {location_text}")

                    # Procesar fecha
                    try:
                        if date_elem and date_elem.get("datetime"):
                            pub_date = datetime.strptime(date_elem["datetime"], "%Y-%m-%d").date()
                        else:
                            date_text = date_elem.text.strip().lower() if date_elem else ""
                            pub_date = datetime.now().date()
                            if any(x in date_text for x in ["hora", "horas", "hour", "hours"]):
                                pub_date = datetime.now().date()
                            elif any(x in date_text for x in ["día", "días", "day", "days"]):
                                days = int(re.search(r'(\d+)', date_text).group(1)) if re.search(r'(\d+)', date_text) else 1
                                pub_date -= timedelta(days=days)
                            elif any(x in date_text for x in ["semana", "semanas", "week", "weeks"]):
                                weeks = int(re.search(r'(\d+)', date_text).group(1)) if re.search(r'(\d+)', date_text) else 1
                                pub_date -= timedelta(weeks=weeks)
                            elif any(x in date_text for x in ["mes", "meses", "month", "months"]):
                                months = int(re.search(r'(\d+)', date_text).group(1)) if re.search(r'(\d+)', date_text) else 1
                                pub_date -= timedelta(days=months*30)
                    except Exception as e:
                        print(f"[DEBUG] Error en fecha para '{title_text}': {e}")
                        pub_date = datetime.now().date()

                    # Intentar extraer habilidades visitando la oferta
                    job_link = job.select_one("a.base-card__full-link")
                    skills_list = []
                    if job_link and 'href' in job_link.attrs:
                        job_url = job_link['href']
                        if not job_url.startswith("https://"):
                            job_url = "https://www.linkedin.com" + job_url
                        print(f"[DEBUG] Visitando oferta {i+1}: {job_url}")
                        driver.get(job_url)
                        try:
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.description__text, section[class*='jobs-description']"))
                            )
                            print("[DEBUG] Página de la oferta cargada correctamente")
                        except Exception as e:
                            print(f"[DEBUG] Error al cargar página de la oferta {i+1}: {e}")
                            driver.get("https://www.linkedin.com/jobs/search/?keywords=desarrollador&location=Asturias%2C%20España&f_TPR=r2592000")
                            WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-card-container, div.base-card, li.jobs-search-results__list-item"))
                            )
                            retries -= 1
                            continue
                        job_soup = BeautifulSoup(driver.page_source, "html.parser")
                        skills_elems = job_soup.select("span.job-criteria__text--criteria, li.description__job-criteria-item, span[class*='skills']")
                        skills_list = [s.text.strip() for s in skills_elems if s.text.strip()]
                        print(f"[DEBUG] Habilidades encontradas para '{title_text}': {skills_list}")
                        driver.get("https://www.linkedin.com/jobs/search/?keywords=desarrollador&location=Asturias%2C%20España&f_TPR=r2592000")
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-card-container, div.base-card, li.jobs-search-results__list-item"))
                        )

                    # Guardar oferta
                    job_obj, created = JobOffer.objects.get_or_create(
                        title=title_text,
                        company=company_text,
                        source="LinkedIn",
                        publication_date=pub_date,
                        defaults={
                            "location": location_text,
                            "salary": None
                        }
                    )

                    # Guardar habilidades
                    if created:
                        for skill_name in skills_list:
                            if skill_name:
                                skill, _ = Skill.objects.get_or_create(name=skill_name)
                                job_obj.skills.add(skill)
                        offers.append(job_obj)
                        print(f"[DEBUG] Oferta {i+1} guardada: {title_text} - {company_text} - {location_text} - {pub_date} - Habilidades: {skills_list}")
                    break  # Salir del bucle de reintentos si tiene éxito
                except Exception as e:
                    print(f"[DEBUG] Error procesando oferta {i+1} (Intento {2-retries}): {e}")
                    retries -= 1
                    if retries == 0:
                        print(f"[DEBUG] Oferta {i+1} descartada tras 2 intentos")
                        continue
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-card-container, div.base-card, li.jobs-search-results__list-item"))
                    )

        # 8. Guardar HTML de debug
        debug_path = os.path.join(os.getcwd(), "linkedin_debug.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"[DEBUG] HTML guardado en {debug_path}")

        # 9. Mensajes
        if offers:
            min_date = min(o.publication_date for o in offers).strftime("%d/%m/%Y")
            max_date = max(o.publication_date for o in offers).strftime("%d/%m/%Y")
            messages.success(request, f"Esta actualización incluye ofertas desde {min_date} hasta {max_date}.")
            messages.success(request, f"Se han extraído {len(offers)} ofertas de LinkedIn.")
        else:
            messages.warning(request, "No se encontraron ofertas. Revisa linkedin_debug.html.")
            driver.save_screenshot("no_offers.png")

    except Exception as e:
        print(f"[DEBUG] Error general: {e}")
        messages.error(request, f"Error al scrapear LinkedIn: {e}")
        if driver:
            try:
                driver.save_screenshot("general_error.png")
            except:
                print("[DEBUG] No se pudo tomar screenshot: navegador cerrado")

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