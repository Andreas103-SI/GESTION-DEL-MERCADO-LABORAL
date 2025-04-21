from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from projects.models import Task
from market_analysis.models import Skill

def recommend_tasks(user, max_recommendations=5):
    """
    Recomienda tareas a un usuario basado en la coincidencia de habilidades.
    """
    open_tasks = Task.objects.filter(status__in=['pending', 'in_progress']).prefetch_related('skills_required')

    if not open_tasks.exists():
        return []

    user_skills = set(user.skills.values_list('id', flat=True))
    if not user_skills:
        return []

    all_skills = Skill.objects.all()
    skill_ids = list(all_skills.values_list('id', flat=True))
    skill_id_to_index = {skill_id: idx for idx, skill_id in enumerate(skill_ids)}

    user_vector = np.zeros(len(skill_ids))
    for skill_id in user_skills:
        user_vector[skill_id_to_index[skill_id]] = 1

    task_vectors = []
    tasks_list = []
    for task in open_tasks:
        task_skills = set(task.skills_required.values_list('id', flat=True))
        task_vector = np.zeros(len(skill_ids))
        for skill_id in task_skills:
            task_vector[skill_id_to_index[skill_id]] = 1
        task_vectors.append(task_vector)
        tasks_list.append(task)

    task_vectors = np.array(task_vectors)
    user_vector = user_vector.reshape(1, -1)
    similarities = cosine_similarity(user_vector, task_vectors)[0]

    task_similarities = list(zip(tasks_list, similarities))
    task_similarities.sort(key=lambda x: x[1], reverse=True)

    recommended_tasks = [task for task, sim in task_similarities if sim > 0][:max_recommendations]
    return recommended_tasks