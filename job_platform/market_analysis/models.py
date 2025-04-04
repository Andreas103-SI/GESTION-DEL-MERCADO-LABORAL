#market_analysis/models.py
from django.db import models
from projects.models import Skill  # Reusamos Skill de projects

class JobOffer(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    salary = models.CharField(max_length=50, blank=True, null=True)
    publication_date = models.DateField()
    source = models.CharField(max_length=50)  # Ej: "Tecnoempleo", "InfoJobs"
    skills = models.ManyToManyField(Skill, blank=True)

    def __str__(self):
        return f"{self.title} - {self.company}"

class MarketData(models.Model):
    trend = models.CharField(max_length=100)  # Ej: "Habilidad más demandada: Django"
    date = models.DateField()
    region = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.trend