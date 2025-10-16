"""
Food label mapping and serving size assignment for Vision API results.

This module bridges the gap between Vision API's generic labels (e.g., "Salad", "Food")
and our nutrition database's specific foods. It provides fuzzy matching to find the
best food match and assigns appropriate serving sizes based on food category.
"""

import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard serving sizes by food category (in grams)
STANDARD_SERVING_SIZES = {
    "protein": 85,  # 3 oz cooked meat/fish
    "grain": 50,  # 1/2 cup cooked rice/pasta, 1 slice bread
    "fruit": 150,  # 1 medium fruit or 1 cup fresh
    "vegetable": 85,  # 1 cup raw leafy, 1/2 cup cooked
    "dairy": 240,  # 1 cup milk/yogurt, 1 oz cheese
    "other": 100,  # Default serving
}

# Category-specific label keywords for enhanced matching
CATEGORY_KEYWORDS = {
    "protein": [
        "chicken",
        "beef",
        "pork",
        "fish",
        "salmon",
        "tuna",
        "turkey",
        "egg",
        "meat",
        "poultry",
        "seafood",
        "shrimp",
        "steak",
    ],
    "grain": [
        "rice",
        "pasta",
        "bread",
        "grain",
        "quinoa",
        "oat",
        "cereal",
        "wheat",
        "noodle",
    ],
    "fruit": [
        "apple",
        "banana",
        "orange",
        "berry",
        "strawberry",
        "blueberry",
        "grape",
        "melon",
        "peach",
        "pear",
        "fruit",
    ],
    "vegetable": [
        "broccoli",
        "carrot",
        "lettuce",
        "tomato",
        "spinach",
        "pepper",
        "onion",
        "cucumber",
        "vegetable",
        "salad",
    ],
    "dairy": ["cheese", "milk", "yogurt", "dairy", "butter", "cream"],
}


