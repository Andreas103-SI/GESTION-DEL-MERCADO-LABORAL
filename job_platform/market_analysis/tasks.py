# market_analysis/tests.py
from django.test import TestCase
from .models import JobOffer, Skill, MarketData
from datetime import date
from unittest.mock import patch, MagicMock
from .tasks import run_linkedin_scraper, scrape_tecnoempleo

# Pruebas para los modelos (ya definidas anteriormente)
class JobOfferModelTests(TestCase):
    def setUp(self):
        self.skill = Skill.objects.create(name="Python")
        self.job_offer = JobOffer.objects.create(
            title="Desarrollador Python",
            company="TechCorp",
            location="Madrid",
            source="Tecnoempleo",
            publication_date=date.today(),
            salary="30000-40000 EUR",
            url="https://example.com/job/123"
        )
        self.job_offer.skills.add(self.skill)

    def test_job_offer_creation(self):
        """Prueba la creación de una oferta de empleo."""
        self.assertEqual(self.job_offer.title, "Desarrollador Python")
        self.assertEqual(self.job_offer.company, "TechCorp")
        self.assertEqual(self.job_offer.location, "Madrid")
        self.assertIn(self.skill, self.job_offer.skills.all())

    def test_unique_together_constraint(self):
        """Prueba que no se puedan crear dos ofertas con el mismo título, empresa y fuente."""
        with self.assertRaises(Exception):
            JobOffer.objects.create(
                title="Desarrollador Python",
                company="TechCorp",
                location="Barcelona",
                source="Tecnoempleo",
                publication_date=date.today(),
                salary="35000-45000 EUR",
                url="https://example.com/job/456"
            )

class SkillModelTests(TestCase):
    def setUp(self):
        self.skill = Skill.objects.create(name="Java")

    def test_skill_creation(self):
        """Prueba la creación de una habilidad."""
        self.assertEqual(self.skill.name, "Java")

class MarketDataModelTests(TestCase):
    def setUp(self):
        self.skill = Skill.objects.create(name="Python")
        self.market_data = MarketData.objects.create(
            date=date.today(),
            skill=self.skill,
            demand_count=10,
            source="LinkedIn"
        )

    def test_market_data_creation(self):
        """Prueba la creación de datos de mercado."""
        self.assertEqual(self.market_data.demand_count, 10)
        self.assertEqual(self.market_data.source, "LinkedIn")
        self.assertEqual(self.market_data.skill, self.skill)

# Pruebas para los scrapers
class ScraperTests(TestCase):
    @patch('market_analysis.tasks.webdriver.Chrome')
    def test_run_linkedin_scraper_success(self, mock_chrome):
        """Prueba el scraper de LinkedIn con datos simulados."""
        # Configurar el mock para simular el comportamiento de Selenium
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Simular las ofertas de empleo (job cards)
        mock_job_card = MagicMock()
        mock_job_card.text = "Desarrollador Python"
        mock_job_card.find_element.side_effect = [
            MagicMock(text="TechCorp"),  # company
            MagicMock(text="Madrid"),    # location
        ]
        mock_job_card.get_attribute.return_value = "https://example.com/job/123"
        mock_job_card.find_elements.return_value = [MagicMock(text="Python"), MagicMock(text="Django")]

        mock_driver.find_elements.return_value = [mock_job_card]

        # Ejecutar el scraper
        result = run_linkedin_scraper()

        # Verificar el resultado
        self.assertEqual(result, "Ofertas de LinkedIn extraídas y guardadas correctamente")
        self.assertTrue(JobOffer.objects.filter(title="Desarrollador Python", source="LinkedIn").exists())
        job_offer = JobOffer.objects.get(title="Desarrollador Python", source="LinkedIn")
        self.assertEqual(job_offer.company, "TechCorp")
        self.assertEqual(job_offer.location, "Madrid")
        self.assertEqual(job_offer.url, "https://example.com/job/123")
        self.assertTrue(job_offer.skills.filter(name="python").exists())
        self.assertTrue(job_offer.skills.filter(name="django").exists())

    @patch('market_analysis.tasks.webdriver.Chrome')
    def test_run_linkedin_scraper_no_new_offers(self, mock_chrome):
        """Prueba el scraper de LinkedIn cuando no hay nuevas ofertas (ya existen en la base de datos)."""
        # Crear una oferta existente
        JobOffer.objects.create(
            title="Desarrollador Python",
            company="TechCorp",
            location="Madrid",
            source="LinkedIn",
            publication_date=date.today(),
            url="https://example.com/job/123"
        )

        # Configurar el mock
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        mock_job_card = MagicMock()
        mock_job_card.text = "Desarrollador Python"
        mock_job_card.find_element.side_effect = [
            MagicMock(text="TechCorp"),
            MagicMock(text="Madrid"),
        ]
        mock_job_card.get_attribute.return_value = "https://example.com/job/123"
        mock_job_card.find_elements.return_value = []

        mock_driver.find_elements.return_value = [mock_job_card]

        # Ejecutar el scraper
        result = run_linkedin_scraper()

        # Verificar el resultado
        self.assertEqual(result, "Ofertas de LinkedIn extraídas y guardadas correctamente")
        self.assertEqual(JobOffer.objects.count(), 1)  # No se creó una nueva oferta

    @patch('market_analysis.tasks.webdriver.Chrome')
    def test_scrape_tecnoempleo_success(self, mock_chrome):
        """Prueba el scraper de Tecnoempleo con datos simulados."""
        # Configurar el mock
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        mock_job_card = MagicMock()
        mock_job_card.text = "Analista de Datos"
        mock_job_card.find_element.side_effect = [
            MagicMock(text="DataCorp"),  # company
            MagicMock(text="Barcelona"), # location
        ]
        mock_job_card.get_attribute.return_value = "https://example.com/job/456"
        mock_job_card.find_elements.return_value = [MagicMock(text="SQL"), MagicMock(text="Python")]

        mock_driver.find_elements.return_value = [mock_job_card]

        # Ejecutar el scraper
        result = scrape_tecnoempleo()

        # Verificar el resultado
        self.assertEqual(result, "Ofertas de Tecnoempleo extraídas y guardadas correctamente")
        self.assertTrue(JobOffer.objects.filter(title="Analista de Datos", source="Tecnoempleo").exists())
        job_offer = JobOffer.objects.get(title="Analista de Datos", source="Tecnoempleo")
        self.assertEqual(job_offer.company, "DataCorp")
        self.assertEqual(job_offer.location, "Barcelona")
        self.assertEqual(job_offer.url, "https://example.com/job/456")
        self.assertTrue(job_offer.skills.filter(name="sql").exists())
        self.assertTrue(job_offer.skills.filter(name="python").exists())

    @patch('market_analysis.tasks.webdriver.Chrome')
    def test_scrape_tecnoempleo_error_handling(self, mock_chrome):
        """Prueba el manejo de errores en el scraper de Tecnoempleo."""
        # Configurar el mock para lanzar una excepción
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.get.side_effect = Exception("Error de conexión")

        # Ejecutar el scraper
        result = scrape_tecnoempleo()

        # Verificar el resultado
        self.assertTrue(result.startswith("Error al extraer ofertas de Tecnoempleo:"))
        self.assertEqual(JobOffer.objects.count(), 0)  # No se creó ninguna oferta