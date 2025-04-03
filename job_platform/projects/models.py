#projects/modesls.py
from django.db import models
from django.conf import settings

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_projects')

    def __str__(self):
        return self.name

class Task(models.Model):
    STATES = (
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
    )
    PRIORITIES = (
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    state = models.CharField(max_length=20, choices=STATES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITIES, default='medium')
    deadline = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='tasks')
    skills = models.ManyToManyField('Skill', blank=True)

    def __str__(self):
        return self.title

class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
# Create your models here.
