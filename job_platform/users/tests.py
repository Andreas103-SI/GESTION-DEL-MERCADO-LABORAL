from django.test import TestCase

# Create your tests here.
# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields import CICharField, CIEmailField

class CustomUser(AbstractUser):
    email = CIEmailField(unique=True)  # Este campo usa CITEXT
    role = models.CharField(max_length=20, default='employee')