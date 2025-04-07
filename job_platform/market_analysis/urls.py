from django.urls import path
from .views import market_dashboard

urlpatterns = [
    path('dashboard/', market_dashboard, name='market_dashboard'),
]