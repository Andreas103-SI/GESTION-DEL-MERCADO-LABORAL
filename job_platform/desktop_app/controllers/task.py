"""
Controlador para operaciones del modelo Task.
"""
from .base import BaseController
from job_platform.tasks.models import Task
from datetime import datetime

class TaskController(BaseController):
    """Controlador para operaciones de tareas."""
    
    def __init__(self):
        """Inicializa el controlador."""
        super().__init__()
        self.required_fields = ['title', 'description', 'status', 'priority', 'deadline', 'project']
    
    def create(self, data):
        """Crea una nueva tarea."""
        try:
            if not self.validate_required_fields(data, self.required_fields):
                return False, "Todos los campos son requeridos"
            
            # Convertir fecha límite de cadena a objeto de fecha
            data['deadline'] = datetime.strptime(
                data['deadline'], '%Y-%m-%d'
            ).date()
            
            task = Task.objects.create(**data)
            return True, task
        except Exception as e:
            return False, self.handle_error(e)
    
    def read(self, task_id=None):
        """Lee tarea(s)."""
        try:
            if task_id:
                return True, Task.objects.get(id=task_id)
            return True, Task.objects.all()
        except Task.DoesNotExist:
            return False, "Tarea no encontrada"
        except Exception as e:
            return False, self.handle_error(e)
    
    def update(self, task_id, data):
        """Actualiza una tarea."""
        try:
            task = Task.objects.get(id=task_id)
            
            if 'deadline' in data:
                data['deadline'] = datetime.strptime(
                    data['deadline'], '%Y-%m-%d'
                ).date()
            
            for key, value in data.items():
                setattr(task, key, value)
            
            task.save()
            return True, task
        except Task.DoesNotExist:
            return False, "Tarea no encontrada"
        except Exception as e:
            return False, self.handle_error(e)
    
    def delete(self, task_id):
        """Elimina una tarea."""
        try:
            task = Task.objects.get(id=task_id)
            task.delete()
            return True, "Tarea eliminada exitosamente"
        except Task.DoesNotExist:
            return False, "Tarea no encontrada"
        except Exception as e:
            return False, self.handle_error(e) 