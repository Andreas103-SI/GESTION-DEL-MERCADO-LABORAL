# user/modelspy
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('manager', 'Gestor de Proyectos'),
        ('collaborator', 'Colaborador'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='collaborator')