"""
USDA FoodData Central API client.
Provides food lookup and nutrition data retrieval from USDA database.
"""

import os

import requests
from nutrition_utils import infer_food_category


class USDAClient:
    """Client for USDA FoodData Central API."""

    BASE_URL = "https://api.nal.usda.gov/fdc/v1"

    def __init__(self, api_key: str | None = None):
        """
        Initialize USDA API client.

        Args:
            api_key: USDA API key. If not provided, reads from USDA_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("USDA_API_KEY", "DEMO_KEY")

    def search_food(self, query: str, page_size: int = 5) -> list[dict]:
        """
        Search for foods matching the query.

        Args:
            query: Food name to search for (e.g., "chicken breast")
            page_size: Number of results to return (default 5)

        Returns:
            List of food items with basic info:
            [
                {
                    "fdc_id": 123456,
                    "description": "Chicken, broilers or fryers, breast, meat only, raw",
                    "data_type": "Survey (FNDDS)",
                    "score": 825.5
                },
                ...
            ]
        """
        url = f"{self.BASE_URL}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": page_size,
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            return data.get("foods", [])
        except requests.exceptions.RequestException as e:
            print(f"Error searching USDA API for '{query}': {e}")
            return []

    def get_food_details(self, fdc_id: int) -> dict | None:
        """
        Get detailed nutrition information for a specific food.

        Args:
            fdc_id: USDA FoodData Central ID

        Returns:
            Food details with nutrients, or None if not found
        """
        url = f"{self.BASE_URL}/food/{fdc_id}"
        params = {"api_key": self.api_key}

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching USDA food details for FDC ID {fdc_id}: {e}")
            return None

    def get_nutrition_per_100g(self, food_name: str) -> dict | None:
        """
        Get nutrition data per 100g for a food item.

        This is the main method used by the nutrition calculator.
        Returns data in the same format as nutrition_db.json.

        Args:
            food_name: Name of food to look up (e.g., "salmon")

        Returns:
            Nutrition dict with values per 100g:
            {
                "calories": 206.0,
                "protein_g": 22.0,
                "carbs_g": 0.0,
                "fat_g": 12.4,
                "fiber_g": 0.0,
                "sodium_mg": 59.0,
                "vitamin_c_mg": 0.0,
                "calcium_mg": 12.0,
                "iron_mg": 0.8,
                "category": "protein"
            }

            Returns None if food not found or API error.
        """
        # Search for the food
        search_results = self.search_food(food_name, page_size=1)

        if not search_results:
            return None

        # Get the top result
        top_result = search_results[0]
        fdc_id = top_result.get("fdcId")

        if not fdc_id:
            return None

        # Get detailed nutrition data
        food_details = self.get_food_details(fdc_id)

        if not food_details:
            return None

        # Extract nutrients (USDA provides per 100g by default)
        nutrients = food_details.get("foodNutrients", [])

        # Map USDA nutrient IDs to our schema
        nutrient_map = {
            1008: "calories",  # Energy (kcal)
            1003: "protein_g",  # Protein
            1005: "carbs_g",  # Carbohydrate, by difference
            1004: "fat_g",  # Total lipid (fat)
            1079: "fiber_g",  # Fiber, total dietary
            1093: "sodium_mg",  # Sodium
            1162: "vitamin_c_mg",  # Vitamin C
            1087: "calcium_mg",  # Calcium
            1089: "iron_mg",  # Iron
        }

        nutrition_data = {}

        for nutrient in nutrients:
            nutrient_id = nutrient.get("nutrient", {}).get("id")
            amount = nutrient.get("amount", 0.0)

            if nutrient_id in nutrient_map:
                key = nutrient_map[nutrient_id]
                nutrition_data[key] = float(amount)

        # Fill in missing nutrients with 0
        for key in nutrient_map.values():
            if key not in nutrition_data:
                nutrition_data[key] = 0.0

        # Infer category using shared utility
        nutrition_data["category"] = infer_food_category(nutrition_data)

        return nutrition_data


# Singleton instance
_usda_client = None


def get_usda_client() -> USDAClient:
    """Get or create USDA API client singleton."""
    global _usda_client
    if _usda_client is None:
        _usda_client = USDAClient()
    return _usda_client
