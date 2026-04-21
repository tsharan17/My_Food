"""
AGENT 3: ANALYSIS AGENT
---------------------------------------------------------
Evaluates nutritional values against daily targets and health conditions.
Produces severity levels, flags, and a daily health score.
"""

# Daily Recommended Intake (DRI) targets per condition
CONDITION_TARGETS = {
    "general": {
        "calories":  {"min": 1800, "max": 2200},
        "protein":   {"min": 50,   "max": 150},
        "carbs":     {"min": 225,  "max": 325},
        "fats":      {"min": 44,   "max": 78},
        "sugar":     {"min": 0,    "max": 50},
        "fiber":     {"min": 25,   "max": 38},
        "label": "General Health"
    },
    "weight_loss": {
        "calories":  {"min": 1200, "max": 1600},
        "protein":   {"min": 60,   "max": 120},
        "carbs":     {"min": 100,  "max": 180},
        "fats":      {"min": 30,   "max": 55},
        "sugar":     {"min": 0,    "max": 25},
        "fiber":     {"min": 25,   "max": 38},
        "label": "Weight Loss"
    },
    "diabetes": {
        "calories":  {"min": 1600, "max": 2000},
        "protein":   {"min": 50,   "max": 120},
        "carbs":     {"min": 130,  "max": 195},
        "fats":      {"min": 44,   "max": 70},
        "sugar":     {"min": 0,    "max": 25},
        "fiber":     {"min": 30,   "max": 45},
        "label": "Diabetes Management"
    },
    "high_bp": {
        "calories":  {"min": 1800, "max": 2000},
        "protein":   {"min": 50,   "max": 120},
        "carbs":     {"min": 225,  "max": 300},
        "fats":      {"min": 30,   "max": 55},
        "sugar":     {"min": 0,    "max": 36},
        "fiber":     {"min": 30,   "max": 40},
        "label": "High Blood Pressure"
    }
}

# Thresholds for single-food warnings
SINGLE_FOOD_THRESHOLDS = {
    "calories": {"moderate": 300, "high": 500},
    "fats":     {"moderate": 10,  "high": 20},
    "sugar":    {"moderate": 12,  "high": 25},
    "carbs":    {"moderate": 40,  "high": 70},
}

# Foods to avoid per condition
CONDITION_AVOID = {
    "diabetes":    ["junk", "sweet", "beverage"],   # sugar-heavy
    "weight_loss": ["junk", "sweet"],
    "high_bp":     ["junk"],                         # high sodium (indirect)
    "general":     []
}

CONDITION_PREFER = {
    "diabetes":    ["vegetable", "protein", "grain"],
    "weight_loss": ["vegetable", "protein", "fruit"],
    "high_bp":     ["vegetable", "fruit", "grain"],
    "general":     ["vegetable", "fruit", "protein", "grain", "dairy"]
}


