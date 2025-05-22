# data_integration/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .scrapers.linkedin import scrape_linkedin
from .scrapers.tecnoempleo import scrape_tecnoempleo
from market_analysis.models import JobOffer
from django.db.models import Count
from datetime import datetime, timedelta
import json
from django.db.models import Q

# Vista para la página principal de scraping.
# Muestra la página de inicio para iniciar el scraping.
def scrape_index(request):
    # Renderiza la plantilla de la página de inicio del scraping.
    return render(request, 'data_integration/scrape_index.html', {})

# Vista para iniciar el scraping de LinkedIn.
# Realiza el scraping cuando se recibe una solicitud POST y redirige a los resultados.
def scrape_linkedin_view(request):
    if request.method == 'POST':
        try:
            # Llama a la función de scraping de LinkedIn y muestra un mensaje de éxito.
            scrape_linkedin(request)
            messages.success(request, 'Datos de LinkedIn actualizados correctamente.')
            return redirect('data_integration:scrape_results')
        except Exception as e:
            # Muestra un mensaje de error si ocurre una excepción durante el scraping.
            messages.error(request, f'Error al actualizar LinkedIn: {e}')
            return redirect('data_integration:scrape_index')
    # Renderiza la plantilla de la página de inicio del scraping si no es una solicitud POST.
    return render(request, 'data_integration/scrape_index.html', {})

# Vista para iniciar el scraping de Tecnoempleo.
# Realiza el scraping cuando se recibe una solicitud POST y redirige a los resultados.
def scrape_tecnoempleo_view(request):
    if request.method == 'POST':
        try:
            # Llama a la función de scraping de Tecnoempleo y muestra un mensaje de éxito.
            scrape_tecnoempleo(request)
            messages.success(request, 'Datos de Tecnoempleo actualizados correctamente.')
            return redirect('data_integration:scrape_results')
        except Exception as e:
            # Muestra un mensaje de error si ocurre una excepción durante el scraping.
            messages.error(request, f'Error al actualizar Tecnoempleo: {e}')
            return redirect('data_integration:scrape_index')
    # Renderiza la plantilla de la página de inicio del scraping si no es una solicitud POST.
    return render(request, 'data_integration/scrape_index.html', {})

# Vista para mostrar los resultados del scraping.
# Muestra las ofertas de trabajo extraídas en los últimos 30 días.
def scrape_results(request):
    # Calcula la fecha de hace un mes para filtrar las ofertas recientes.
    one_month_ago = datetime.now().date() - timedelta(days=30)
    
    # Obtener el término de búsqueda
    search_query = request.GET.get('search', '')
    
    # Filtra las ofertas de trabajo publicadas en el último mes
    offers = JobOffer.objects.filter(publication_date__gte=one_month_ago)
    
    # Aplicar filtro de búsqueda si existe
    if search_query:
        offers = offers.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(skills__name__icontains=search_query)
        ).distinct()
    
    # Ordenar por fecha de publicación
    offers = offers.order_by('-publication_date')
    
    num_offers = offers.count()
    context = {
        'offers': offers,
        'num_offers': num_offers,
        'search_query': search_query,
    }
    # Renderiza la plantilla con los resultados del scraping.
    return render(request, 'data_integration/scrape_results.html', context)

# Vista para el panel de control.
# Muestra gráficos de las ofertas de trabajo por fuente en los últimos 30 días.
def dashboard_view(request):
    # Calcula la fecha de hace un mes para filtrar las ofertas recientes.
    one_month_ago = datetime.now().date() - timedelta(days=30)
    
    # Datos para gráficos de fuentes
    sources_count = JobOffer.objects.filter(publication_date__gte=one_month_ago).values('source').annotate(count=Count('id')).order_by('-count')
    sources_labels = json.dumps([source['source'] for source in sources_count])
    sources_data = json.dumps([source['count'] for source in sources_count])
    
    # Datos para gráfico de habilidades más demandadas
    skills_data = JobOffer.objects.filter(
        publication_date__gte=one_month_ago,
        skills__isnull=False
    ).values('skills__name').annotate(count=Count('id')).order_by('-count')[:10]
    
    skills_labels = json.dumps([skill['skills__name'] for skill in skills_data])
    skills_data = json.dumps([skill['count'] for skill in skills_data])
    
    # Datos para gráfico de habilidades futuras (últimos 7 días)
    seven_days_ago = datetime.now().date() - timedelta(days=7)
    future_skills_data = JobOffer.objects.filter(
        publication_date__gte=seven_days_ago,
        skills__isnull=False
    ).values('skills__name').annotate(count=Count('id')).order_by('-count')[:5]
    
    future_skills_labels = json.dumps([skill['skills__name'] for skill in future_skills_data])
    future_skills_data = json.dumps([skill['count'] for skill in future_skills_data])
    
    # Datos para comparación entre plataformas
    platform_comparison = {}
    for source in ['LinkedIn', 'Tecnoempleo']:
        skills = JobOffer.objects.filter(
            publication_date__gte=one_month_ago,
            source=source,
            skills__isnull=False
        ).values('skills__name').annotate(count=Count('id')).order_by('-count')[:5]
        platform_comparison[source] = [{'name': s['skills__name'], 'count': s['count']} for s in skills]
    
    # Preparar datos para el gráfico de comparación
    all_skills = set()
    for platform_data in platform_comparison.values():
        all_skills.update(item['name'] for item in platform_data)
    
    comparison_data = {
        'labels': sorted(list(all_skills)),
        'datasets': []
    }
    
    colors = ['#4CAF50', '#2196F3']  # Verde para LinkedIn, Azul para Tecnoempleo
    for i, (platform, skills) in enumerate(platform_comparison.items()):
        skill_counts = {item['name']: item['count'] for item in skills}
        data = [skill_counts.get(skill, 0) for skill in comparison_data['labels']]
        comparison_data['datasets'].append({
            'label': platform,
            'data': data,
            'backgroundColor': colors[i],
            'borderColor': colors[i],
            'fill': False
        })
    
    context = {
        'sources_count': sources_count,
        'sources_labels': sources_labels,
        'sources_data': sources_data,
        'skills_labels': skills_labels,
        'skills_data': skills_data,
        'future_skills_labels': future_skills_labels,
        'future_skills_data': future_skills_data,
        'platform_comparison': platform_comparison,
        'comparison_data': json.dumps(comparison_data),
    }
    return render(request, 'data_integration/dashboard.html', context)