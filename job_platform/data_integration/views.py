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
            return HttpResponseRedirect('/data/scrape-results/')
        except Exception as e:
            # Muestra un mensaje de error si ocurre una excepción durante el scraping.
            messages.error(request, f'Error al actualizar LinkedIn: {e}')
            return HttpResponseRedirect('/data/')
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
            return HttpResponseRedirect('/data/scrape-results/')
        except Exception as e:
            # Muestra un mensaje de error si ocurre una excepción durante el scraping.
            messages.error(request, f'Error al actualizar Tecnoempleo: {e}')
            return HttpResponseRedirect('/data/')
    # Renderiza la plantilla de la página de inicio del scraping si no es una solicitud POST.
    return render(request, 'data_integration/scrape_index.html', {})

# Vista para mostrar los resultados del scraping.
# Muestra las ofertas de trabajo extraídas en los últimos 30 días.
def scrape_results(request):
    # Calcula la fecha de hace un mes para filtrar las ofertas recientes.
    one_month_ago = datetime.now().date() - timedelta(days=30)
    # Filtra las ofertas de trabajo publicadas en el último mes y las ordena por fecha de publicación.
    offers = JobOffer.objects.filter(publication_date__gte=one_month_ago).order_by('-publication_date')
    num_offers = offers.count()
    context = {
        'offers': offers,
        'num_offers': num_offers,
    }
    # Renderiza la plantilla con los resultados del scraping.
    return render(request, 'data_integration/scrape_results.html', context)

# Vista para el panel de control.
# Muestra gráficos de las ofertas de trabajo por fuente en los últimos 30 días.
def dashboard_view(request):
    # Calcula la fecha de hace un mes para filtrar las ofertas recientes.
    one_month_ago = datetime.now().date() - timedelta(days=30)
    
    # Datos para gráficos
    # Cuenta las ofertas de trabajo por fuente y las ordena por cantidad.
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
    # Renderiza la plantilla del panel de control con los datos de los gráficos.
    return render(request, 'data_integration/dashboard.html', context)