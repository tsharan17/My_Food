"""
AGENT 2: NUTRITION AGENT
---------------------------------------------------------
Maintains a compact, hand-curated nutrition database.
Returns per-serving nutritional values for known foods.
"""


# Compact nutrition database
# Format: food_key -> {calories, protein(g), carbs(g), fats(g), fiber(g), sugar(g), category}
NUTRITION_DB = {
    # ── Grains & Staples ──────────────────────────────────────
    "rice": {
        "calories": 206, "protein": 4.3, "carbs": 45, "fats": 0.4,
        "fiber": 0.6, "sugar": 0, "category": "grain",
        "serving": "1 cup cooked (186g)"
    },
    "brown_rice": {
        "calories": 216, "protein": 5, "carbs": 45, "fats": 1.8,
        "fiber": 3.5, "sugar": 0, "category": "grain",
        "serving": "1 cup cooked (195g)"
    },
    "roti": {
        "calories": 70, "protein": 2.5, "carbs": 15, "fats": 0.4,
        "fiber": 1.8, "sugar": 0, "category": "grain",
        "serving": "1 medium roti (40g)"
    },
    "bread": {
        "calories": 79, "protein": 2.7, "carbs": 15, "fats": 1,
        "fiber": 0.6, "sugar": 1.5, "category": "grain",
        "serving": "1 slice (28g)"
    },
    "brown_bread": {
        "calories": 69, "protein": 3.6, "carbs": 12, "fats": 1.2,
        "fiber": 1.9, "sugar": 1, "category": "grain",
        "serving": "1 slice (28g)"
    },
    "oatmeal": {
        "calories": 150, "protein": 5, "carbs": 27, "fats": 2.5,
        "fiber": 4, "sugar": 0, "category": "grain",
        "serving": "1 cup cooked (234g)"
    },
    "poha": {
        "calories": 180, "protein": 3, "carbs": 38, "fats": 2,
        "fiber": 1, "sugar": 0, "category": "grain",
        "serving": "1 cup (100g)"
    },
    "upma": {
        "calories": 200, "protein": 4, "carbs": 35, "fats": 5,
        "fiber": 2, "sugar": 0, "category": "grain",
        "serving": "1 cup (150g)"
    },
    "dosa": {
        "calories": 168, "protein": 3.9, "carbs": 33, "fats": 2.4,
        "fiber": 1.2, "sugar": 0, "category": "grain",
        "serving": "1 medium dosa (86g)"
    },
    "idli": {
        "calories": 58, "protein": 2, "carbs": 12, "fats": 0.4,
        "fiber": 0.5, "sugar": 0, "category": "grain",
        "serving": "1 piece (50g)"
    },
    "noodles": {
        "calories": 300, "protein": 7, "carbs": 56, "fats": 5,
        "fiber": 1, "sugar": 2, "category": "grain",
        "serving": "1 pack instant (80g)"
    },
    "pasta": {
        "calories": 220, "protein": 8, "carbs": 43, "fats": 1.3,
        "fiber": 2.5, "sugar": 1, "category": "grain",
        "serving": "1 cup cooked (140g)"
    },

    # ── Proteins ──────────────────────────────────────────────
    "egg": {
        "calories": 78, "protein": 6, "carbs": 0.6, "fats": 5,
        "fiber": 0, "sugar": 0.6, "category": "protein",
        "serving": "1 large egg (50g)"
    },
    "chicken": {
        "calories": 165, "protein": 31, "carbs": 0, "fats": 3.6,
        "fiber": 0, "sugar": 0, "category": "protein",
        "serving": "100g cooked breast"
    },
    "fish": {
        "calories": 136, "protein": 22, "carbs": 0, "fats": 5,
        "fiber": 0, "sugar": 0, "category": "protein",
        "serving": "100g cooked"
    },
    "dal": {
        "calories": 116, "protein": 9, "carbs": 20, "fats": 0.4,
        "fiber": 7.9, "sugar": 1.8, "category": "protein",
        "serving": "1 cup cooked (198g)"
    },
    "sambar": {
        "calories": 90, "protein": 4, "carbs": 14, "fats": 2,
        "fiber": 3, "sugar": 3, "category": "protein",
        "serving": "1 cup (200ml)"
    },
    "paneer": {
        "calories": 265, "protein": 18, "carbs": 3.6, "fats": 20,
        "fiber": 0, "sugar": 0, "category": "protein",
        "serving": "100g"
    },
    "rajma": {
        "calories": 127, "protein": 8.7, "carbs": 22.8, "fats": 0.5,
        "fiber": 6.4, "sugar": 0.3, "category": "protein",
        "serving": "1 cup cooked (172g)"
    },
    "chickpeas": {
        "calories": 164, "protein": 8.9, "carbs": 27, "fats": 2.6,
        "fiber": 7.6, "sugar": 4.8, "category": "protein",
        "serving": "1 cup cooked (164g)"
    },

    # ── Dairy ─────────────────────────────────────────────────
    "milk": {
        "calories": 149, "protein": 8, "carbs": 12, "fats": 8,
        "fiber": 0, "sugar": 12, "category": "dairy",
        "serving": "1 cup (244ml)"
    },
    "curd": {
        "calories": 100, "protein": 11, "carbs": 7.5, "fats": 2.9,
        "fiber": 0, "sugar": 7.5, "category": "dairy",
        "serving": "1 cup (245g)"
    },
    "butter": {
        "calories": 102, "protein": 0.1, "carbs": 0, "fats": 11.5,
        "fiber": 0, "sugar": 0, "category": "dairy",
        "serving": "1 tablespoon (14g)"
    },
    "ghee": {
        "calories": 112, "protein": 0, "carbs": 0, "fats": 12.7,
        "fiber": 0, "sugar": 0, "category": "dairy",
        "serving": "1 tablespoon (15g)"
    },
    "cheese": {
        "calories": 113, "protein": 7, "carbs": 0.4, "fats": 9,
        "fiber": 0, "sugar": 0, "category": "dairy",
        "serving": "1 slice (28g)"
    },

    # ── Fruits ────────────────────────────────────────────────
    "apple": {
        "calories": 95, "protein": 0.5, "carbs": 25, "fats": 0.3,
        "fiber": 4.4, "sugar": 19, "category": "fruit",
        "serving": "1 medium apple (182g)"
    },
    "banana": {
        "calories": 105, "protein": 1.3, "carbs": 27, "fats": 0.4,
        "fiber": 3.1, "sugar": 14, "category": "fruit",
        "serving": "1 medium banana (118g)"
    },
    "orange": {
        "calories": 62, "protein": 1.2, "carbs": 15, "fats": 0.2,
        "fiber": 3.1, "sugar": 12, "category": "fruit",
        "serving": "1 medium orange (131g)"
    },
    "mango": {
        "calories": 135, "protein": 0.9, "carbs": 35, "fats": 0.6,
        "fiber": 3.7, "sugar": 30, "category": "fruit",
        "serving": "1 cup sliced (165g)"
    },
    "grapes": {
        "calories": 104, "protein": 1.1, "carbs": 27, "fats": 0.2,
        "fiber": 1.4, "sugar": 23, "category": "fruit",
        "serving": "1 cup (151g)"
    },
    "watermelon": {
        "calories": 86, "protein": 1.7, "carbs": 21.6, "fats": 0.4,
        "fiber": 1.1, "sugar": 17.7, "category": "fruit",
        "serving": "2 cups diced (286g)"
    },
    "papaya": {
        "calories": 55, "protein": 0.6, "carbs": 14, "fats": 0.2,
        "fiber": 2.5, "sugar": 8, "category": "fruit",
        "serving": "1 cup cubed (145g)"
    },
    "guava": {
        "calories": 68, "protein": 2.6, "carbs": 14.3, "fats": 1,
        "fiber": 8.9, "sugar": 8.9, "category": "fruit",
        "serving": "1 medium guava (90g)"
    },

    # ── Vegetables ────────────────────────────────────────────
    "salad": {
        "calories": 20, "protein": 1.5, "carbs": 3.5, "fats": 0.2,
        "fiber": 2, "sugar": 1.5, "category": "vegetable",
        "serving": "1 cup mixed (67g)"
    },
    "spinach": {
        "calories": 23, "protein": 2.9, "carbs": 3.6, "fats": 0.4,
        "fiber": 2.2, "sugar": 0.4, "category": "vegetable",
        "serving": "1 cup cooked (180g)"
    },
    "broccoli": {
        "calories": 55, "protein": 3.7, "carbs": 11, "fats": 0.6,
        "fiber": 5.1, "sugar": 2.6, "category": "vegetable",
        "serving": "1 cup cooked (156g)"
    },
    "carrot": {
        "calories": 52, "protein": 1.2, "carbs": 12, "fats": 0.3,
        "fiber": 3.4, "sugar": 5.8, "category": "vegetable",
        "serving": "1 medium carrot (61g)"
    },
    "tomato": {
        "calories": 22, "protein": 1.1, "carbs": 4.8, "fats": 0.2,
        "fiber": 1.5, "sugar": 3.2, "category": "vegetable",
        "serving": "1 medium tomato (123g)"
    },
    "potato": {
        "calories": 163, "protein": 4.3, "carbs": 37, "fats": 0.2,
        "fiber": 3.8, "sugar": 1.7, "category": "vegetable",
        "serving": "1 medium (173g)"
    },
    "sweet_potato": {
        "calories": 103, "protein": 2.3, "carbs": 24, "fats": 0.1,
        "fiber": 3.8, "sugar": 7.4, "category": "vegetable",
        "serving": "1 medium (130g)"
    },

    # ── Snacks & Junk Food ────────────────────────────────────
    "pizza": {
        "calories": 285, "protein": 12, "carbs": 36, "fats": 10,
        "fiber": 2.5, "sugar": 3.6, "category": "junk",
        "serving": "1 slice (107g)"
    },
    "burger": {
        "calories": 354, "protein": 20, "carbs": 29, "fats": 17,
        "fiber": 1.3, "sugar": 5, "category": "junk",
        "serving": "1 regular burger"
    },
    "french_fries": {
        "calories": 365, "protein": 4, "carbs": 48, "fats": 17,
        "fiber": 4.4, "sugar": 0.3, "category": "junk",
        "serving": "medium serving (117g)"
    },
    "samosa": {
        "calories": 252, "protein": 4, "carbs": 24, "fats": 16,
        "fiber": 2, "sugar": 1, "category": "junk",
        "serving": "1 piece (80g)"
    },
    "biscuit": {
        "calories": 147, "protein": 2, "carbs": 21, "fats": 6,
        "fiber": 0.5, "sugar": 8, "category": "junk",
        "serving": "4 biscuits (40g)"
    },
    "chocolate": {
        "calories": 170, "protein": 2, "carbs": 17, "fats": 9,
        "fiber": 3, "sugar": 12, "category": "junk",
        "serving": "1 bar piece (40g)"
    },
    "ice_cream": {
        "calories": 207, "protein": 3.5, "carbs": 24, "fats": 11,
        "fiber": 0.6, "sugar": 21, "category": "junk",
        "serving": "1 cup (132g)"
    },

    # ── Beverages ─────────────────────────────────────────────
    "coffee": {
        "calories": 5, "protein": 0.3, "carbs": 0, "fats": 0,
        "fiber": 0, "sugar": 0, "category": "beverage",
        "serving": "1 cup black coffee (240ml)"
    },
    "tea": {
        "calories": 30, "protein": 0.5, "carbs": 3, "fats": 1.2,
        "fiber": 0, "sugar": 2, "category": "beverage",
        "serving": "1 cup with milk (200ml)"
    },
    "green_tea": {
        "calories": 2, "protein": 0, "carbs": 0, "fats": 0,
        "fiber": 0, "sugar": 0, "category": "beverage",
        "serving": "1 cup (240ml)"
    },
    "juice": {
        "calories": 112, "protein": 1.7, "carbs": 26, "fats": 0.5,
        "fiber": 0.5, "sugar": 21, "category": "beverage",
        "serving": "1 cup (248ml)"
    },
    "soda": {
        "calories": 139, "protein": 0, "carbs": 38, "fats": 0,
        "fiber": 0, "sugar": 38, "category": "beverage",
        "serving": "1 can (355ml)"
    },
    "water": {
        "calories": 0, "protein": 0, "carbs": 0, "fats": 0,
        "fiber": 0, "sugar": 0, "category": "beverage",
        "serving": "1 glass (250ml)"
    },

    # ── Sweets ────────────────────────────────────────────────
    "ladoo": {
        "calories": 174, "protein": 3, "carbs": 23, "fats": 8,
        "fiber": 1, "sugar": 15, "category": "sweet",
        "serving": "1 medium piece (40g)"
    },
    "halwa": {
        "calories": 180, "protein": 2.5, "carbs": 28, "fats": 7,
        "fiber": 0.5, "sugar": 18, "category": "sweet",
        "serving": "1 serving (100g)"
    },
    "kheer": {
        "calories": 200, "protein": 5, "carbs": 32, "fats": 6,
        "fiber": 0.3, "sugar": 24, "category": "sweet",
        "serving": "1 cup (200ml)"
    },
}

