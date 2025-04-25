# data_integration/scrapers/linkedin.py
# Este script realiza scraping de ofertas de trabajo desde LinkedIn.
# Extrae información como título, empresa y ubicación de las ofertas.
# El proceso puede demorar varios minutos dependiendo del número de ofertas a extraer y las restricciones de LinkedIn.
import re
import time
import logging
import os
import unicodedata
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from rolepermissions.decorators import has_role_decorator
from market_analysis.models import JobOffer, Skill
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

# Función para iniciar el scraping de LinkedIn desde una vista.
# Crea una instancia del scraper y ejecuta el proceso de extracción de ofertas.
# Maneja excepciones y muestra mensajes de éxito o error en la interfaz de usuario.
@has_role_decorator(['admin', 'collaborator'])
def scrape_linkedin(request):
    scraper = LinkedInScraper()
    try:
        offers = scraper.run(
            query="software developer",
            location="Spain",
            max_offers=10
        )
        messages.success(request, f"Se han extraído {len(offers)} ofertas de LinkedIn.")
        context = {
            'offers': offers,
            'num_offers': len(offers)
        }
        return render(request, 'data_integration/scrape_results.html', context)
    except Exception as e:
        messages.error(request, f"Error al scrapear LinkedIn: {e}")
        return render(request, 'data_integration/scrape_results.html', {'offers': []})

