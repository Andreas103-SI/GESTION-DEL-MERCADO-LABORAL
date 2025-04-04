# projects/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from job_platform.views import role_required
from django.http import HttpResponseForbidden

@role_required('manager')
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = request.user
            project.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form})

def project_list(request):
    projects = Project.objects.all() if request.user.role == 'admin' else Project.objects.filter(manager=request.user)
    return render(request, 'projects/project_list.html', {'projects': projects})

def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Verificar si el usuario tiene acceso al proyecto
    if request.user.role != 'admin' and project.manager != request.user:
        return HttpResponseForbidden("No tienes permiso para acceder a este proyecto.")
    return render(request, 'projects/project_detail.html', {'project': project})


@role_required('manager')
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.manager != request.user and request.user.role != 'admin':
        return HttpResponseForbidden("No tienes permiso para acceder a este proyecto.")
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form})

@role_required('manager')
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Verificar si el usuario es el manager del proyecto
    if project.manager != request.user and request.user.role != 'admin':
        return HttpResponseForbidden("No tienes permiso para eliminar este proyecto.")
    
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project': project})

@role_required('manager')
def task_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            form.save_m2m()  # Para guardar relaciones muchos-a-muchos
            return redirect('project_detail', pk=project.pk)
    else:
        form = TaskForm()
    return render(request, 'projects/task_form.html', {'form': form, 'project': project})

def task_list(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all()
    return render(request, 'projects/task_list.html', {'tasks': tasks, 'project': project})

@role_required('manager')
def task_update(request, project_id, task_id):
    project = get_object_or_404(Project, id=project_id)
    task = get_object_or_404(Task, id=task_id, project=project)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm(instance=task)
    return render(request, 'projects/task_form.html', {'form': form, 'project': project})

@role_required('manager')
def task_delete(request, project_id, task_id):
    project = get_object_or_404(Project, id=project_id)
    task = get_object_or_404(Task, id=task_id, project=project)
    if request.method == 'POST':
        task.delete()
        return redirect('project_detail', project_id=project.id)
    return render(request, 'projects/task_confirm_delete.html', {'task': task, 'project': project})

def task_detail(request, project_id, task_id):
    project = get_object_or_404(Project, id=project_id)
    task = get_object_or_404(Task, id=task_id, project=project)
    return render(request, 'projects/task_detail.html', {'task': task, 'project': project})