# market_analysis/views.py
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.contrib import messages
from market_analysis.models import JobOffer, Skill, MarketData
from ai_module.recommendations import recommend_tasks
from ai_module.predictions import get_future_skill_trends
from datetime import datetime, timedelta
import json
from data_integration.scrapers.linkedin import scrape_linkedin
from data_integration.scrapers.tecnoempleo import scrape_tecnoempleo
from django.core.paginator import Paginator

def dashboard(request):
    one_month_ago = datetime.now().date() - timedelta(days=30)
    
    # Habilidades más demandadas
    skills_demand = JobOffer.objects.filter(
        publication_date__gte=one_month_ago,
        skills__isnull=False,
        skills__name__isnull=False,
        skills__name__gt=''
    ).values('skills__name').annotate(count=Count('id')).order_by('-count')[:10]
    skills_labels = json.dumps([skill['skills__name'].capitalize() for skill in skills_demand])
    skills_data = json.dumps([skill['count'] for skill in skills_demand])
    
    print("Skills Labels:", skills_labels)
    print("Skills Data:", skills_data)
    
    # Ofertas por fuente
    sources_count = JobOffer.objects.filter(publication_date__gte=one_month_ago).values('source').annotate(count=Count('id')).order_by('-count')
    sources_labels = json.dumps([source['source'] for source in sources_count])
    sources_data = json.dumps([source['count'] for source in sources_count])
    
    print("Sources Labels:", sources_labels)
    print("Sources Data:", sources_data)
    
    # Habilidades por región (Asturias)
    asturias_skills = JobOffer.objects.filter(
        publication_date__gte=one_month_ago,
        location__icontains='Asturias',
        skills__isnull=False,
        skills__name__isnull=False,
        skills__name__gt=''
    ).values('skills__name').annotate(count=Count('id')).order_by('-count')[:5]
    
    # Total de ofertas
    total_offers = JobOffer.objects.filter(publication_date__gte=one_month_ago).count()
    
    # Empresas con más ofertas
    companies_count = JobOffer.objects.filter(
        publication_date__gte=one_month_ago
    ).values('company').annotate(count=Count('id')).order_by('-count')[:5]
    
    # Comparación entre plataformas
    platform_comparison = {}
    for source in ['LinkedIn', 'Tecnoempleo']:
        skills = JobOffer.objects.filter(
            publication_date__gte=one_month_ago,
            source=source,
            skills__isnull=False,
            skills__name__isnull=False,
            skills__name__gt=''
        ).values('skills__name').annotate(count=Count('id')).order_by('-count')[:5]
        platform_comparison[source] = [{'name': s['skills__name'], 'count': s['count']} for s in skills]
    
    # Predicciones de habilidades futuras
    try:
        future_skills = get_future_skill_trends()
    except Exception as e:
        print("Error en predicciones:", e)
        future_skills = []
    
    # Recomendaciones de tareas
    try:
        recommended_tasks = recommend_tasks(request.user)
    except Exception as e:
        print("Error en recomendaciones:", e)
        recommended_tasks = []
    
    # Ofertas recientes con búsqueda y filtro
    search_query = request.GET.get('search', '')
    priority_filter = request.GET.get('priority', '')
    
    recent_offers = JobOffer.objects.filter(
        publication_date__gte=one_month_ago
    ).order_by('-publication_date')
    
    if search_query:
        recent_offers = recent_offers.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    paginator = Paginator(recent_offers, 10)
    page_number = request.GET.get('page')
    recent_offers = paginator.get_page(page_number)
    
    context = {
        'skills_demand': skills_demand,
        'skills_labels': skills_labels,
        'skills_data': skills_data,
        'sources_count': sources_count,
        'sources_labels': sources_labels,
        'sources_data': sources_data,
        'asturias_skills': asturias_skills,
        'total_offers': total_offers,
        'companies_count': companies_count,
        'platform_comparison': platform_comparison,
        'future_skills': future_skills,
        'recommended_tasks': recommended_tasks,
        'recent_offers': recent_offers,
        'search_query': search_query,
        'priority_filter': priority_filter,
    }
    
    return render(request, 'market_analysis/dashboard.html', context)

def update_scraper(request):
    if request.method == 'POST':
        source = request.POST.get('source')
        try:
            if source == 'LinkedIn':
                scrape_linkedin(request)
                messages.success(request, 'Datos de LinkedIn actualizados correctamente.')
            elif source == 'Tecnoempleo':
                scrape_tecnoempleo(request)
                messages.success(request, 'Datos de Tecnoempleo actualizados correctamente.')
        except Exception as e:
            messages.error(request, f'Error al actualizar {source}: {e}')
    return redirect('dashboard')