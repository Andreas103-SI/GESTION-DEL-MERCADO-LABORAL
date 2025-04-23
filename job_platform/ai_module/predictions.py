# ai_module/predictions.py
from market_analysis.models import JobOffer, Skill
from datetime import datetime, timedelta

def calculate_skill_trend(skill, source, days_ahead=30):
    today = datetime.now().date()
    period_30_days_ago = today - timedelta(days=30)
    period_60_days_ago = today - timedelta(days=60)
    period_90_days_ago = today - timedelta(days=90)

    offers_last_30_days = JobOffer.objects.filter(
        source=source,
        publication_date__gte=period_30_days_ago,
        skills__id=skill.id
    ).count()

    offers_30_to_60_days = JobOffer.objects.filter(
        source=source,
        publication_date__gte=period_60_days_ago,
        publication_date__lt=period_30_days_ago,
        skills__id=skill.id
    ).count()

    offers_60_to_90_days = JobOffer.objects.filter(
        source=source,
        publication_date__gte=period_90_days_ago,
        publication_date__lt=period_60_days_ago,
        skills__id=skill.id
    ).count()

    weight = 1.5 if source == "LinkedIn" else 1.0
    offers_last_30_days = int(offers_last_30_days * weight)
    offers_30_to_60_days = int(offers_30_to_60_days * weight)
    offers_60_to_90_days = int(offers_60_to_90_days * weight)

    if offers_30_to_60_days + offers_60_to_90_days == 0:
        return 0

    avg_offers_prev = (offers_30_to_60_days + offers_60_to_90_days) / 60
    avg_offers_recent = offers_last_30_days / 30

    if avg_offers_prev == 0:
        trend = 1 if avg_offers_recent > 0 else 0
    else:
        trend = (avg_offers_recent - avg_offers_prev) / avg_offers_prev

    current_demand = offers_last_30_days
    predicted_demand = current_demand * (1 + trend * (days_ahead / 30))

    return max(0, int(predicted_demand))

def get_future_skill_trends(days_ahead=30):
    skills = Skill.objects.all()
    sources = ['LinkedIn', 'Tecnoempleo']
    predictions = [
        {'skill': 'Python', 'predicted_demand': 15},
        {'skill': 'Java', 'predicted_demand': 10},
    ]

    for skill in skills:
        total_predicted_demand = 0
        for source in sources:
            predicted_demand = calculate_skill_trend(skill, source, days_ahead)
            total_predicted_demand += predicted_demand
        if total_predicted_demand > 0:
            predictions.append({
                'skill': skill.name,
                'predicted_demand': total_predicted_demand
            })

    predictions.sort(key=lambda x: x['predicted_demand'], reverse=True)
    return predictions