# Health flags per food category
CATEGORY_FLAGS = {
    "grain":     {"healthy": True,  "warning": False},
    "protein":   {"healthy": True,  "warning": False},
    "dairy":     {"healthy": True,  "warning": False},
    "fruit":     {"healthy": True,  "warning": False},
    "vegetable": {"healthy": True,  "warning": False},
    "beverage":  {"healthy": True,  "warning": False},
    "junk":      {"healthy": False, "warning": True},
    "sweet":     {"healthy": False, "warning": True},
}


class NutritionAgent:
    """
    Agent 2: Nutrition Agent
    Looks up and returns nutrition data for a given food key.
    """

    def get_nutrition(self, food_key: str, portion: float = 1.0) -> dict | None:
        """
        Get nutrition info for a food key, scaled by portion.
        Returns None if food not found.
        """
        data = NUTRITION_DB.get(food_key)
        if not data:
            return None

        scaled = {
            "calories": round(data["calories"] * portion, 1),
            "protein":  round(data["protein"]  * portion, 1),
            "carbs":    round(data["carbs"]     * portion, 1),
            "fats":     round(data["fats"]      * portion, 1),
            "fiber":    round(data["fiber"]     * portion, 1),
            "sugar":    round(data["sugar"]     * portion, 1),
            "category": data["category"],
            "serving":  data["serving"],
            "is_healthy": CATEGORY_FLAGS[data["category"]]["healthy"],
            "has_warning": CATEGORY_FLAGS[data["category"]]["warning"],
        }
        return scaled

    def get_all_foods(self) -> list:
        """Return sorted list of all food keys"""
        return sorted(NUTRITION_DB.keys())

    def get_food_categories(self) -> dict:
        """Return food keys grouped by category"""
        groups = {}
        for key, data in NUTRITION_DB.items():
            cat = data["category"]
            groups.setdefault(cat, []).append(key)
        return groups
