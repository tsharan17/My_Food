import random  # ✅ FIX: global import

# ─────────────────────────────────────────────────────────────
# AGENT 4: RECOMMENDATION AGENT
# ─────────────────────────────────────────────────────────────

# Condition-specific advice banks
CONDITION_TIPS = {
    "general": [
        "Aim for a balanced plate: half vegetables, quarter protein, quarter grains.",
        "Stay hydrated — drink at least 8 glasses of water daily.",
        "Include fiber-rich foods like fruits, vegetables, and whole grains.",
        "Limit processed and packaged foods.",
        "Eat slowly and mindfully to avoid overeating.",
    ],
    "weight_loss": [
        "Keep calories under 1600 kcal/day for steady weight loss.",
        "Prioritize protein to stay full longer and preserve muscle.",
        "Avoid sugary drinks, snacks, and desserts.",
        "Fill half your plate with non-starchy vegetables.",
        "Eat smaller portions spread across 4-5 meals.",
    ],
    "diabetes": [
        "Choose low-glycemic foods: oats, brown rice, lentils, vegetables.",
        "Avoid sugary foods and refined carbohydrates.",
        "Eat consistent meals at regular times.",
        "Pair carbs with protein or fiber.",
    ],
    "high_bp": [
        "Limit sodium intake — avoid processed foods and pickles.",
        "Eat potassium-rich foods: banana, spinach, sweet potato.",
        "Avoid caffeine and sugary beverages.",
    ]
}

CATEGORY_ADVICE = {
    "junk": [
        "Limit junk food — high in unhealthy fats and sodium.",
        "Try baking instead of frying.",
    ],
    "sweet": [
        "Limit sweets — they spike blood sugar.",
        "Try fruits instead of desserts.",
    ],
    "protein": [
        "Good protein choice! Helps muscle and satiety.",
    ],
    "vegetable": [
        "Excellent! Vegetables are nutrient-dense and low calorie.",
    ]
}

SEVERITY_MESSAGES = {
    "green": {
        "before": "✅ Healthy choice!",
        "after": "✅ Good job logging this meal!"
    },
    "yellow": {
        "before": "⚡ Moderate food — control portions.",
        "after": "⚡ Keep balance in mind."
    },
    "red": {
        "before": "🚨 Not ideal for your health goals.",
        "after": "🚨 Balance this with healthier foods."
    }
}

RECOVERY_SUGGESTIONS = {
    "calories": "Take a short walk to burn extra calories.",
    "carbs": "Next meal: more protein, fewer carbs.",
    "fats": "Choose grilled or steamed food next.",
}


class RecommendationAgent:

    def recommend(self, food_name, nutrition, analysis, condition, daily_totals):

        item_score = analysis.get("item_health_score", 7.0)

        # ✅ Severity logic
        if item_score >= 8:
            severity = "green"
        elif item_score >= 5:
            severity = "yellow"
        else:
            severity = "red"

        mode = analysis.get("mode", "before")
        category = nutrition.get("category", "")

        summary = SEVERITY_MESSAGES.get(severity, {}).get(mode, "")

        # 🔹 Warnings
        warnings = [
            f["message"]
            for f in analysis.get("flags", [])
            if f["type"] in ["red", "yellow"]
        ]

        # 🔹 Positives
        positives = [
            f["message"]
            for f in analysis.get("flags", [])
            if f["type"] == "green"
        ]

        # 🔹 Suggestions
        suggestions = []

        for flag in analysis.get("daily_flags", []):
            for key, rec in RECOVERY_SUGGESTIONS.items():
                if key in flag.get("message", "").lower():
                    suggestions.append(rec)

        # Category advice
        cat_advice = CATEGORY_ADVICE.get(category, [])
        if cat_advice:
            suggestions.append(random.choice(cat_advice))

        # Tips
        condition_tips = CONDITION_TIPS.get(condition, CONDITION_TIPS["general"])
        tips = random.sample(condition_tips, min(2, len(condition_tips)))

        # Alternatives
        alternatives = self._suggest_alternatives(category, condition)

        # Remove duplicates
        suggestions = list(dict.fromkeys(suggestions))
        warnings = list(dict.fromkeys(warnings))
        positives = list(dict.fromkeys(positives))
        tips = list(dict.fromkeys(tips))

        # Limit suggestions based on severity
        if severity == "green":
            suggestions = suggestions[:1]
        elif severity == "yellow":
            suggestions = suggestions[:2]
        else:
            suggestions = suggestions[:3]

        return {
            "summary": summary,
            "warnings": warnings,
            "positives": positives,
            "suggestions": suggestions,
            "tips": tips,
            "alternatives": alternatives,
            "health_score": item_score,
            "score_label": self._score_label(item_score),
            "severity": severity
        }

    def _suggest_alternatives(self, category, condition):
        if category == "junk":
            return ["Try grilled food instead", "Switch to fruits or nuts"]
        if category == "sweet":
            return ["Try fruit instead", "Use dark chocolate in small amount"]
        return []

    def _score_label(self, score):
        if score >= 8:
            return "Excellent"
        elif score >= 6:
            return "Good"
        elif score >= 4:
            return "Moderate"
        else:
            return "Poor"