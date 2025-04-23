"""
Controlador para operaciones del modelo JobOffer.
"""
from .base import BaseController
from job_platform.job_offers.models import JobOffer
from datetime import datetime

class JobOfferController(BaseController):
    """Controlador para operaciones de ofertas de trabajo."""
    
    def __init__(self):
        """Inicializa el controlador."""
        super().__init__()
        self.required_fields = ['title', 'company', 'location', 'publication_date']
    
    def create(self, data):
        """Crea una nueva oferta de trabajo."""
        try:
            if not self.validate_required_fields(data, self.required_fields):
                return False, "Todos los campos son requeridos"
            
            # Convertir fecha de publicación de cadena a objeto de fecha
            data['publication_date'] = datetime.strptime(
                data['publication_date'], '%Y-%m-%d'
            ).date()
            
            job_offer = JobOffer.objects.create(**data)
            return True, job_offer
        except Exception as e:
            return False, self.handle_error(e)
    
    def read(self, job_offer_id=None):
        """Lee oferta(s) de trabajo."""
        try:
            if job_offer_id:
                return True, JobOffer.objects.get(id=job_offer_id)
            return True, JobOffer.objects.all()
        except JobOffer.DoesNotExist:
            return False, "Oferta de trabajo no encontrada"
        except Exception as e:
            return False, self.handle_error(e)
    
    def update(self, job_offer_id, data):
        """Actualiza una oferta de trabajo."""
        try:
            job_offer = JobOffer.objects.get(id=job_offer_id)
            
            if 'publication_date' in data:
                data['publication_date'] = datetime.strptime(
                    data['publication_date'], '%Y-%m-%d'
                ).date()
            
            for key, value in data.items():
                setattr(job_offer, key, value)
            
            job_offer.save()
            return True, job_offer
        except JobOffer.DoesNotExist:
            return False, "Oferta de trabajo no encontrada"
        except Exception as e:
            return False, self.handle_error(e)
    
    def delete(self, job_offer_id):
        """Elimina una oferta de trabajo."""
        try:
            job_offer = JobOffer.objects.get(id=job_offer_id)
            job_offer.delete()
            return True, "Oferta de trabajo eliminada exitosamente"
        except JobOffer.DoesNotExist:
            return False, "Oferta de trabajo no encontrada"
        except Exception as e:
            return False, self.handle_error(e) 