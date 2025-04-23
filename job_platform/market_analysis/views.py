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
from django.core.paginator import Paginator

def dashboard(request):
    one_month_ago = datetime.now().date() - timedelta(days=30)
    
    # Habilidades más demandadas (global)
    skills_demand = JobOffer.objects.filter(
        publication_date__gte=one_month_ago,
        skills__isnull=False,
        skills__name__isnull=False,
        skills__name__gt=''  # Excluye cadenas vacías
    ).values('skills__name').annotate(count=Count('id')).order_by('-count')[:10]
    skills_labels = json.dumps([skill['skills__name'].capitalize() for skill in skills_demand])
    skills_data = json.dumps([skill['count'] for skill in skills_demand])
    
    # Ofertas por fuente
    sources_count = JobOffer.objects.filter(publication_date__gte=one_month_ago).values('source').annotate(count=Count('id')).order_by('-count')
    sources_labels = json.dumps([source['source'] for source in sources_count])
    sources_data = json.dumps([source['count'] for source in sources_count])
    
    # Habilidades por región (Asturias como ejemplo)
    asturias_skills = JobOffer.objects.filter(
        publication_date__gte=one_month_ago,
        location__icontains='Asturias',
        skills__isnull=False,
        skills__name__isnull=False,
        skills__name__gt=''  # Excluye cadenas vacías
    ).values('skills__name').annotate(count=Count('id')).order_by('-count')[:5]
    asturias_labels = json.dumps([skill['skills__name'].capitalize() for skill in asturias_skills])
    asturias_data = json.dumps([skill['count'] for skill in asturias_skills])
    
    # Comparación entre plataformas
    platform_comparison = {}
    for source in ['LinkedIn', 'Tecnoempleo']:
        skills = JobOffer.objects.filter(
            publication_date__gte=one_month_ago,
            source=source,
            skills__isnull=False
        ).values('skills__name').annotate(count=Count('id')).order_by('-count')[:3]
        platform_comparison[source] = [
            {'name': skill['skills__name'].capitalize(), 'count': skill['count']}
            for skill in skills
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
    priority_filter = request.GET.get('priority', '')  # Obtener el filtro de prioridad
    if request.user.is_authenticated and request.user.role == 'collaborator':
        recommended_tasks = recommend_tasks(request.user)
        # Aplicar filtro de prioridad
        if priority_filter:
            recommended_tasks = [task for task in recommended_tasks if task.priority == priority_filter]

    # Predicciones de habilidades futuras
    future_skills = get_future_skill_trends()

    # Ofertas recientes con filtro de búsqueda y paginación
    search_query = request.GET.get('search', '')
    recent_offers = JobOffer.objects.filter(publication_date__gte=one_month_ago)
    if search_query:
        recent_offers = recent_offers.filter(
            title__icontains=search_query
        ) | recent_offers.filter(
            company__icontains=search_query
        ) | recent_offers.filter(
            location__icontains=search_query
        )
    recent_offers = recent_offers.order_by('-publication_date')
    
    # Añadir paginación
    paginator = Paginator(recent_offers, 10)
    page_number = request.GET.get('page', 1)
    recent_offers_page = paginator.get_page(page_number)

    total_offers = JobOffer.objects.filter(publication_date__gte=one_month_ago).count()
    companies_count = JobOffer.objects.filter(publication_date__gte=one_month_ago).values('company').annotate(count=Count('id')).order_by('-count')[:5]

    context = {
        'skills_demand': skills_demand,
        'sources_count': sources_count,
        'asturias_skills': asturias_skills,
        'platform_comparison': platform_comparison,
        'recommended_tasks': recommended_tasks,
        'future_skills': future_skills,
        'total_offers': total_offers,
        'companies_count': companies_count,
        'recent_offers': recent_offers_page,
        'skills_labels': skills_labels,
        'skills_data': skills_data,
        'sources_labels': sources_labels,
        'sources_data': sources_data,
        'asturias_labels': asturias_labels,
        'asturias_data': asturias_data,
        'search_query': search_query,
        'priority_filter': priority_filter,  # Añadir el filtro de prioridad al contexto
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