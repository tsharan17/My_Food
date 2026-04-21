"""
My Food – Main Application
Agent-based architecture using Flask.
Refined for a clean, minimal, premium user experience.
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, date, timedelta
import json
import os

# ─────────────────────────────────────────────────────────────
# AGENT IMPORTS
# Each module is a self-contained intelligent component:
#   Agent 1 – Input Agent    : Parses & normalises user food input
#   Agent 2 – Nutrition Agent: Returns per-serving nutritional data
#   Agent 3 – Analysis Agent : Evaluates intake vs health targets
#   Agent 4 – Recommendation : Generates human-readable advice
#   Agent 5 – Tracking Agent : Maintains daily/weekly history
# ─────────────────────────────────────────────────────────────
from agents.input_agent import InputAgent            # Agent 1
from agents.nutrition_agent import NutritionAgent    # Agent 2
from agents.analysis_agent import AnalysisAgent      # Agent 3
from agents.recommendation_agent import RecommendationAgent  # Agent 4
from agents.tracking_agent import TrackingAgent      # Agent 5

# ── Flask app setup ───────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'myfood-secret-2024')

# ── Instantiate all agents at startup ─────────────────────────
input_agent          = InputAgent()
nutrition_agent      = NutritionAgent()
analysis_agent       = AnalysisAgent()
recommendation_agent = RecommendationAgent()
tracking_agent       = TrackingAgent()

# ── In-memory storage (resets on restart – suitable for demo) ─
daily_log  = {}   # {date_str: [entry, ...]}
weekly_log = {}   # kept for tracking agent compatibility


# ─────────────────────────────────────────────────────────────
# HELPER UTILITIES
# ─────────────────────────────────────────────────────────────

def get_today() -> str:
    """Return today's date as an ISO string (YYYY-MM-DD)."""
    return date.today().isoformat()


def get_daily_totals(log_date: str = None) -> dict:
    """
    Aggregate nutritional totals for all entries on a given date.
    Falls back to today if no date is supplied.
    """
    if log_date is None:
        log_date = get_today()
    entries = daily_log.get(log_date, [])
    totals = {"calories": 0, "protein": 0, "carbs": 0,
              "fats": 0, "fiber": 0, "sugar": 0}
    for entry in entries:
        for key in totals:
            totals[key] += entry.get("nutrition", {}).get(key, 0)
    return totals


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────

@app.route('/')
def landing():
    """Landing page – clean hero with app name, tagline, and start button."""
    return render_template('landing.html')


@app.route('/dashboard')
def index():
    """Dashboard – main food logging and health monitor view."""
    today             = get_today()
    daily_totals      = get_daily_totals(today)
    entries           = daily_log.get(today, [])
    health_condition  = session.get('health_condition', 'general')
    return render_template(
        'index.html',
        daily_totals=daily_totals,
        entries=entries,
        health_condition=health_condition,
        today=today
    )


# ── Agent Pipeline: Analyse (before eating) ───────────────────
@app.route('/api/analyze', methods=['POST'])
def analyze_food():
    """
    Pre-meal analysis endpoint.
    Pipeline: Input Agent → Nutrition Agent → Analysis Agent → Recommendation Agent
    Returns nutritional data and health advice WITHOUT logging the food.
    """
    data             = request.get_json()
    food_name        = data.get('food', '').strip()
    meal_type        = data.get('meal_type', 'general')
    health_condition = data.get('health_condition',
                                session.get('health_condition', 'general'))
    portion          = float(data.get('portion', 1.0))

    if not food_name:
        return jsonify({'error': 'Please enter a food item.'}), 400

    # Agent 1: Normalise input (handles aliases, spelling variants, portions)
    parsed_food = input_agent.parse(food_name, portion)

    # Agent 2: Fetch nutrition data for the resolved food key
    nutrition = nutrition_agent.get_nutrition(parsed_food['food_key'], portion)

    if not nutrition:
        return jsonify({
            'error': (f'Food "{food_name}" not found. '
                      'Try: rice, bread, egg, chicken, apple, banana, '
                      'milk, dal, roti, idli, sambar, coffee, tea, salad.')
        }), 404

    # Agent 3: Evaluate nutrition against today's totals and health condition
    today_totals = get_daily_totals()
    analysis     = analysis_agent.analyze(nutrition, today_totals,
                                          health_condition, mode='before')

    # Agent 4: Generate human-readable recommendation
    recommendation = recommendation_agent.recommend(
        food_name, nutrition, analysis, health_condition, today_totals
    )

    return jsonify({
        'food':           food_name,
        'portion':        portion,
        'nutrition':      nutrition,
        'analysis':       analysis,
        'recommendation': recommendation,
        'mode':           'before'
    })


