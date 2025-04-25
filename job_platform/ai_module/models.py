from django.db import models

# Create your models here.
# ai_module/models.py
from django.db import models

class AIModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name