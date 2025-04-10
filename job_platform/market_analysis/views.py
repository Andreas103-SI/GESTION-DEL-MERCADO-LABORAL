from django.shortcuts import render
from django.db.models import Count
from market_analysis.models import JobOffer, Skill
import json

def dashboard(request):
    # Habilidades más demandadas
    skills_demand = JobOffer.objects.values('skills__name').annotate(count=Count('id')).order_by('-count')[:10]
    # Filtrar valores nulos y asegurar cadenas válidas
    skills_labels = json.dumps([skill['skills__name'] for skill in skills_demand if skill['skills__name'] is not None])
    skills_data = json.dumps([skill['count'] for skill in skills_demand if skill['skills__name'] is not None])
    
    # Ofertas por fuente
    sources_count = JobOffer.objects.values('source').annotate(count=Count('id')).order_by('-count')
    sources_labels = json.dumps([source['source'] for source in sources_count])
    sources_data = json.dumps([source['count'] for source in sources_count])
    
    # Total de ofertas
    total_offers = JobOffer.objects.count()
    
    # Empresas más activas
    companies_count = JobOffer.objects.values('company').annotate(count=Count('id')).order_by('-count')[:5]

    context = {
        'skills_demand': skills_demand,
        'sources_count': sources_count,
        'total_offers': total_offers,
        'companies_count': companies_count,
        'skills_labels': skills_labels,
        'skills_data': skills_data,
        'sources_labels': sources_labels,
        'sources_data': sources_data,
    }
    return render(request, 'market_analysis/dashboard.html', context)