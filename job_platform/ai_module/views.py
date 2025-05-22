from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from projects.models import Task
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# Create your views here.

@login_required
@require_POST
def complete_task(request, task_id):
    """
    Marca una tarea como completada y actualiza su estado.
    
    Args:
        request: HttpRequest object
        task_id: ID de la tarea a completar
    
    Returns:
        HttpResponse: Redirección a la página del dashboard o respuesta JSON
    """
    try:
        # Obtener la tarea y verificar permisos
        task = get_object_or_404(Task, id=task_id)
        
        # Verificar si el usuario es colaborador o manager del proyecto
        if request.user not in task.collaborators.all() and request.user != task.project.manager:
            messages.error(request, 'No tienes permisos para completar esta tarea.')
            return redirect('market_analysis:dashboard')
        
        # Verificar si la tarea ya está completada
        if task.state == 'completed':
            messages.warning(request, 'Esta tarea ya estaba marcada como completada.')
            return redirect('market_analysis:dashboard')
        
        # Actualizar la tarea
        task.state = 'completed'
        task.save()
        
        # Mensaje de éxito
        messages.success(request, '¡Tarea completada con éxito!')
        
        # Si es una petición AJAX, devolver respuesta JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Tarea completada con éxito',
                'task_id': task.id
            })
            
    except Task.DoesNotExist:
        messages.error(request, 'La tarea no existe.')
    except Exception as e:
        messages.error(request, f'Error al completar la tarea: {str(e)}')
        # Log del error para debugging
        print(f"Error completing task {task_id}: {str(e)}")
    
    return redirect('market_analysis:dashboard')