class FoodLabelMapper:
    """Map Vision API labels to specific foods with serving sizes."""

    def __init__(self, nutrition_db: List[Dict], cnf_client=None, usda_client=None):
        """
        Initialize mapper with nutrition databases.

        Args:
            nutrition_db: Local nutrition database (list of food dicts)
            cnf_client: Optional CNF API client
            usda_client: Optional USDA API client
        """
        self.nutrition_db = nutrition_db
        self.cnf_client = cnf_client
        self.usda_client = usda_client

    def map_label_to_food(self, label: str, category: str) -> Optional[Dict[str, any]]:
        """
        Map Vision API label to specific food from nutrition databases.

        Uses 3-tier fallback strategy:
        1. Local database (exact + fuzzy match)
        2. CNF API (if available)
        3. USDA API (if available)

        Args:
            label: Vision API label (e.g., "Salad", "Chicken dish")
            category: Inferred food category (protein, grain, fruit, vegetable, dairy, other)

        Returns:
            Food dictionary with nutrition data, or None if no match found:
            {
                "name": "grilled chicken breast",
                "calories": 165,
                "protein": 31,
                "category": "protein",
                "source": "local"  # or "cnf" or "usda"
            }
        """
        logger.info(f"Mapping label '{label}' (category: {category}) to specific food")

        # Strategy 1: Search local database
        local_match = self._search_local_db(label, category)
        if local_match:
            logger.info(f"Found local match: {local_match['name']}")
            return {**local_match, "source": "local"}

        # Strategy 2: Search CNF API
        if self.cnf_client:
            cnf_match = self._search_cnf_api(label, category)
            if cnf_match:
                logger.info(f"Found CNF match: {cnf_match['name']}")
                return {**cnf_match, "source": "cnf"}

        # Strategy 3: Search USDA API
        if self.usda_client:
            usda_match = self._search_usda_api(label, category)
            if usda_match:
                logger.info(f"Found USDA match: {usda_match['name']}")
                return {**usda_match, "source": "usda"}

        logger.warning(f"No food match found for label '{label}'")
        return None

    def _search_local_db(self, label: str, category: str) -> Optional[Dict]:
        """
        Search local nutrition database for matching food.

        Uses multi-level fuzzy matching:
        1. Exact match (case-insensitive)
        2. Contains match (label in food name)
        3. Reverse contains (food name in label)
        4. Category-based keyword match

        Args:
            label: Vision API label
            category: Food category

        Returns:
            Matching food dictionary or None
        """
        label_lower = label.lower()

        # Level 1: Exact match
        for food in self.nutrition_db:
            if food["name"].lower() == label_lower:
                return food

        # Level 2: Contains match (label is substring of food name)
        for food in self.nutrition_db:
            if label_lower in food["name"].lower():
                return food

        # Level 3: Reverse contains (food name is substring of label)
        for food in self.nutrition_db:
            if food["name"].lower() in label_lower:
                return food

        # Level 4: Category-based keyword match
        # If label contains category keywords, find first food in that category
        if category in CATEGORY_KEYWORDS:
            for keyword in CATEGORY_KEYWORDS[category]:
                if keyword in label_lower:
                    # Find first food in this category
                    for food in self.nutrition_db:
                        if food.get("category") == category:
                            logger.info(
                                f"Category-based match: '{label}' → '{food['name']}' "
                                f"(keyword: '{keyword}')"
                            )
                            return food

        return None

    def _search_cnf_api(self, label: str, category: str) -> Optional[Dict]:
        """
        Search CNF API for matching food.

        Args:
            label: Vision API label
            category: Food category

        Returns:
            Matching food dictionary or None
        """
        if not self.cnf_client:
            return None

        try:
            # Search CNF API
            results = self.cnf_client.search_food(label)
            if results:
                # Get nutrition data for first result
                food_code = results[0]["food_code"]
                nutrition = self.cnf_client.get_nutrition(food_code)
                if nutrition:
                    # Format to match our schema
                    return {
                        "name": results[0]["description"].lower(),
                        "calories": nutrition.get("energy_kcal", 0),
                        "protein": nutrition.get("protein_g", 0),
                        "carbs": nutrition.get("carbohydrate_g", 0),
                        "fat": nutrition.get("fat_g", 0),
                        "fiber": nutrition.get("fibre_g", 0),
                        "sugar": nutrition.get("sugars_g", 0),
                        "category": category,
                    }
        except Exception as e:
            logger.error(f"CNF API search failed for '{label}': {e}")

        return None

    def _search_usda_api(self, label: str, category: str) -> Optional[Dict]:
        """
        Search USDA API for matching food.

        Args:
            label: Vision API label
            category: Food category

        Returns:
            Matching food dictionary or None
        """
        if not self.usda_client:
            return None

        try:
            # Search USDA API
            results = self.usda_client.search_food(label)
            if results:
                # Get nutrition data for first result
                fdc_id = results[0]["fdcId"]
                nutrition = self.usda_client.get_nutrition(fdc_id)
                if nutrition:
                    # Format to match our schema
                    return {
                        "name": results[0]["description"].lower(),
                        "calories": nutrition.get("energy_kcal", 0),
                        "protein": nutrition.get("protein_g", 0),
                        "carbs": nutrition.get("carbohydrate_g", 0),
                        "fat": nutrition.get("fat_g", 0),
                        "fiber": nutrition.get("fiber_g", 0),
                        "sugar": nutrition.get("sugar_g", 0),
                        "category": category,
                    }
        except Exception as e:
            logger.error(f"USDA API search failed for '{label}': {e}")

        return None

    def assign_serving_size(self, food_name: str, category: str) -> int:
        """
        Assign appropriate serving size based on food category.

        Args:
            food_name: Name of the food
            category: Food category (protein, grain, fruit, vegetable, dairy, other)

        Returns:
            Serving size in grams
        """
        serving_size = STANDARD_SERVING_SIZES.get(category, 100)
        logger.info(
            f"Assigned {serving_size}g serving size to '{food_name}' (category: {category})"
        )
        return serving_size

    def process_vision_result(self, vision_result: Dict) -> Optional[Dict]:
        """
        Process a single Vision API detection result into a meal component.

        Args:
            vision_result: Vision API detection dict with label, confidence, category

        Returns:
            Meal component dict ready for nutrition calculation, or None if no match:
            {
                "name": "grilled chicken breast",
                "grams": 85,
                "category": "protein",
                "source": "local",
                "confidence": 0.94
            }
        """
        label = vision_result["label"]
        category = vision_result["category"]
        confidence = vision_result["confidence"]

        # Map label to specific food
        food = self.map_label_to_food(label, category)
        if not food:
            return None

        # Assign serving size
        serving_size = self.assign_serving_size(food["name"], category)

        return {
            "name": food["name"],
            "grams": serving_size,
            "category": category,
            "source": food.get("source", "unknown"),
            "confidence": confidence,
        }
