from sklearn.linear_model import LinearRegression
import numpy as np
from market_analysis.models import MarketData, Skill
from datetime import datetime, timedelta

def predict_skill_demand(skill, source, days_ahead=30):
    three_months_ago = datetime.now().date() - timedelta(days=90)
    historical_data = MarketData.objects.filter(
        skill=skill,
        source=source,
        date__gte=three_months_ago
    ).order_by('date')

    if historical_data.count() < 2:
        return 0

    dates = [(d.date - three_months_ago).days for d in historical_data]
    demands = [d.demand_count for d in historical_data]

    X = np.array(dates).reshape(-1, 1)
    y = np.array(demands)

    model = LinearRegression()
    model.fit(X, y)

    future_day = (datetime.now().date() - three_months_ago).days + days_ahead
    predicted_demand = model.predict([[future_day]])[0]

    return max(0, int(predicted_demand))

def get_future_skill_trends(days_ahead=30):
    skills = Skill.objects.all()
    sources = ['LinkedIn', 'Tecnoempleo']
    predictions = []

    for skill in skills:
        total_predicted_demand = 0
        for source in sources:
            predicted_demand = predict_skill_demand(skill, source, days_ahead)
            total_predicted_demand += predicted_demand
        if total_predicted_demand > 0:
            predictions.append({
                'skill': skill.name,
                'predicted_demand': total_predicted_demand
            })

    predictions.sort(key=lambda x: x['predicted_demand'], reverse=True)
    return predictions[:5]