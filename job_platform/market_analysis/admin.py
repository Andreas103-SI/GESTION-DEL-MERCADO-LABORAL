#market_analysis/admin.py
from django.contrib import admin
from .models import JobOffer, MarketData

admin.site.register(JobOffer)
admin.site.register(MarketData)