class AnalysisAgent:
    """
    Agent 3: Analysis Agent
    Evaluates a food item and daily totals against condition-specific targets.
    """

    def analyze(self, nutrition: dict, daily_totals: dict, condition: str, mode: str = 'before') -> dict:
        """
        Analyze a food item in context of daily intake and health condition.

        Args:
            nutrition: Nutrition dict for the food
            daily_totals: Accumulated daily nutrition totals
            condition: Health condition key
            mode: 'before' (pre-analysis) or 'after' (post-log)

        Returns:
            Analysis dict with severity, flags, and messages
        """
        targets = CONDITION_TARGETS.get(condition, CONDITION_TARGETS["general"])
        avoid_categories = CONDITION_AVOID.get(condition, [])
        prefer_categories = CONDITION_PREFER.get(condition, [])

        flags = []
        severity = "green"  # green | yellow | red

        food_cat = nutrition.get("category", "")

        # ── Single-food checks ───────────────────────────────
        for nutrient, limits in SINGLE_FOOD_THRESHOLDS.items():
            val = nutrition.get(nutrient, 0)
            if val >= limits["high"]:
                flags.append({
                    "type": "red",
                    "nutrient": nutrient,
                    "message": f"⚠️ High {nutrient} ({val}{'kcal' if nutrient=='calories' else 'g'}) in this food!"
                })
                severity = "red"
            elif val >= limits["moderate"]:
                flags.append({
                    "type": "yellow",
                    "nutrient": nutrient,
                    "message": f"⚡ Moderate {nutrient} ({val}{'kcal' if nutrient=='calories' else 'g'}) in this food."
                })
                if severity == "green":
                    severity = "yellow"

        # ── Category-based condition warnings ────────────────
        if food_cat in avoid_categories:
            flags.append({
                "type": "red",
                "nutrient": "category",
                "message": f"🚫 {food_cat.capitalize()} foods are not ideal for {targets['label']}."
            })
            severity = "red"
        elif food_cat in prefer_categories:
            flags.append({
                "type": "green",
                "nutrient": "category",
                "message": f"✅ Great choice for {targets['label']}!"
            })

        # ── Daily accumulation checks ─────────────────────────
        projected = {}
        for key in ["calories", "protein", "carbs", "fats", "sugar", "fiber"]:
            projected[key] = daily_totals.get(key, 0) + nutrition.get(key, 0)

        daily_flags = []
        for nutrient, target in targets.items():
            if nutrient == "label":
                continue
            proj_val = projected.get(nutrient, 0)
            max_val = target["max"]
            if proj_val > max_val * 1.2:
                daily_flags.append({
                    "type": "red",
                    "message": f"🔴 Daily {nutrient} will exceed limit ({proj_val:.0f} / {max_val})!"
                })
                severity = "red"
            elif proj_val > max_val:
                daily_flags.append({
                    "type": "yellow",
                    "message": f"🟡 Daily {nutrient} nearing limit ({proj_val:.0f} / {max_val})."
                })
                if severity == "green":
                    severity = "yellow"

        # ── Compute health score for this item (out of 10) ───
        item_score = self._item_health_score(nutrition, condition)

        return {
            "severity": severity,
            "flags": flags,
            "daily_flags": daily_flags,
            "projected_totals": projected,
            "item_health_score": item_score,
            "condition": condition,
            "condition_label": targets["label"],
            "mode": mode
        }

    def _item_health_score(self, nutrition: dict, condition: str) -> float:
        """Score a single food item out of 10 based on its nutritional profile."""
        score = 7.0  # neutral start
        cat = nutrition.get("category", "")

        # Category adjustments
        if cat in ["vegetable", "fruit"]:
            score += 2.0
        elif cat in ["protein", "grain", "dairy"]:
            score += 1.0
        elif cat == "junk":
            score -= 3.0
        elif cat == "sweet":
            score -= 2.5
        elif cat == "beverage":
            score += 0.5

        # Nutrient adjustments
        cal = nutrition.get("calories", 0)
        fat = nutrition.get("fats", 0)
        sugar = nutrition.get("sugar", 0)
        fiber = nutrition.get("fiber", 0)
        protein = nutrition.get("protein", 0)

        if cal > 500: score -= 1.5
        elif cal > 300: score -= 0.5

        if fat > 20: score -= 1.5
        elif fat > 10: score -= 0.5

        if sugar > 25: score -= 1.5
        elif sugar > 12: score -= 0.5

        if fiber > 4: score += 0.5
        if protein > 15: score += 0.5

        # Condition-specific adjustments
        avoid_cats = CONDITION_AVOID.get(condition, [])
        if cat in avoid_cats:
            score -= 2.0

        return max(0.0, min(10.0, round(score, 1)))

    def daily_health_score(self, totals: dict, condition: str) -> float:
        """
        Compute a daily health score (0-10) based on how well totals
        align with condition targets.
        """
        if not any(totals.values()):
            return None

        targets = CONDITION_TARGETS.get(condition, CONDITION_TARGETS["general"])
        score = 10.0
        nutrients_checked = ["calories", "carbs", "fats", "sugar"]

        for nutrient in nutrients_checked:
            target = targets.get(nutrient, {})
            val = totals.get(nutrient, 0)
            max_v = target.get("max", 999)
            min_v = target.get("min", 0)

            if val > max_v * 1.3:
                score -= 2.0
            elif val > max_v * 1.1:
                score -= 1.0
            elif val > max_v:
                score -= 0.5
            elif val < min_v * 0.5 and val > 0:
                score -= 0.5

        # Fiber bonus
        fiber_target = targets.get("fiber", {}).get("min", 25)
        if totals.get("fiber", 0) >= fiber_target:
            score += 0.5

        return max(0.0, min(10.0, round(score, 1)))

    def get_targets(self, condition: str) -> dict:
        """Return daily targets for a given condition"""
        return CONDITION_TARGETS.get(condition, CONDITION_TARGETS["general"])
