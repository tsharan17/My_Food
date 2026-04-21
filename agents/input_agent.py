"""
AGENT 1: INPUT AGENT
---------------------------------------------------------
Responsible for parsing and normalizing user food input.
Handles aliases, spelling corrections, and portion normalization.
"""

import re

# Alias map: common names/variants → canonical food key
FOOD_ALIASES = {
    # Grains
    "white rice": "rice", "boiled rice": "rice", "cooked rice": "rice",
    "brown rice": "brown_rice", "basmati": "rice", "basmati rice": "rice",
    "chapati": "roti", "chapatti": "roti", "phulka": "roti", "wheat roti": "roti",
    "white bread": "bread", "brown bread": "brown_bread", "multigrain bread": "brown_bread",
    "oats": "oatmeal", "oatmeal": "oatmeal", "porridge": "oatmeal",
    "poha": "poha", "flattened rice": "poha",
    "upma": "upma", "semolina upma": "upma",
    "dosa": "dosa", "plain dosa": "dosa", "masala dosa": "dosa",
    "idli": "idli", "idly": "idli",
    "noodles": "noodles", "maggi": "noodles", "instant noodles": "noodles",
    "pasta": "pasta", "spaghetti": "pasta",

    # Proteins
    "egg": "egg", "boiled egg": "egg", "fried egg": "egg", "scrambled egg": "egg",
    "chicken": "chicken", "grilled chicken": "chicken", "roasted chicken": "chicken",
    "chicken breast": "chicken", "boiled chicken": "chicken",
    "fish": "fish", "salmon": "fish", "tuna": "fish", "tilapia": "fish",
    "dal": "dal", "lentils": "dal", "red dal": "dal", "toor dal": "dal",
    "sambar": "sambar", "sambhar": "sambar",
    "paneer": "paneer", "cottage cheese": "paneer",
    "rajma": "rajma", "kidney beans": "rajma",
    "chana": "chickpeas", "chickpeas": "chickpeas", "chole": "chickpeas",

    # Dairy
    "milk": "milk", "whole milk": "milk", "skimmed milk": "milk",
    "curd": "curd", "yogurt": "curd", "dahi": "curd",
    "butter": "butter", "ghee": "ghee", "clarified butter": "ghee",
    "cheese": "cheese", "cheddar": "cheese",

    # Fruits
    "apple": "apple", "green apple": "apple", "red apple": "apple",
    "banana": "banana", "ripe banana": "banana",
    "orange": "orange", "oranges": "orange",
    "mango": "mango", "ripe mango": "mango",
    "grapes": "grapes", "green grapes": "grapes", "red grapes": "grapes",
    "watermelon": "watermelon",
    "papaya": "papaya",
    "guava": "guava",

    # Vegetables
    "salad": "salad", "green salad": "salad", "vegetable salad": "salad",
    "spinach": "spinach", "palak": "spinach",
    "broccoli": "broccoli",
    "carrot": "carrot", "carrots": "carrot",
    "tomato": "tomato", "tomatoes": "tomato",
    "potato": "potato", "boiled potato": "potato", "aloo": "potato",
    "sweet potato": "sweet_potato",

    # Snacks & Junk
    "pizza": "pizza", "cheese pizza": "pizza",
    "burger": "burger", "hamburger": "burger", "veggie burger": "burger",
    "fries": "french_fries", "french fries": "french_fries", "chips": "french_fries",
    "samosa": "samosa",
    "biscuit": "biscuit", "biscuits": "biscuit", "cookie": "biscuit",
    "chocolate": "chocolate", "dark chocolate": "chocolate",
    "ice cream": "ice_cream", "icecream": "ice_cream",

    # Beverages
    "coffee": "coffee", "black coffee": "coffee", "cappuccino": "coffee",
    "tea": "tea", "green tea": "green_tea", "chai": "tea", "milk tea": "tea",
    "juice": "juice", "orange juice": "juice", "apple juice": "juice",
    "soda": "soda", "cola": "soda", "coke": "soda", "pepsi": "soda",
    "water": "water",

    # Sweets / Desserts
    "ladoo": "ladoo", "laddoo": "ladoo",
    "halwa": "halwa", "sooji halwa": "halwa",
    "kheer": "kheer", "rice pudding": "kheer",
}


class InputAgent:
    """
    Agent 1: Input Agent
    Primary interface for transforming natural language food mentions
    into canonical keys used by the Nutrition Agent.
    """

    def parse(self, raw_food: str, portion: float = 1.0) -> dict:
        """
        Parse user input into normalized food key + metadata.

        Args:
            raw_food: Raw string from user (e.g., "2 bowls of rice")
            portion: Portion multiplier

        Returns:
            dict with food_key, display_name, portion
        """
        cleaned = raw_food.lower().strip()
        cleaned = re.sub(r'[^a-z0-9 ]', '', cleaned)

        # Try to extract quantity words
        quantity_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'half': 0.5, 'quarter': 0.25, 'a': 1, 'an': 1
        }
        for word, qty in quantity_words.items():
            pattern = r'\b' + word + r'\b'
            if re.search(pattern, cleaned):
                cleaned = re.sub(pattern, '', cleaned).strip()
                if portion == 1.0:
                    portion = qty
                break

        # Remove common filler words
        stop_words = ['bowl', 'bowls', 'plate', 'plates', 'cup', 'cups',
                      'of', 'the', 'some', 'glass', 'glasses', 'serving', 'servings',
                      'piece', 'pieces', 'slice', 'slices']
        words = [w for w in cleaned.split() if w not in stop_words]
        cleaned = ' '.join(words).strip()

        # Lookup alias
        food_key = FOOD_ALIASES.get(cleaned, cleaned.replace(' ', '_'))

        return {
            'food_key': food_key,
            'display_name': raw_food.strip(),
            'portion': portion
        }

    def get_all_foods(self) -> list:
        """Return list of all known food display names"""
        return sorted(set(FOOD_ALIASES.keys()))
