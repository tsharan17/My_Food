"""
Recommendation Agent
Generates human-readable health advice, warnings, and suggestions
based on analysis output and health condition.
"""

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
        "Eat smaller portions spread across 4-5 meals rather than 2-3 large ones.",
        "Avoid fried and junk foods — they are calorie-dense with low nutrition.",
    ],
    "diabetes": [
        "Choose low-glycemic foods: oats, brown rice, lentils, vegetables.",
        "Avoid sugary foods, drinks, and refined carbohydrates.",
        "Eat consistent meals at regular times to manage blood sugar.",
        "Pair carbohydrates with protein or fiber to slow glucose absorption.",
        "Limit fruit intake to low-sugar varieties like guava, papaya, and berries.",
        "Avoid white rice, white bread, and instant noodles.",
    ],
    "high_bp": [
        "Limit sodium intake — avoid salty snacks, processed foods, and pickles.",
        "Eat potassium-rich foods: banana, spinach, sweet potato.",
        "Choose lean proteins like chicken, fish, and dal over red meat.",
        "Avoid alcohol, caffeine, and sugary beverages.",
        "Include magnesium-rich foods: leafy greens, nuts, whole grains.",
        "Maintain a healthy weight — even a small loss reduces BP significantly.",
    ]
}

# Specific food-category advice
CATEGORY_ADVICE = {
    "junk": [
        "Junk food is high in calories, sodium, and unhealthy fats. Limit to once a week.",
        "Try baking or air-frying instead of deep frying for healthier versions.",
        "Replace chips and fries with roasted chickpeas or carrot sticks.",
    ],
    "sweet": [
        "Sweets and desserts spike blood sugar rapidly. Enjoy occasionally.",
        "Try natural sweeteners like jaggery or dates in small amounts.",
        "Have a small portion of fruit to satisfy sweet cravings.",
    ],
    "grain": [
        "Choose whole grain options (brown rice, whole wheat roti) over refined grains.",
        "Control portion sizes for grains to manage carbohydrate intake.",
    ],
    "protein": [
        "Excellent protein choice! Protein keeps you full and supports muscle health.",
        "Try to include protein in every meal for sustained energy.",
    ],
    "vegetable": [
        "Great choice! Load up on vegetables — they are nutrient-dense and low in calories.",
        "Aim for a colorful plate with a variety of vegetables.",
    ],
    "fruit": [
        "Fruits are healthy but contain natural sugars. 2-3 servings per day is ideal.",
        "Eat whole fruits rather than juices to retain fiber.",
    ],
    "dairy": [
        "Dairy provides calcium and protein. Opt for low-fat varieties if watching weight.",
    ],
    "beverage": [
        "Stay well hydrated with water as your primary drink.",
        "Limit sugary beverages — they add empty calories.",
    ]
}

# Severity-based messages
SEVERITY_MESSAGES = {
    "green": {
        "before": "✅ This looks like a healthy choice! Go ahead and enjoy.",
        "after":  "✅ Good job logging your meal! This was a nutritious choice."
    },
    "yellow": {
        "before": "⚡ This food is moderate — eat it in controlled portions.",
        "after":  "⚡ Noted! Keep an eye on your daily totals to stay balanced."
    },
    "red": {
        "before": "🚨 Warning! This food may not be ideal for your health goals right now.",
        "after":  "🚨 Heads up! This added significantly to your daily totals. Balance with healthy foods next."
    }
}

# Suggestions for staying on track
RECOVERY_SUGGESTIONS = {
    "calories": "Take a 20-minute walk to burn some extra calories.",
    "carbs":    "Your next meal should be rich in vegetables and protein, low in carbs.",
    "fats":     "Opt for steamed, boiled, or grilled foods for your next meal.",
    "sugar":    "Drink a large glass of water and avoid any more sugary items today.",
    "fiber":    "Add a salad or fruit to boost your fiber intake today."
}


