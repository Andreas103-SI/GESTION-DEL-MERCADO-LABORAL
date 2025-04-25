# Este módulo define los modelos de datos para el análisis del mercado laboral.
# Incluye modelos para habilidades, ofertas de trabajo y datos de mercado.

# Modelo que representa una habilidad específica.
# Almacena el nombre de la habilidad de manera única y sensible a mayúsculas/minúsculas.
from job_platform.ai_module import models


class Skill(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        db_collation='fr-CI-x-icu'
    )
    def __str__(self): return self.name

# Modelo que representa una oferta de trabajo.
# Almacena detalles como título, empresa, ubicación, fuente, fecha de publicación, salario y URL.
# Relaciona las ofertas con las habilidades requeridas.
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

# Modelo que representa datos de mercado para una habilidad en una fecha específica.
# Almacena la cantidad de demanda de la habilidad y la fuente de los datos.
class MarketData(models.Model):
    date = models.DateField()
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    demand_count = models.PositiveIntegerField()
    source = models.CharField(max_length=50)

    class Meta:
        unique_together = ('date', 'skill', 'source')

    def __str__(self):
        return f"{self.skill.name} - {self.demand_count} ({self.source}, {self.date})"