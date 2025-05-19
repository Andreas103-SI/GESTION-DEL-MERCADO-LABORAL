# Este módulo contiene pruebas para los scrapers de Tecnoempleo y LinkedIn.
# Verifica la correcta extracción y procesamiento de datos como fechas, salarios y ofertas de trabajo.

from django.test import TestCase
from market_analysis.models import JobOffer, Skill
from bs4 import BeautifulSoup
from datetime import date, datetime
import os
import re

class TecnoempleoScraperTests(TestCase):
    def setUp(self):
        debug_path = os.path.join(os.getcwd(), "tecnoempleo_debug.html")
        if os.path.exists(debug_path):
            with open(debug_path, "r", encoding="utf-8") as f:
                self.soup = BeautifulSoup(f.read(), "html.parser")
        else:
            self.soup = BeautifulSoup("", "html.parser")

    def test_parse_date(self):
        # Usamos un HTML simulado con formato consistente
        html = '<span class="d-block d-lg-none text-gray-800">Barcelona (Híbrido) - 11/04/2025<br>27.000€ - 33.000€ b/a</span>'
        span = BeautifulSoup(html, "html.parser").find("span", class_="d-block d-lg-none text-gray-800")
        if span:
            # Extraemos el texto y dividimos por " - " para obtener la fecha
            parts = span.text.split(" - ")
            if len(parts) > 1:
                date_part = parts[1].split("<br>")[0].strip()
                # Usamos una expresión regular para extraer solo la fecha (formato dd/mm/yyyy)
                match = re.match(r"(\d{2}/\d{2}/\d{4})", date_part)
                if match:
                    date_str = match.group(1)
                    try:
                        pub_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                        self.assertEqual(pub_date.strftime("%d/%m/%Y"), "11/04/2025")
                    except ValueError:
                        self.fail("Error al parsear fecha")
                else:
                    self.fail("Formato de fecha no encontrado")
            else:
                self.fail("Formato de fecha inesperado")
        else:
            self.fail("Elemento span no encontrado")

    def test_save_job_offer(self):
        job, created = JobOffer.objects.get_or_create(
            title="Software Engineer",
            company="Solera",
            source="Tecnoempleo",
            defaults={"location": "Madrid", "publication_date": date(2025, 4, 12)}
        )
        self.assertTrue(created)
        self.assertEqual(job.title, "Software Engineer")
        skill, _ = Skill.objects.get_or_create(name="Java")
        job.skills.add(skill)
        self.assertIn(skill, job.skills.all())

class LinkedInScraperTests(TestCase):
    def setUp(self):
        debug_path = os.path.join(os.getcwd(), "linkedin_debug.html")
        if os.path.exists(debug_path):
            with open(debug_path, "r", encoding="utf-8") as f:
                self.soup = BeautifulSoup(f.read(), "html.parser")
        else:
            self.soup = BeautifulSoup("", "html.parser")

    def test_parse_date(self):
        html = '<time datetime="2025-04-12">12 abril 2025</time>'
        time_elem = BeautifulSoup(html, "html.parser").time
        try:
            pub_date = datetime.strptime(time_elem["datetime"], "%Y-%m-%d").date()
            self.assertEqual(pub_date.strftime("%d/%m/%Y"), "12/04/2025")
        except (ValueError, KeyError):
            self.fail("Error al parsear fecha de LinkedIn")

    def test_save_job_offer(self):
        job, created = JobOffer.objects.get_or_create(
            title="Full Stack Developer",
            company="TechCorp",
            source="LinkedIn",
            defaults={"location": "Asturias", "publication_date": date(2025, 4, 12)}
        )
        self.assertTrue(created)
        self.assertEqual(job.title, "Full Stack Developer")
        skill, _ = Skill.objects.get_or_create(name="Python")
        job.skills.add(skill)
        self.assertIn(skill, job.skills.all())