from django.urls import path
from .views import project_create, project_list

urlpatterns = [
    path('projects/', project_list, name='project_list'),
    path('projects/create/', project_create, name='project_create'),
]