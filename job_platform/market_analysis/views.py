# market_analysis/views.py
from django.shortcuts import render, redirect
from django.db.models import Count
from django.contrib import messages
from market_analysis.models import JobOffer, Skill, MarketData
from ai_module.recommendations import recommend_tasks
from ai_module.predictions import get_future_skill_trends
from datetime import datetime, timedelta
import json
from data_integration.scrapers.linkedin import scrape_linkedin
from data_integration.scrapers.tecnoempleo import scrape_tecnoempleo

def dashboard(request):
    one_month_ago = datetime.now().date() - timedelta(days=30)
    
    # Habilidades más demandadas (global)
    skills_demand = JobOffer.objects.filter(publication_date__gte=one_month_ago).values('skills__name').annotate(count=Count('id')).order_by('-count')[:10]
    skills_labels = json.dumps([skill['skills__name'].capitalize() for skill in skills_demand if skill['skills__name']])
    skills_data = json.dumps([skill['count'] for skill in skills_demand if skill['skills__name']])
    
    # Ofertas por fuente
    sources_count = JobOffer.objects.filter(publication_date__gte=one_month_ago).values('source').annotate(count=Count('id')).order_by('-count')
    sources_labels = json.dumps([source['source'] for source in sources_count])
    sources_data = json.dumps([source['count'] for source in sources_count])
    
    # Habilidades por región (Asturias como ejemplo)
    asturias_skills = JobOffer.objects.filter(
        publication_date__gte=one_month_ago,
        location__icontains='Asturias'
    ).values('skills__name').annotate(count=Count('id')).order_by('-count')[:5]
    asturias_labels = json.dumps([skill['skills__name'].capitalize() for skill in asturias_skills if skill['skills__name']])
    asturias_data = json.dumps([skill['count'] for skill in asturias_skills if skill['skills__name']])
    
    # Comparación entre plataformas
    platform_comparison = {}
    for source in ['LinkedIn', 'Tecnoempleo']:
        skills = JobOffer.objects.filter(
            publication_date__gte=one_month_ago,
            source=source
        ).values('skills__name').annotate(count=Count('id')).order_by('-count')[:3]
        platform_comparison[source] = [
            {'name': skill['skills__name'].capitalize(), 'count': skill['count']}
            for skill in skills if skill['skills__name']
        ]
    
    # Actualizar MarketData
    for skill in Skill.objects.all():
        for source in ['LinkedIn', 'Tecnoempleo']:
            count = JobOffer.objects.filter(
                publication_date__gte=one_month_ago,
                source=source,
                skills=skill
            ).count()
            MarketData.objects.update_or_create(
                date=datetime.now().date(),
                skill=skill,
                source=source,
                defaults={'demand_count': count}
            )
    
    # Recomendaciones de tareas (solo para usuarios autenticados)
    recommended_tasks = []
    if request.user.is_authenticated and request.user.role == 'collaborator':
        recommended_tasks = recommend_tasks(request.user)

    # Predicciones de habilidades futuras
    future_skills = get_future_skill_trends()

    total_offers = JobOffer.objects.filter(publication_date__gte=one_month_ago).count()
    companies_count = JobOffer.objects.filter(publication_date__gte=one_month_ago).values('company').annotate(count=Count('id')).order_by('-count')[:5]
    recent_offers = JobOffer.objects.filter(publication_date__gte=one_month_ago).order_by('-publication_date')[:10]

    context = {
        'skills_demand': skills_demand,
        'sources_count': sources_count,
        'asturias_skills': asturias_skills,
        'platform_comparison': platform_comparison,
        'recommended_tasks': recommended_tasks,
        'future_skills': future_skills,
        'total_offers': total_offers,
        'companies_count': companies_count,
        'recent_offers': recent_offers,
        'skills_labels': skills_labels,
        'skills_data': skills_data,
        'sources_labels': sources_labels,
        'sources_data': sources_data,
        'asturias_labels': asturias_labels,
        'asturias_data': asturias_data,
    }
    return render(request, 'market_analysis/dashboard.html', context)

def update_scraper(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Debes iniciar sesión para actualizar los datos.')
        return redirect('dashboard')
    if request.method == 'POST':
        source = request.POST.get('source')
        if source == 'LinkedIn':
            try:
                scrape_linkedin(request)
                messages.info(request, 'Datos de LinkedIn actualizados.')
            except Exception as e:
                messages.error(request, f'Error al actualizar LinkedIn: {e}')
        elif source == 'Tecnoempleo':
            try:
                scrape_tecnoempleo(request)
                messages.success(request, 'Tecnoempleo se actualizó correctamente.')
            except Exception as e:
                messages.error(request, f'Error al ejecutar el scraper de Tecnoempleo: {e}')
        else:
            messages.error(request, 'Fuente no válida.')
        return redirect('dashboard')
    return redirect('dashboard')