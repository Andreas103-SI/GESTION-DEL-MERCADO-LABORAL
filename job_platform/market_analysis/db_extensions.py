from django.apps import AppConfig

class MarketAnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'market_analysis'

    def ready(self):
        import market_analysis.db_extensions
