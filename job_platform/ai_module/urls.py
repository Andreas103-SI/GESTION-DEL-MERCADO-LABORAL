from django.urls import path
from . import views

app_name = 'ai_module'

urlpatterns = [
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
] 