# Clase que define el scraper de LinkedIn.
# Hereda de BaseScraper y maneja la lógica de extracción de datos.
# Utiliza Selenium para interactuar con la página web de LinkedIn de manera automatizada.
class LinkedInScraper(BaseScraper):
    def __init__(self):
        # Inicializa el scraper con la URL base de LinkedIn y configura el navegador.
        # Muestra advertencias sobre el uso del scraper debido a posibles violaciones de los Términos de Servicio.
        # Configura el navegador en modo headless para evitar mostrar la interfaz gráfica.
        # Utiliza ChromeDriverManager para gestionar la instalación del controlador de Chrome.
        super().__init__("LinkedIn", "https://www.linkedin.com")
        logger.warning("\n" + "*" * 70)
        logger.warning("ADVERTENCIA: Scraping de LinkedIn en curso.")
        logger.warning("Esto puede violar los Términos de Servicio de LinkedIn y resultar en bloqueos.")
        logger.warning("Usa este código bajo tu propio riesgo y con moderación.")
        logger.warning("Ejecutando en modo headless (sin navegador visible).")
        logger.warning("*" * 70 + "\n")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        chrome_options.add_argument("--lang=en-US")  # Forzar idioma inglés

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Método para iniciar sesión en LinkedIn.
    # Utiliza las credenciales almacenadas en variables de entorno para acceder a la cuenta.
    # Verifica si el inicio de sesión fue exitoso comprobando la URL actual.
    # Captura y maneja errores durante el proceso de inicio de sesión.
    def login(self, username, password):
        logger.info("Iniciando sesión en LinkedIn...")
        self.driver.get("https://www.linkedin.com/login")
        time.sleep(2)

        try:
            email_field = self.driver.find_element(By.ID, "username")
            email_field.send_keys(username)

            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)

            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(5)

            if "feed" in self.driver.current_url:
                logger.info("Inicio de sesión exitoso.")
            else:
                logger.error("Error al iniciar sesión. Puede haber CAPTCHA, 2FA o credenciales incorrectas.")
                self.driver.save_screenshot("login_error.png")
                raise Exception("No se pudo iniciar sesión en LinkedIn.")
        except Exception as e:
            logger.error(f"Error durante el inicio de sesión: {e}")
            raise

    # Método para buscar ofertas de trabajo en LinkedIn.
    # Realiza una búsqueda basada en la consulta y ubicación proporcionadas, y maneja posibles CAPTCHA.
    # Implementa un sistema de reintentos para manejar CAPTCHA y otros problemas de carga de página.
    # Utiliza BeautifulSoup para analizar el HTML de la página y extraer URLs de ofertas de trabajo.
    def fetch_offers(self, query="software developer", location="Spain", max_offers=10):
        if not query or not query.strip():
            logger.error("Query vacía o inválida proporcionada")
            return []
        
        logger.info(f"Buscando ofertas en LinkedIn: query='{query}', location='{location}', max_offers={max_offers}")
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}&sort=date"
        self.driver.get(search_url)
        time.sleep(5)

        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        max_attempts = 3
        attempt = 0

        while ("challenge" in self.driver.current_url or
               "verify" in self.driver.current_url or
               soup.select_one('input[id="captcha"]')):
            if attempt >= max_attempts:
                logger.error("Demasiados intentos fallidos de CAPTCHA. Abortando...")
                return []
            logger.warning(f"Intento {attempt + 1}/{max_attempts}: CAPTCHA o verificación detectada.")
            logger.warning(f"URL actual: {self.driver.current_url}")
            logger.warning(f"Fragmento de página: {soup.text[:200]}...")
            self.driver.save_screenshot(f"captcha_detected_attempt_{attempt}.png")
            logger.warning("Modo headless activo: no se puede resolver CAPTCHA manualmente. Saltando...")
            break
            time.sleep(5)
            self.driver.get(search_url)
            time.sleep(5)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            attempt += 1

        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.debug("Página básica cargada.")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/jobs/view/']"))
            )
            logger.debug("Ofertas de búsqueda cargadas correctamente.")
        except Exception as e:
            logger.error(f"Error al cargar la página de búsqueda: {e}")
            self.driver.save_screenshot("search_error.png")
            with open("linkedin_search.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            return []

        offer_urls = []
        scroll_attempts = 0
        max_scrolls = 5

        while len(offer_urls) < max_offers and scroll_attempts < max_scrolls:
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            job_cards = soup.select('a[href*="/jobs/view/"]')
            for card in job_cards:
                href = card.get('href', '')
                if href and href not in offer_urls and "/jobs/view/" in href:
                    full_url = f"https://www.linkedin.com{href.split('?')[0]}"
                    offer_urls.append(full_url)
                    logger.debug(f"URL encontrada: {full_url}")
                    if len(offer_urls) >= max_offers:
                        break

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            scroll_attempts += 1

        logger.info(f"Total URLs recolectadas: {len(offer_urls)}")
        return offer_urls[:max_offers]

    # Método para analizar los detalles de una oferta de trabajo específica.
    # Extrae información como título, empresa, ubicación, descripción, habilidades, fecha de publicación y salario.
    # Normaliza el texto extraído para asegurar consistencia en los datos.
    # Verifica la presencia de datos esenciales antes de guardar la oferta en la base de datos.
    def parse_offer_detail(self, url):
        logger.info(f"Parseando detalle: {url}")
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(5)
            job_id = url.split('/jobs/view/')[1].split('/')[0]
            html_filename = f"job_detail_{job_id}.html"
            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.debug(f"HTML de detalle guardado en '{html_filename}'.")
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            data = {'url': url, 'source': "LinkedIn"}

            # Normalizar texto extraído
            def normalize_text(text):
                if not text:
                    return ""
                return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').strip()

            # Título
            title_tag = soup.select_one('h1.top-card-layout__title') or soup.select_one('.job-details-jobs-unified-top-card__job-title')
            data['title'] = normalize_text(title_tag.get_text(strip=True)[:255]) if title_tag else "Sin título"
            logger.debug(f"Título: {data['title']}")

            # Empresa
            company_tag = soup.select_one('a.topcard__org-name-link') or soup.select_one('.job-details-jobs-unified-top-card__company-name a')
            data['company'] = normalize_text(company_tag.get_text(strip=True)[:255]) if company_tag else "Desconocida"
            logger.debug(f"Empresa: {data['company']}")

            # Ubicación
            location_tag = soup.select_one('.artdeco-entity-lockup__caption div[dir="ltr"]') or soup.select_one('.job-details-jobs-unified-top-card__primary-description')
            data['location'] = normalize_text(location_tag.get_text(strip=True)[:255]) if location_tag else "Ubicación no especificada"
            logger.debug(f"Ubicación: {data['location']}")

            # Descripción
            description_tag = soup.select_one('div.jobs-description__content') or soup.select_one('.jobs-box__html-content')
            description = normalize_text(description_tag.get_text(strip=True)[:2000]) if description_tag else "No especificada"
            logger.debug(f"Descripción: {description[:100]}...")

            # Habilidades
            valid_skills = {
                'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'node.js', 'django', 'flask',
                'spring', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'docker', 'kubernetes', 'aws', 'azure',
                'gcp', 'git', 'ci/cd', 'scrum', 'agile', 'linux', 'bash', 'php', 'ruby', 'go', 'c++', 'c#', '.net',
                'html', 'css', 'sass', 'graphql', 'rest', 'terraform', 'ansible', 'jenkins', 'flutter', 'kotlin', 'swift'
            }
            skills_list = []

            # Intento 1: Extraer habilidades desde la sección de habilidades
            skills_section = soup.select_one('.job-details-skill-match-status__skill div')
            if skills_section:
                skills_text = normalize_text(skills_section.get_text(strip=True))
                skills_list = [skill.strip().lower() for skill in skills_text.split(',') if skill.strip()]
                skills_list = [skill for skill in skills_list if skill in valid_skills]
                logger.debug(f"Habilidades extraídas de la sección: {skills_list}")

            # Intento 2: Extraer habilidades desde el enlace de habilidades
            if not skills_list:
                skills_link = soup.select_one('a[href*="#HYM"][data-test-app-aware-link]')
                if skills_link and "Skills:" in skills_link.get_text():
                    skills_text = normalize_text(skills_link.get_text(strip=True).strip().replace("Skills:", ""))
                    skills_list = [skill.strip().lower() for skill in skills_text.split(',') if skill.strip()]
                    skills_list = [skill for skill in skills_list if skill in valid_skills]
                    logger.debug(f"Habilidades extraídas del enlace: {skills_list}")

            # Intento 3: Extraer habilidades desde la descripción
            if not skills_list and description:
                text = description.lower()
                for skill in valid_skills:
                    if skill == 'go':
                        if re.search(r'\bgo\b|\bgolang\b', text):
                            skills_list.append(skill)
                    elif re.search(rf'\b{re.escape(skill)}\b', text) and skill not in skills_list:
                        skills_list.append(skill)
                logger.debug(f"Habilidades extraídas de la descripción: {skills_list}")

            # Crear o obtener objetos Skill
            skill_objects = []
            for skill_name in set(skills_list):
                if len(skill_name) > 2:
                    skill_obj, created = Skill.objects.get_or_create(name=skill_name.lower())
                    skill_objects.append(skill_obj)
            data['required_skills'] = [skill.name for skill in skill_objects]
            logger.debug(f"Habilidades finales guardadas: {data['required_skills']}")

            # Fecha de publicación
            date_tag = soup.select_one('time') or soup.select_one('span.jobs-unified-top-card__posted-date')
            if date_tag:
                date_text = normalize_text(date_tag.get_text(strip=True).lower())
                logger.debug(f"Texto de fecha crudo: '{date_text}'")
                if "ago" in date_text:
                    match = re.search(r'(\d+)\s*(hour|day|week|month)', date_text)
                    if match:
                        value, unit = match.groups()
                        value = int(value)
                        now = datetime.now().date()
                        if "hour" in unit:
                            data['publication_date'] = now
                        elif "day" in unit:
                            data['publication_date'] = now - timedelta(days=value)
                        elif "week" in unit:
                            data['publication_date'] = now - timedelta(weeks=value)
                        elif "month" in unit:
                            data['publication_date'] = now - timedelta(days=value * 30)
                        else:
                            data['publication_date'] = now
                    else:
                        data['publication_date'] = datetime.now().date()
                else:
                    data['publication_date'] = datetime.now().date()
            else:
                data['publication_date'] = datetime.now().date()
            logger.debug(f"Fecha: {data['publication_date']}")

            # Salario
            salary_tag = soup.select_one('#SALARY .jobs-details__salary-main-rail-card span') or soup.select_one('.jobs-unified-top-card__salary')
            data['salary'] = normalize_text(salary_tag.get_text(strip=True)[:255]) if salary_tag else None
            logger.debug(f"Salario: {data['salary']}")

            # Validar datos requeridos
            if not data.get('title') or not data.get('url') or data['title'] == "Sin título":
                logger.warning(f"Oferta descartada por faltar título o URL válida: {url}")
                return None

            try:
                job_offer, created = JobOffer.objects.get_or_create(
                    url=data['url'],
                    defaults={
                        'title': data['title'],
                        'company': data['company'] or "Desconocida",
                        'location': data['location'],
                        'publication_date': data['publication_date'],
                        'salary': data['salary'],
                        'source': data['source'],
                    }
                )
                if skill_objects:
                    job_offer.skills.set(skill_objects)
                    logger.debug(f"Habilidades asociadas a JobOffer: {[skill.name for skill in skill_objects]}")
                logger.info(f"Guardado en JobOffer: {job_offer.title} {'(nueva)' if created else '(actualizada)'}")
            except Exception as e:
                logger.error(f"Error al guardar en JobOffer: {e}")
                return None

            return data

        except Exception as e:
            logger.error(f"Error al parsear detalle: {e}")
            return None

    # Método principal para ejecutar el proceso de scraping.
    # Inicia sesión, busca ofertas, analiza los detalles y guarda los datos extraídos.
    # Maneja excepciones críticas y asegura el cierre adecuado del navegador.
    def run(self, query="software developer", location="Spain", max_offers=10):
        logger.info(f"Iniciando scraping de LinkedIn: query='{query}', location='{location}', max_offers={max_offers}")
        try:
            username = os.getenv("LINKEDIN_EMAIL", "andreasierra1223@gmail.com")
            password = os.getenv("LINKEDIN_PASSWORD", "Dicampus@2020")

            if not username or not password:
                logger.error("Las credenciales de LinkedIn (LINKEDIN_EMAIL y LINKEDIN_PASSWORD) no están configuradas en .env")
                raise ValueError("Credenciales de LinkedIn no configuradas")

            self.login(username, password)
            offer_urls = self.fetch_offers(query, location, max_offers)
            all_offer_data = []
            for url in offer_urls:
                try:
                    detail_data = self.parse_offer_detail(url)
                    if detail_data:
                        all_offer_data.append(detail_data)
                except Exception as e:
                    logger.error(f"Error al procesar {url}: {e}")
                time.sleep(5)
            logger.info(f"Total ofertas extraídas: {len(all_offer_data)}")
            return all_offer_data
        except Exception as e:
            logger.error(f"Error crítico en la ejecución: {e}")
            return []
        finally:
            try:
                self.driver.quit()
                logger.info("Navegador cerrado correctamente.")
            except Exception as e:
                logger.error(f"Error al cerrar el navegador: {e}")