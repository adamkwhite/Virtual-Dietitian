"""
Canadian Nutrient File (CNF) API client.
Provides food lookup and nutrition data from Health Canada database.
"""

from typing import Dict, List, Optional

import requests
from nutrition_utils import infer_food_category


class CNFClient:
    """Client for Canadian Nutrient File API."""

    BASE_URL = "https://food-nutrition.canada.ca/api/canadian-nutrient-file/"

    def __init__(self):
        """Initialize CNF API client."""
        self._foods_list = None  # Cached list of all 5,690 foods
        self._nutrition_cache = {}  # Cached nutrition data by food_code

    def get_cnf_foods_list(self) -> List[Dict]:
        """
        Get list of all CNF foods (downloads once, then caches).

        Returns:
            List of food dicts:
            [
                {
                    "food_code": 109,
                    "food_description": "Cheese, gouda"
                },
                ...
            ]
        """
        if self._foods_list is not None:
            return self._foods_list

        # Download all foods from CNF API
        url = f"{self.BASE_URL}food/"
        params = {"lang": "en", "type": "json"}

        try:
            print(f"[CNF] Downloading food list from {url}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            self._foods_list = response.json()
            print(f"[CNF] Downloaded {len(self._foods_list)} foods")
            return self._foods_list
        except requests.exceptions.RequestException as e:
            print(f"[CNF] Error downloading food list: {e}")
            return []

    def search_food(self, query: str) -> Optional[int]:
        """
        Search for food by name (fuzzy matching).

        Args:
            query: Food name to search for (e.g., "chicken")

        Returns:
            food_code (int) if found, None otherwise
        """
        foods = self.get_cnf_foods_list()

        if not foods:
            return None

        query_lower = query.lower().strip()

        # Return None for empty queries
        if not query_lower:
            return None

        # Try exact match first
        for food in foods:
            if query_lower == food["food_description"].lower():
                return food["food_code"]

        # Try contains match
        for food in foods:
            if query_lower in food["food_description"].lower():
                return food["food_code"]

        # Try reverse contains (query contains food name)
        for food in foods:
            if food["food_description"].lower() in query_lower:
                return food["food_code"]

        return None

    def get_nutrition_per_100g(self, food_name: str) -> Optional[Dict]:
        """
        Get nutrition data per 100g for a food item.

        This is the main method used by the nutrition calculator.
        Returns data in the same format as nutrition_db.json.

        Args:
            food_name: Name of food to look up (e.g., "chicken")

        Returns:
            Nutrition dict with values per 100g:
            {
                "calories": 357.0,
                "protein_g": 24.94,
                "carbs_g": 2.22,
                "fat_g": 28.0,
                "fiber_g": 0.0,
                "sodium_mg": 819.0,
                "vitamin_c_mg": 0.0,
                "calcium_mg": 700.0,
                "iron_mg": 0.24,
                "category": "dairy"
            }

            Returns None if food not found or API error.
        """
        # Search for food code
        food_code = self.search_food(food_name)

        if food_code is None:
            return None

        # Fetch nutrition data (with caching)
        return self._fetch_nutrition_data(food_code)

    def _fetch_nutrition_data(self, food_code: int) -> Optional[Dict]:
        """
        Fetch nutrition data for a specific food code.

        Checks cache first, then calls API if needed.

        Args:
            food_code: CNF food code

        Returns:
            Normalized nutrition dict or None
        """
        # Check cache
        if food_code in self._nutrition_cache:
            return self._nutrition_cache[food_code]

        # Fetch from API
        url = f"{self.BASE_URL}nutrientamount/"
        params = {"id": food_code, "lang": "en", "type": "json"}

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            cnf_data = response.json()

            # Normalize to our schema
            nutrition = self._normalize_nutrient_data(cnf_data)

            # Cache it
            self._nutrition_cache[food_code] = nutrition

            return nutrition
        except requests.exceptions.RequestException as e:
            print(f"[CNF] Error fetching nutrition for food_code {food_code}: {e}")
            return None

    def _normalize_nutrient_data(self, cnf_data: List[Dict]) -> Dict:
        """
        Map CNF nutrient data to our schema.

        Args:
            cnf_data: List of nutrient dicts from CNF API

        Returns:
            Normalized nutrition dict
        """
        # Map CNF nutrient names to our schema
        nutrient_map = {
            "Energy (kcal)": "calories",
            "Protein": "protein_g",
            "Carbohydrate": "carbs_g",
            "Total Fat": "fat_g",
            "Fibre, total dietary": "fiber_g",
            "Sodium, Na": "sodium_mg",
            "Vitamin C": "vitamin_c_mg",
            "Calcium, Ca": "calcium_mg",
            "Iron, Fe": "iron_mg",
        }

        nutrition_data = {}

        # Extract nutrients
        for item in cnf_data:
            nutrient_name = item.get("nutrient_web_name", "")
            nutrient_value = item.get("nutrient_value", 0.0)

            if nutrient_name in nutrient_map:
                key = nutrient_map[nutrient_name]
                nutrition_data[key] = float(nutrient_value)

        # Fill in missing nutrients with 0
        for key in nutrient_map.values():
            if key not in nutrition_data:
                nutrition_data[key] = 0.0

        # Infer category using shared utility
        nutrition_data["category"] = infer_food_category(nutrition_data)

        return nutrition_data


# Singleton instance
_cnf_client = None


def get_cnf_client() -> CNFClient:
    """Get or create CNF API client singleton."""
    global _cnf_client
    if _cnf_client is None:
        _cnf_client = CNFClient()
    return _cnf_client
