from django.shortcuts import render
from django.db.models import Count
from market_analysis.models import JobOffer, Skill
from datetime import datetime, timedelta
import json

def dashboard(request):
    one_month_ago = datetime.now().date() - timedelta(days=30)
    skills_demand = JobOffer.objects.filter(publication_date__gte=one_month_ago).values('skills__name').annotate(count=Count('id')).order_by('-count')[:10]
    skills_labels = json.dumps([skill['skills__name'] for skill in skills_demand if skill['skills__name']])
    skills_data = json.dumps([skill['count'] for skill in skills_demand if skill['skills__name']])
    
    sources_count = JobOffer.objects.filter(publication_date__gte=one_month_ago).values('source').annotate(count=Count('id')).order_by('-count')
    sources_labels = json.dumps([source['source'] for source in sources_count])
    sources_data = json.dumps([source['count'] for source in sources_count])
    
    total_offers = JobOffer.objects.filter(publication_date__gte=one_month_ago).count()
    companies_count = JobOffer.objects.filter(publication_date__gte=one_month_ago).values('company').annotate(count=Count('id')).order_by('-count')[:5]
    recent_offers = JobOffer.objects.filter(publication_date__gte=one_month_ago).order_by('-publication_date')[:10]

    context = {
        'skills_demand': skills_demand,
        'sources_count': sources_count,
        'total_offers': total_offers,
        'companies_count': companies_count,
        'recent_offers': recent_offers,
        'skills_labels': skills_labels,
        'skills_data': skills_data,
        'sources_labels': sources_labels,
        'sources_data': sources_data,
    }
    return render(request, 'market_analysis/dashboard.html', context)