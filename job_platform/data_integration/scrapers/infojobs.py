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
from dotenv import load_dotenv




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