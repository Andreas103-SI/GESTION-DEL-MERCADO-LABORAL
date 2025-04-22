# market_analysis/tasks.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import date
from .models import JobOffer, Skill

def run_linkedin_scraper():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        print("Extrayendo ofertas de LinkedIn...")
        driver.get("https://www.linkedin.com/jobs/search/")
        time.sleep(3)

        job_cards = driver.find_elements(By.CLASS_NAME, "job-card-list__title")
        for card in job_cards[:10]:
            title = card.text
            company = card.find_element(By.XPATH, "..//span[@class='job-card-container__company-name']").text
            location = card.find_element(By.XPATH, "..//span[@class='job-card-container__metadata-item']").text
            url = card.get_attribute("href")

            skill_elements = card.find_elements(By.XPATH, "..//span[@class='job-card-container__skill']")
            skill_names = [elem.text.lower() for elem in skill_elements]

            if not JobOffer.objects.filter(url=url, source="LinkedIn").exists():
                job_offer = JobOffer.objects.create(
                    title=title,
                    company=company,
                    location=location,
                    source="LinkedIn",
                    publication_date=date.today(),
                    url=url
                )
                for skill_name in skill_names:
                    skill, created = Skill.objects.get_or_create(name=skill_name)
                    job_offer.skills.add(skill)

        return "Ofertas de LinkedIn extraídas y guardadas correctamente"
    except Exception as e:
        print(f"Error al extraer ofertas de LinkedIn: {e}")
        return f"Error al extraer ofertas de LinkedIn: {e}"
    finally:
        driver.quit()

def scrape_tecnoempleo():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        print("Extrayendo ofertas de Tecnoempleo...")
        driver.get("https://www.tecnoempleo.com/ofertas-trabajo/")
        time.sleep(3)

        job_cards = driver.find_elements(By.CLASS_NAME, "title")
        for card in job_cards[:10]:
            title = card.text
            company = card.find_element(By.XPATH, "..//div[@class='company']").text
            location = card.find_element(By.XPATH, "..//div[@class='location']").text
            url = card.get_attribute("href")

            skill_elements = card.find_elements(By.XPATH, "..//span[@class='skill']")
            skill_names = [elem.text.lower() for elem in skill_elements]

            if not JobOffer.objects.filter(url=url, source="Tecnoempleo").exists():
                job_offer = JobOffer.objects.create(
                    title=title,
                    company=company,
                    location=location,
                    source="Tecnoempleo",
                    publication_date=date.today(),
                    url=url
                )
                for skill_name in skill_names:
                    skill, created = Skill.objects.get_or_create(name=skill_name)
                    job_offer.skills.add(skill)

        return "Ofertas de Tecnoempleo extraídas y guardadas correctamente"
    except Exception as e:
        print(f"Error al extraer ofertas de Tecnoempleo: {e}")
        return f"Error al extraer ofertas de Tecnoempleo: {e}"
    finally:
        driver.quit()