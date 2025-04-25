# projects/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from job_platform.views import role_required
from django.http import HttpResponseForbidden

# Vista para crear un nuevo proyecto.
# Solo accesible para usuarios con rol de 'manager'.
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

# Vista para listar todos los proyectos.
# Muestra proyectos según el rol del usuario.
def project_list(request):
    projects = Project.objects.all() if request.user.role == 'admin' else Project.objects.filter(manager=request.user)
    return render(request, 'projects/project_list.html', {'projects': projects})

# Vista para mostrar los detalles de un proyecto específico.
# Verifica el acceso del usuario al proyecto.
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Verificar si el usuario tiene acceso al proyecto
    if request.user.role != 'admin' and project.manager != request.user:
        return HttpResponseForbidden("No tienes permiso para acceder a este proyecto.")
    return render(request, 'projects/project_detail.html', {'project': project})

# Vista para actualizar un proyecto existente.
# Solo accesible para el manager del proyecto o un administrador.
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

# Vista para eliminar un proyecto.
# Solo accesible para el manager del proyecto o un administrador.
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

# Vista para crear una nueva tarea dentro de un proyecto.
# Solo accesible para usuarios con rol de 'manager'.
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

# Vista para listar todas las tareas de un proyecto.
# Muestra las tareas asociadas a un proyecto específico.
def task_list(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all()
    return render(request, 'projects/task_list.html', {'tasks': tasks, 'project': project})

# Vista para actualizar una tarea existente.
# Solo accesible para el manager del proyecto.
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

# Vista para eliminar una tarea.
# Solo accesible para el manager del proyecto.
@role_required('manager')
def task_delete(request, project_id, task_id):
    project = get_object_or_404(Project, id=project_id)
    task = get_object_or_404(Task, id=task_id, project=project)
    if request.method == 'POST':
        task.delete()
        return redirect('project_detail', project_id=project.id)
    return render(request, 'projects/task_confirm_delete.html', {'task': task, 'project': project})

# Vista para mostrar los detalles de una tarea específica.
# Muestra la información detallada de una tarea dentro de un proyecto.
def task_detail(request, project_id, task_id):
    project = get_object_or_404(Project, id=project_id)
    task = get_object_or_404(Task, id=task_id, project=project)
    return render(request, 'projects/task_detail.html', {'task': task, 'project': project})