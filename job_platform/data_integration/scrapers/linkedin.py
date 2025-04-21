from django.contrib import messages
from django.shortcuts import render
from rolepermissions.decorators import has_role_decorator
from market_analysis.models import JobOffer, Skill
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import os
import time
import re

@has_role_decorator('admin')
def scrape_linkedin(request):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--lang=en-US")  # Forzar idioma inglés

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        # Iniciar sesión en LinkedIn
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        
        email = os.getenv("LINKEDIN_EMAIL", "andreasierra1223@gmail.com")
        password = os.getenv("LINKEDIN_PASSWORD", "Dicampus@2020")
        
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # Verificar si la autenticación fue exitosa
        try:
            WebDriverWait(driver, 15).until(EC.url_contains("feed"))
        except:
            # Guardar HTML para depuración en caso de fallo de autenticación
            debug_path = os.path.join(os.getcwd(), "linkedin_debug.html")
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            messages.error(request, "Error de autenticación en LinkedIn. Verifica las credenciales o si hay verificación adicional (CAPTCHA).")
            return render(request, 'data_integration/scrape_results.html', {'offers': []})

        # Ir a la página de búsqueda de empleos
        url = "https://www.linkedin.com/jobs/search/?keywords=software%20developer&location=Spain"
        driver.get(url)
        time.sleep(5)

        # Desplazar la página para cargar más ofertas
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        debug_path = os.path.join(os.getcwd(), "linkedin_debug.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print("HTML devuelto por LinkedIn:", driver.page_source[:1000])

        offers = []
        one_month_ago = datetime.now().date() - timedelta(days=30)

        job_cards = soup.select('li.jobs-search-results__list-item')
        for card in job_cards:
            title_elem = card.select_one('a.job-card-list__title')
            company_elem = card.select_one('a.job-card-container__company-name')
            location_elem = card.select_one('li.job-card-container__metadata-item')
            date_elem = card.select_one('time')
            skills_elem = card.select_one('a.LXelMjlWJejSAuCMUMmhrhaUQtEhAGwXKZOmrw')

            if title_elem and company_elem and location_elem:
                title = title_elem.text.strip()[:255]
                company = company_elem.text.strip()[:255]
                location = location_elem.text.strip()[:255]
                date_text = date_elem['datetime'] if date_elem and 'datetime' in date_elem.attrs else None

                pub_date = one_month_ago
                if date_text:
                    try:
                        pub_date = datetime.strptime(date_text, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        days_ago_match = re.search(r'(\d+) day', date_text)
                        if days_ago_match:
                            days_ago = int(days_ago_match.group(1))
                            pub_date = datetime.now().date() - timedelta(days=days_ago)

                if pub_date < one_month_ago:
                    continue

                job, created = JobOffer.objects.get_or_create(
                    title=title,
                    company=company,
                    source="LinkedIn",
                    defaults={
                        'location': location,
                        'publication_date': pub_date,
                        'salary': None,
                        'url': title_elem['href'] if 'href' in title_elem.attrs else None
                    }
                )
                if created:
                    if skills_elem:
                        skills_text = skills_elem.text.strip().replace("Skills: ", "")
                        skill_names = [skill.strip() for skill in skills_text.split(",")]
                        for skill_name in skill_names:
                            if skill_name and "more" not in skill_name:
                                skill, _ = Skill.objects.get_or_create(name=skill_name)
                                job.skills.add(skill)
                    offers.append(job)

        messages.success(request, f"Se han extraído {len(offers)} ofertas de LinkedIn.")
        context = {
            'offers': offers,
            'num_offers': len(offers)
        }
        return render(request, 'data_integration/scrape_results.html', context)

    except Exception as e:
        messages.error(request, f"Error al scrapear LinkedIn: {e}")
        return render(request, 'data_integration/scrape_results.html', {'offers': []})

    finally:
        driver.quit()