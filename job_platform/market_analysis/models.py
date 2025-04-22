# market_analysis/models.py
from django.db import models
from django.contrib.postgres.fields import CICharField  # For PostgreSQL case-insensitive field

class Skill(models.Model):
    name = CICharField(max_length=100, unique=True)  # Changed to CICharField for case-insensitive uniqueness
    def __str__(self): return self.name

class JobOffer(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=50)
    publication_date = models.DateField()
    salary = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(max_length=500, unique=True, blank=True, null=True)
    skills = models.ManyToManyField(Skill, related_name='job_offers')

    class Meta:
        unique_together = ('title', 'company', 'source')

    def __str__(self):
        return f"{self.title} - {self.company} ({self.source})"

class MarketData(models.Model):
    date = models.DateField()
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    demand_count = models.PositiveIntegerField()
    source = models.CharField(max_length=50)

    class Meta:
        unique_together = ('date', 'skill', 'source')

    def __str__(self):
        return f"{self.skill.name} - {self.demand_count} ({self.source}, {self.date})"