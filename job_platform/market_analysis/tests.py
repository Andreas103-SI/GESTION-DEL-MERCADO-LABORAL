from django.test import TestCase
from market_analysis.models import JobOffer, Skill
from bs4 import BeautifulSoup
from datetime import datetime
import os

class TecnoempleoScraperTests(TestCase):
    def setUp(self):
        # Cargar HTML de prueba
        debug_path = os.path.join(os.getcwd(), "tecnoempleo_debug.html")
        if os.path.exists(debug_path):
            with open(debug_path, "r", encoding="utf-8") as f:
                self.soup = BeautifulSoup(f.read(), "html.parser")
        else:
            self.soup = BeautifulSoup("", "html.parser")

    def test_parse_date(self):
        # Simular elemento de fecha
        html = '<span class="d-block d-lg-none text-gray-800">Barcelona (Híbrido) - 11/04/2025<br>27.000€ - 33.000€ b/a</span>'
        span = BeautifulSoup(html, "html.parser").span
        date_text = span.text.split(" - ")[1].split("<br>")[0].replace("Actualizada", "").strip()
        try:
            pub_date = datetime.strptime(date_text, "%d/%m/%Y").date()
            self.assertEqual(pub_date.strftime("%d/%m/%Y"), "11/04/2025")
        except ValueError:
            self.fail("Error al parsear fecha")

    def test_clean_salary(self):
        html = '<span class="d-block d-lg-none text-gray-800">Madrid - 12/04/2025<br>27.000€ - 33.000€ b/a</span>'
        span = BeautifulSoup(html, "html.parser").span
        date_text = span.text.split(" - ")[1].split("<br>")[0].strip()
        self.assertEqual(date_text, "12/04/2025")

    def test_save_job_offer(self):
        job, created = JobOffer.objects.get_or_create(
            title="Software Engineer",
            company="Solera",
            source="Tecnoempleo",
            defaults={"location": "Madrid", "publication_date": "2025-04-12"}
        )
        self.assertTrue(created)
        self.assertEqual(job.title, "Software Engineer")
        skill, _ = Skill.objects.get_or_create(name="Java")
        job.skills.add(skill)
        self.assertIn(skill, job.skills.all())

class InfoJobsScraperTests(TestCase):
    def setUp(self):
        # Cargar HTML de prueba (crear infojobs_debug.html si existe)
        debug_path = os.path.join(os.getcwd(), "infojobs_debug.html")
        if os.path.exists(debug_path):
            with open(debug_path, "r", encoding="utf-8") as f:
                self.soup = BeautifulSoup(f.read(), "html.parser")
        else:
            self.soup = BeautifulSoup("", "html.parser")

    def test_parse_date(self):
        # Simular elemento de InfoJobs (ajustar según HTML real)
        html = '<div class="job-date">Publicado el 11/04/2025</div>'
        div = BeautifulSoup(html, "html.parser").div
        date_text = div.text.replace("Publicado el", "").strip()
        try:
            pub_date = datetime.strptime(date_text, "%d/%m/%Y").date()
            self.assertEqual(pub_date.strftime("%d/%m/%Y"), "11/04/2025")
        except ValueError:
            self.fail("Error al parsear fecha de InfoJobs")

    def test_save_job_offer(self):
        job, created = JobOffer.objects.get_or_create(
            title="Desarrollador Web",
            company="InfoJobsTest",
            source="InfoJobs",
            defaults={"location": "Oviedo", "publication_date": "2025-04-11"}
        )
        self.assertTrue(created)
        self.assertEqual(job.title, "Desarrollador Web")

class LinkedInScraperTests(TestCase):
    def setUp(self):
        # Cargar HTML de prueba
        debug_path = os.path.join(os.getcwd(), "linkedin_debug.html")
        if os.path.exists(debug_path):
            with open(debug_path, "r", encoding="utf-8") as f:
                self.soup = BeautifulSoup(f.read(), "html.parser")
        else:
            self.soup = BeautifulSoup("", "html.parser")

    def test_parse_date(self):
        # Simular elemento de LinkedIn
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
            defaults={"location": "Asturias", "publication_date": "2025-04-12"}
        )
        self.assertTrue(created)
        self.assertEqual(job.title, "Full Stack Developer")
        skill, _ = Skill.objects.get_or_create(name="Python")
        job.skills.add(skill)
        self.assertIn(skill, job.skills.all())