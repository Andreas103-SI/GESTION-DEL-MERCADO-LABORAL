# market_analysis/views.py
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.contrib import messages
from market_analysis.models import JobOffer, Skill, MarketData
from ai_module.recommendations import recommend_tasks
from datetime import datetime, timedelta
import json
from data_integration.scrapers.linkedin import scrape_linkedin
from data_integration.scrapers.tecnoempleo import scrape_tecnoempleo
from django.core.paginator import Paginator
from django.utils import timezone
from collections import defaultdict

def dashboard(request):
    one_month_ago = datetime.now().date() - timedelta(days=30)
    
    # Habilidades más demandadas (último mes)
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
    
    # Predicciones de habilidades futuras usando MarketData
    skill_trends = []
    future_skills_labels = json.dumps([])
    future_skills_data = json.dumps([])
    try:
        # Filtrar datos de MarketData de los últimos 30 días
        market_data = MarketData.objects.filter(date__gte=one_month_ago)
        
        # Agrupar por habilidad y calcular el promedio de demand_count
        skill_demand = defaultdict(list)
        for entry in market_data:
            # Convertir el objeto Skill a su nombre (str)
            skill_name = entry.skill.name if entry.skill else "Desconocido"
            skill_demand[skill_name].append(entry.demand_count)
        
        # Calcular promedio y ordenar por demanda descendente (top 5)
        skill_trends = [
            {'name': skill, 'count': sum(demands) / len(demands)} 
            for skill, demands in skill_demand.items() if len(demands) > 0
        ]
        skill_trends = sorted(skill_trends, key=lambda x: x['count'], reverse=True)[:5]
        
        # Generar datos para el gráfico
        future_skills_labels = json.dumps([trend['name'] for trend in skill_trends])
        future_skills_data = json.dumps([trend['count'] for trend in skill_trends])
    except Exception as e:
        print("Error al calcular tendencias de habilidades:", e)

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
    
    # Definir el contexto después de todas las variables
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
        'future_skills': skill_trends,
        'future_skills_labels': future_skills_labels,
        'future_skills_data': future_skills_data,
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
    return redirect('market_analysis:dashboard')