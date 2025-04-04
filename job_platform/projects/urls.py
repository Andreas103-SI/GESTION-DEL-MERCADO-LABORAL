from django.urls import path
from .views import (
    project_create, project_list, project_detail,
    task_create, task_list, task_detail, task_update, task_delete
)

urlpatterns = [
    path('projects/', project_list, name='project_list'),
    path('projects/create/', project_create, name='project_create'),
    path('projects/<int:project_id>/', project_detail, name='project_detail'),
    path('projects/<int:project_id>/tasks/', task_list, name='task_list'),
    path('projects/<int:project_id>/tasks/create/', task_create, name='task_create'),
    path('projects/<int:project_id>/tasks/<int:task_id>/', task_detail, name='task_detail'),
    path('projects/<int:project_id>/tasks/<int:task_id>/update/', task_update, name='task_update'),
    path('projects/<int:project_id>/tasks/<int:task_id>/delete/', task_delete, name='task_delete'),
    
]