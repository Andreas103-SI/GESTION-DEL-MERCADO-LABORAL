# ai_module/recommendations.py
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from projects.models import Task, Project
from market_analysis.models import Skill
from django.utils import timezone
from django.contrib.auth import get_user_model
import os

User = get_user_model()

def recommend_tasks(user, max_recommendations=5):
    """
    Recomienda tareas a un usuario basado en la coincidencia de habilidades.
    """
    # Obtener o crear usuario predeterminado
    try:
        default_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not default_user:
            # Crear usuario predeterminado
            default_user = User.objects.create_user(
                username='default_manager',
                password=os.getenv('AI_MODULE_PASSWORD'),
                email=os.getenv('AI_MODULE_EMAIL'),
                is_active=True
            )
            print("Creado usuario predeterminado: default_manager")
    except Exception as e:
        print(f"Error obteniendo/creando usuario predeterminado: {e}")
        return []

    # Usar usuario autenticado o predeterminado
    project_manager = user if user.is_authenticated else default_user

    try:
        # Crear proyecto de prueba si no existe
        project, _ = Project.objects.get_or_create(
            name='Proyecto de Prueba',
            defaults={
                'description': 'Proyecto para tareas de prueba',
                'start_date': timezone.now().date(),
                'manager': project_manager
            }
        )
        tasks = Task.objects.filter(state__in=['pending', 'in_progress'])[:max_recommendations]
        if not tasks.exists():
            # Crear tareas de prueba
            python = Skill.objects.get_or_create(name='Python')[0]
            java = Skill.objects.get_or_create(name='Java')[0]
            task1 = Task.objects.create(
                title='Aprender Python Básico',
                description='Curso introductorio de Python',
                priority='high',
                state='pending',
                deadline=timezone.now().date() + timezone.timedelta(days=30),
                project=project
            )
            task1.skills.add(python)
            task2 = Task.objects.create(
                title='Desarrollar API en Java',
                description='Crear una API REST con Java',
                priority='medium',
                state='pending',
                deadline=timezone.now().date() + timezone.timedelta(days=30),
                project=project
            )
            task2.skills.add(java)
            tasks = Task.objects.filter(id__in=[task1.id, task2.id])
        task_list = list(tasks)
    except Exception as e:
        print(f"Error creating test tasks: {e}")
        return []

    # Si el usuario no tiene habilidades, devolver tareas populares
    user_skills = set(user.skills.values_list('id', flat=True)) if user.is_authenticated and hasattr(user, 'skills') else set()
    if not user_skills:
        return task_list[:max_recommendations]

    # Crea un índice de todas las habilidades
    all_skills = Skill.objects.all()
    skill_ids = list(all_skills.values_list('id', flat=True))
    skill_id_to_index = {skill_id: idx for idx, skill_id in enumerate(skill_ids)}

    # Crea el vector del usuario
    user_vector = np.zeros(len(skill_ids))
    for skill_id in user_skills:
        user_vector[skill_id_to_index[skill_id]] = 1

    # Crea vectores para las tareas
    task_vectors = []
    tasks_list = []
    for task in task_list:
        task_skills = set(task.skills.values_list('id', flat=True))
        task_vector = np.zeros(len(skill_ids))
        for skill_id in task_skills:
            task_vector[skill_id_to_index[skill_id]] = 1
        task_vectors.append(task_vector)
        tasks_list.append(task)

    # Calcula la similitud coseno
    task_vectors = np.array(task_vectors)
    user_vector = user_vector.reshape(1, -1)
    similarities = cosine_similarity(user_vector, task_vectors)[0]

    # Ajusta la similitud según la prioridad
    priority_weights = {'low': 1.0, 'medium': 1.2, 'high': 1.5}
    task_similarities = []
    for task, sim in zip(tasks_list, similarities):
        weight = priority_weights.get(task.priority, 1.0)
        adjusted_sim = sim * weight
        task_similarities.append((task, adjusted_sim))

    # Ordena y selecciona las mejores
    task_similarities.sort(key=lambda x: x[1], reverse=True)
    recommended_tasks = [task for task, sim in task_similarities if sim > 0][:max_recommendations]
    return recommended_tasks if recommended_tasks else task_list[:max_recommendations]