#market_analysis/views
from django.shortcuts import render
from .models import JobOffer
from job_platform.views import role_required
from django.db.models import Count

@role_required('admin')
def market_dashboard(request):
    skills_demand = (JobOffer.objects.values('skills__name')
                     .annotate(count=Count('skills__name'))
                     .order_by('-count')[:5])
    sources_count = (JobOffer.objects.values('source')
                     .annotate(count=Count('source'))
                     .order_by('-count'))
    return render(request, 'market_analysis/dashboard.html', {
        'skills_demand': skills_demand,
        'sources_count': sources_count
    })