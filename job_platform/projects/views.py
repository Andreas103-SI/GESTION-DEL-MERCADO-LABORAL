# projects/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Project
from .forms import ProjectForm
from job_platform.views import role_required

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