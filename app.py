"""
Food & Health Smart Assistant - Main Application
Agent-based architecture using Flask
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, date, timedelta
import json
import os

# Import agents
from agents.input_agent import InputAgent
from agents.nutrition_agent import NutritionAgent
from agents.analysis_agent import AnalysisAgent
from agents.recommendation_agent import RecommendationAgent
from agents.tracking_agent import TrackingAgent

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'food-health-assistant-secret-2024')

# Initialize agents
input_agent = InputAgent()
nutrition_agent = NutritionAgent()
analysis_agent = AnalysisAgent()
recommendation_agent = RecommendationAgent()
tracking_agent = TrackingAgent()

# In-memory storage (resets on restart — suitable for demo/competition)
daily_log = {}
weekly_log = {}


def get_today():
    return date.today().isoformat()


def get_daily_totals(log_date=None):
    if log_date is None:
        log_date = get_today()
    entries = daily_log.get(log_date, [])
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0, "fiber": 0, "sugar": 0}
    for entry in entries:
        for key in totals:
            totals[key] += entry.get("nutrition", {}).get(key, 0)
    return totals


@app.route('/')
def index():
    today = get_today()
    daily_totals = get_daily_totals(today)
    entries = daily_log.get(today, [])
    health_condition = session.get('health_condition', 'general')
    return render_template(
        'index.html',
        daily_totals=daily_totals,
        entries=entries,
        health_condition=health_condition,
        today=today
    )


@app.route('/api/analyze', methods=['POST'])
def analyze_food():
    """Analyze food before eating (pre-meal analysis)"""
    data = request.get_json()
    food_name = data.get('food', '').strip()
    meal_type = data.get('meal_type', 'general')
    health_condition = data.get('health_condition', session.get('health_condition', 'general'))
    portion = float(data.get('portion', 1.0))

    if not food_name:
        return jsonify({'error': 'Please enter a food item.'}), 400

    # Agent pipeline: Input → Nutrition → Analysis → Recommendation
    parsed_food = input_agent.parse(food_name, portion)
    nutrition = nutrition_agent.get_nutrition(parsed_food['food_key'], portion)

    if not nutrition:
        return jsonify({
            'error': f'Food "{food_name}" not found in database. Try: rice, bread, egg, chicken, apple, banana, milk, dal, roti, idli, sambar, coffee, tea, salad.'
        }), 404

    today_totals = get_daily_totals()
    analysis = analysis_agent.analyze(nutrition, today_totals, health_condition, mode='before')
    recommendation = recommendation_agent.recommend(
        food_name, nutrition, analysis, health_condition, today_totals
    )

    return jsonify({
        'food': food_name,
        'portion': portion,
        'nutrition': nutrition,
        'analysis': analysis,
        'recommendation': recommendation,
        'mode': 'before'
    })


@app.route('/api/log', methods=['POST'])
def log_food():
    """Log food after eating"""
    data = request.get_json()
    food_name = data.get('food', '').strip()
    meal_type = data.get('meal_type', 'general')
    health_condition = data.get('health_condition', session.get('health_condition', 'general'))
    portion = float(data.get('portion', 1.0))

    if not food_name:
        return jsonify({'error': 'Please enter a food item.'}), 400

    parsed_food = input_agent.parse(food_name, portion)
    nutrition = nutrition_agent.get_nutrition(parsed_food['food_key'], portion)

    if not nutrition:
        return jsonify({
            'error': f'Food "{food_name}" not found in database. Try: rice, bread, egg, chicken, apple, banana, milk, dal, roti, idli, sambar, coffee, tea, salad.'
        }), 404

    # Log the food
    today = get_today()
    entry = {
        'food': food_name,
        'portion': portion,
        'meal_type': meal_type,
        'nutrition': nutrition,
        'time': datetime.now().strftime('%H:%M'),
        'health_condition': health_condition
    }

    if today not in daily_log:
        daily_log[today] = []
    daily_log[today].append(entry)

    # Update tracking agent
    tracking_agent.update_daily(today, daily_log[today])

    today_totals = get_daily_totals(today)
    analysis = analysis_agent.analyze(nutrition, today_totals, health_condition, mode='after')
    recommendation = recommendation_agent.recommend(
        food_name, nutrition, analysis, health_condition, today_totals
    )

    return jsonify({
        'food': food_name,
        'portion': portion,
        'nutrition': nutrition,
        'analysis': analysis,
        'recommendation': recommendation,
        'daily_totals': today_totals,
        'entries_today': len(daily_log.get(today, [])),
        'mode': 'after'
    })


@app.route('/api/set_condition', methods=['POST'])
def set_condition():
    """Set health condition for the session"""
    data = request.get_json()
    condition = data.get('condition', 'general')
    valid_conditions = ['weight_loss', 'diabetes', 'high_bp', 'general']
    if condition not in valid_conditions:
        return jsonify({'error': 'Invalid condition'}), 400
    session['health_condition'] = condition
    return jsonify({'status': 'ok', 'condition': condition})


@app.route('/api/daily_summary')
def daily_summary():
    """Get today's nutrition summary"""
    today = get_today()
    totals = get_daily_totals(today)
    entries = daily_log.get(today, [])
    health_condition = session.get('health_condition', 'general')
    score = analysis_agent.daily_health_score(totals, health_condition)
    return jsonify({
        'date': today,
        'totals': totals,
        'entries': entries,
        'health_score': score,
        'entry_count': len(entries)
    })


@app.route('/api/weekly_summary')
def weekly_summary():
    """Get 7-day weekly summary"""
    weekly_data = []
    today = date.today()
    for i in range(6, -1, -1):
        day = (today - timedelta(days=i)).isoformat()
        totals = get_daily_totals(day)
        entries = daily_log.get(day, [])
        health_condition = session.get('health_condition', 'general')
        score = analysis_agent.daily_health_score(totals, health_condition) if entries else None
        weekly_data.append({
            'date': day,
            'day': (today - timedelta(days=i)).strftime('%a'),
            'totals': totals,
            'entry_count': len(entries),
            'health_score': score
        })
    return jsonify({'weekly': weekly_data})


@app.route('/api/clear_today', methods=['POST'])
def clear_today():
    """Clear today's log (for testing)"""
    today = get_today()
    daily_log[today] = []
    return jsonify({'status': 'cleared', 'date': today})


@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Food Health Assistant'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
