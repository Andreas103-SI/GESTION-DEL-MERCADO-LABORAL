# data_integration/views.py
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from .scrapers.linkedin import scrape_linkedin
from .scrapers.tecnoempleo import scrape_tecnoempleo
from market_analysis.models import JobOffer
from django.db.models import Count
from datetime import datetime, timedelta
import json

def scrape_index(request):
    return render(request, 'data_integration/scrape_index.html', {})

def scrape_linkedin_view(request):
    if request.method == 'POST':
        try:
            scrape_linkedin(request)
            messages.success(request, 'Datos de LinkedIn actualizados correctamente.')
            return HttpResponseRedirect('/data/scrape-results/')
        except Exception as e:
            messages.error(request, f'Error al actualizar LinkedIn: {e}')
            return HttpResponseRedirect('/data/')
    return render(request, 'data_integration/scrape_index.html', {})

def scrape_tecnoempleo_view(request):
    if request.method == 'POST':
        try:
            scrape_tecnoempleo(request)
            messages.success(request, 'Datos de Tecnoempleo actualizados correctamente.')
            return HttpResponseRedirect('/data/scrape-results/')
        except Exception as e:
            messages.error(request, f'Error al actualizar Tecnoempleo: {e}')
            return HttpResponseRedirect('/data/')
    return render(request, 'data_integration/scrape_index.html', {})

def scrape_results(request):
    one_month_ago = datetime.now().date() - timedelta(days=30)
    offers = JobOffer.objects.filter(publication_date__gte=one_month_ago).order_by('-publication_date')
    num_offers = offers.count()
    context = {
        'offers': offers,
        'num_offers': num_offers,
    }
    return render(request, 'data_integration/scrape_results.html', context)

def dashboard_view(request):
    one_month_ago = datetime.now().date() - timedelta(days=30)
    
    # Datos para gráficos
    sources_count = JobOffer.objects.filter(publication_date__gte=one_month_ago).values('source').annotate(count=Count('id')).order_by('-count')
    sources_labels = json.dumps([source['source'] for source in sources_count])
    sources_data = json.dumps([source['count'] for source in sources_count])
    
    print("Sources Count:", list(sources_count))  # Depuración
    print("Sources Labels:", sources_labels)
    print("Sources Data:", sources_data)
    
    context = {
        'sources_count': sources_count,
        'sources_labels': sources_labels,
        'sources_data': sources_data,
    }
    return render(request, 'data_integration/dashboard.html', context)