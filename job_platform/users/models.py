# user/modelspy
from django.db import models
from django.contrib.auth.models import AbstractUser
from market_analysis.models import Skill

class CustomUser(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('manager', 'Gestor de Proyectos'),
        ('collaborator', 'Colaborador'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='collaborator')
    skills = models.ManyToManyField('market_analysis.Skill', related_name='users', blank=True)

    def __str__(self):
        return self.username
    
    