class RecommendationAgent:
    """
    Agent 4: Recommendation Agent
    Generates warnings, suggestions, and actionable advice.
    """

    def recommend(self, food_name: str, nutrition: dict, analysis: dict,
                  condition: str, daily_totals: dict) -> dict:
        """
        Generate a complete recommendation bundle.

        Returns:
            dict with: summary, warnings, suggestions, tips, health_score, score_label
        """
        severity = analysis.get("severity", "green")
        mode = analysis.get("mode", "before")
        category = nutrition.get("category", "")
        item_score = analysis.get("item_health_score", 7.0)

        # Main summary message
        summary = SEVERITY_MESSAGES.get(severity, {}).get(mode, "")

        # Collect warnings from flags
        warnings = []
        for flag in analysis.get("flags", []):
            if flag["type"] in ["red", "yellow"]:
                warnings.append(flag["message"])
        for flag in analysis.get("daily_flags", []):
            if flag["type"] in ["red", "yellow"]:
                warnings.append(flag["message"])

        # Positive notes
        positives = []
        for flag in analysis.get("flags", []):
            if flag["type"] == "green":
                positives.append(flag["message"])

        # Suggestions
        suggestions = []

        # Recovery suggestions based on which nutrients are over limit
        for flag in analysis.get("daily_flags", []):
            nutrient = flag.get("message", "")
            for key, rec in RECOVERY_SUGGESTIONS.items():
                if key in nutrient.lower() and rec not in suggestions:
                    suggestions.append(rec)

        # Category-specific suggestions
        cat_advice = CATEGORY_ADVICE.get(category, [])
        if cat_advice:
            suggestions.append(cat_advice[0])  # top one to keep it minimal

        # Condition-specific tips (pick 2)
        condition_tips = CONDITION_TIPS.get(condition, CONDITION_TIPS["general"])
        tips = self._pick_relevant_tips(condition_tips, nutrition, daily_totals)

        # Better alternatives (for junk/sweet)
        alternatives = self._suggest_alternatives(category, condition)

        # Compute score label
        score_label = self._score_label(item_score)

        return {
            "summary": summary,
            "warnings": warnings,
            "positives": positives,
            "suggestions": suggestions,
            "tips": tips,
            "alternatives": alternatives,
            "health_score": item_score,
            "score_label": score_label,
            "severity": severity
        }

    def _pick_relevant_tips(self, tips: list, nutrition: dict, daily_totals: dict) -> list:
        """Return up to 2 most relevant tips"""
        selected = []
        cal = nutrition.get("calories", 0)
        sugar = nutrition.get("sugar", 0)

        for tip in tips:
            if sugar > 10 and "sugar" in tip.lower():
                selected.append(tip)
            elif cal > 300 and "calori" in tip.lower():
                selected.append(tip)
            elif len(selected) < 2:
                selected.append(tip)
            if len(selected) >= 2:
                break
        return selected[:2]

    def _suggest_alternatives(self, category: str, condition: str) -> list:
        """Suggest healthier alternatives for junk/sweet foods"""
        if category == "junk":
            if condition == "weight_loss":
                return ["Try grilled chicken with salad instead.", "Replace fries with roasted sweet potato."]
            elif condition == "diabetes":
                return ["Try oatmeal or boiled eggs instead.", "A bowl of dal and roti is a healthier option."]
            else:
                return ["Try a homemade version with less oil.", "A bowl of fruits or mixed nuts is a great snack."]
        elif category == "sweet":
            return ["Try a small piece of dark chocolate (70%+) if craving sweets.", "Fresh fruit can satisfy sweet cravings with added nutrients."]
        elif category == "beverage" and condition == "diabetes":
            return ["Replace juice/soda with plain water or green tea.", "Add lemon to water for a refreshing, sugar-free drink."]
        return []

    def _score_label(self, score: float) -> str:
        if score >= 8:
            return "Excellent"
        elif score >= 6:
            return "Good"
        elif score >= 4:
            return "Moderate"
        elif score >= 2:
            return "Poor"
        else:
            return "Very Poor"
