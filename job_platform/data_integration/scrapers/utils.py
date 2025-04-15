# data_integration/scrapers/utils.py
from datetime import datetime, timedelta
import re

def parse_relative_date(date_text):
    """
    Convierte textos como 'hace 2 días' en una fecha absoluta.
    """
    now = datetime.now().date()
    date_text = date_text.lower()
    if "hace" in date_text:
        match = re.search(r'(\d+)\s*(hora|día|semana|mes)', date_text)
        if match:
            value, unit = match.groups()
            value = int(value)
            if "hora" in unit:
                return now
            elif "día" in unit:
                return now - timedelta(days=value)
            elif "semana" in unit:
                return now - timedelta(weeks=value)
            elif "mes" in unit:
                return now - timedelta(days=value * 30)
    return now