# ── Agent Pipeline: Log (after eating) ───────────────────────
@app.route('/api/log', methods=['POST'])
def log_food():
    """
    Post-meal logging endpoint.
    Runs the same pipeline as /api/analyze, but also persists the
    entry to daily_log and notifies the Tracking Agent.
    """
    data             = request.get_json()
    food_name        = data.get('food', '').strip()
    meal_type        = data.get('meal_type', 'general')
    health_condition = data.get('health_condition',
                                session.get('health_condition', 'general'))
    portion          = float(data.get('portion', 1.0))

    if not food_name:
        return jsonify({'error': 'Please enter a food item.'}), 400

    # Agent 1: Normalise input
    parsed_food = input_agent.parse(food_name, portion)

    # Agent 2: Fetch nutrition
    nutrition = nutrition_agent.get_nutrition(parsed_food['food_key'], portion)

    if not nutrition:
        return jsonify({
            'error': (f'Food "{food_name}" not found. '
                      'Try: rice, bread, egg, chicken, apple, banana, '
                      'milk, dal, roti, idli, sambar, coffee, tea, salad.')
        }), 404

    # Persist entry to in-memory daily log
    today = get_today()
    entry = {
        'food':             food_name,
        'portion':          portion,
        'meal_type':        meal_type,
        'nutrition':        nutrition,
        'time':             datetime.now().strftime('%H:%M'),
        'health_condition': health_condition
    }
    daily_log.setdefault(today, []).append(entry)

    # Agent 5: Update tracking with the new log
    tracking_agent.update_daily(today, daily_log[today])

    # Agent 3: Re-evaluate now including the just-logged food
    today_totals = get_daily_totals(today)
    analysis     = analysis_agent.analyze(nutrition, today_totals,
                                          health_condition, mode='after')

    # Agent 4: Generate post-meal recommendation
    recommendation = recommendation_agent.recommend(
        food_name, nutrition, analysis, health_condition, today_totals
    )

    return jsonify({
        'food':           food_name,
        'portion':        portion,
        'nutrition':      nutrition,
        'analysis':       analysis,
        'recommendation': recommendation,
        'daily_totals':   today_totals,
        'entries_today':  len(daily_log.get(today, [])),
        'mode':           'after'
    })


# ── Health Condition ──────────────────────────────────────────
@app.route('/api/set_condition', methods=['POST'])
def set_condition():
    """
    Persist the user's health condition in the server session.
    Accepted values: general | weight_loss | diabetes | high_bp
    """
    data      = request.get_json()
    condition = data.get('condition', 'general')
    valid     = ['weight_loss', 'diabetes', 'high_bp', 'general']
    if condition not in valid:
        return jsonify({'error': 'Invalid condition.'}), 400
    session['health_condition'] = condition
    return jsonify({'status': 'ok', 'condition': condition})


# ── Daily Summary ─────────────────────────────────────────────
@app.route('/api/daily_summary')
def daily_summary():
    """Return today's aggregated nutrition totals and a health score."""
    today            = get_today()
    totals           = get_daily_totals(today)
    entries          = daily_log.get(today, [])
    health_condition = session.get('health_condition', 'general')
    score            = analysis_agent.daily_health_score(totals, health_condition)
    return jsonify({
        'date':        today,
        'totals':      totals,
        'entries':     entries,
        'health_score': score,
        'entry_count': len(entries)
    })


# ── Weekly Summary ────────────────────────────────────────────
@app.route('/api/weekly_summary')
def weekly_summary():
    """Return a 7-day rolling summary of daily nutrition and health scores."""
    weekly_data      = []
    today            = date.today()
    health_condition = session.get('health_condition', 'general')
    for i in range(6, -1, -1):
        day     = (today - timedelta(days=i)).isoformat()
        totals  = get_daily_totals(day)
        entries = daily_log.get(day, [])
        score   = (analysis_agent.daily_health_score(totals, health_condition)
                   if entries else None)
        weekly_data.append({
            'date':        day,
            'day':         (today - timedelta(days=i)).strftime('%a'),
            'totals':      totals,
            'entry_count': len(entries),
            'health_score': score
        })
    return jsonify({'weekly': weekly_data})


# ── Clear Today (testing helper) ──────────────────────────────
@app.route('/api/clear_today', methods=['POST'])
def clear_today():
    """Reset today's food log — useful during testing and demos."""
    today = get_today()
    daily_log[today] = []
    return jsonify({'status': 'cleared', 'date': today})


# ── Health Check ──────────────────────────────────────────────
@app.route('/health')
def health_check():
    """Lightweight liveness probe for Cloud Run / load balancers."""
    return jsonify({'status': 'healthy', 'service': 'My Food'})


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # default local port
    app.run(host='0.0.0.0', port=port, debug=True)