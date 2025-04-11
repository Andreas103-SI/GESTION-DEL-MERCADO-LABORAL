from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class JobOffer(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=50)
    publication_date = models.DateField()
    salary = models.CharField(max_length=100, blank=True, null=True)  # Nuevo
    skills = models.ManyToManyField(Skill, blank=True)

    class Meta:
        unique_together = ('title', 'company', 'source')  # Evita duplicados

    def __str__(self):
        return f"{self.title} - {self.company} ({self.source})"