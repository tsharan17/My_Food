"""
AGENT 5: TRACKING AGENT
---------------------------------------------------------
Maintains in-memory daily and weekly summaries.
Computes streaks, weekly averages, and progress insights.
"""

from datetime import date, timedelta


class TrackingAgent:
    """
    Agent 5: Tracking Agent
    Manages daily food logs and weekly/monthly summaries.
    """

    def __init__(self):
        self._daily_summaries = {}  # date_str -> summary dict

    def update_daily(self, date_str: str, entries: list):
        """
        Recompute and store daily summary from log entries.

        Args:
            date_str: ISO date string (YYYY-MM-DD)
            entries: List of food entry dicts
        """
        totals = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0, "fiber": 0, "sugar": 0}
        for entry in entries:
            for key in totals:
                totals[key] += entry.get("nutrition", {}).get(key, 0)

        self._daily_summaries[date_str] = {
            "date": date_str,
            "totals": {k: round(v, 1) for k, v in totals.items()},
            "entry_count": len(entries),
            "foods": [e["food"] for e in entries]
        }

    def get_daily_summary(self, date_str: str) -> dict:
        """Get summary for a specific date"""
        return self._daily_summaries.get(date_str, {
            "date": date_str,
            "totals": {"calories": 0, "protein": 0, "carbs": 0, "fats": 0, "fiber": 0, "sugar": 0},
            "entry_count": 0,
            "foods": []
        })

    def get_weekly_summary(self, reference_date: str = None) -> list:
        """
        Get 7-day summary ending on reference_date (default: today).
        Returns list of daily summaries with computed averages.
        """
        if reference_date is None:
            ref = date.today()
        else:
            ref = date.fromisoformat(reference_date)

        days = []
        for i in range(6, -1, -1):
            d = (ref - timedelta(days=i)).isoformat()
            summary = self.get_daily_summary(d)
            summary["day_label"] = (ref - timedelta(days=i)).strftime("%a %d")
            days.append(summary)

        return days

    def get_weekly_averages(self, reference_date: str = None) -> dict:
        """Compute average daily nutrients for the past 7 days (only days with data)."""
        days = self.get_weekly_summary(reference_date)
        active_days = [d for d in days if d["entry_count"] > 0]

        if not active_days:
            return {}

        nutrients = ["calories", "protein", "carbs", "fats", "fiber", "sugar"]
        averages = {}
        for nutrient in nutrients:
            total = sum(d["totals"].get(nutrient, 0) for d in active_days)
            averages[nutrient] = round(total / len(active_days), 1)

        averages["active_days"] = len(active_days)
        return averages

    def get_streak(self) -> int:
        """Return number of consecutive days user has logged food (including today)."""
        today = date.today()
        streak = 0
        for i in range(0, 30):
            d = (today - timedelta(days=i)).isoformat()
            summary = self._daily_summaries.get(d)
            if summary and summary.get("entry_count", 0) > 0:
                streak += 1
            else:
                break
        return streak

    def get_progress_insight(self, weekly_days: list, condition: str) -> str:
        """Generate a simple text insight for weekly progress."""
        active = [d for d in weekly_days if d["entry_count"] > 0]
        if not active:
            return "No data logged this week. Start tracking your meals to see insights!"

        avg_cal = sum(d["totals"]["calories"] for d in active) / len(active)
        streak = self.get_streak()

        parts = []
        parts.append(f"You logged meals on {len(active)}/7 days this week.")
        if streak >= 3:
            parts.append(f"🔥 {streak}-day tracking streak — keep it up!")
        if avg_cal > 0:
            parts.append(f"Average daily intake: {avg_cal:.0f} kcal.")
        if condition == "weight_loss" and avg_cal < 1600:
            parts.append("✅ Calorie intake is within your weight loss target!")
        elif condition == "diabetes" and avg_cal < 2000:
            parts.append("✅ Calorie intake looks well-managed for diabetes care.")

        return " ".join(parts)
