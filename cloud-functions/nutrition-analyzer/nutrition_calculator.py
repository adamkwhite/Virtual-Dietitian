"""
Nutrition calculation and aggregation logic.
Loads food database and calculates total nutritional values.
Supports fallback to USDA API when foods not in static database.
"""

import json
import os
from typing import Any

from config import Config


def load_nutrition_db():
    """
    Load nutrition database from JSON file.

    How it works:
    1. Gets database path from Config (env-aware: local or cloud)
    2. Loads JSON with 47 foods
    3. Creates a fast lookup dictionary:
       - Maps "chicken" -> full food data
       - Maps "grilled chicken" (alias) -> same food data
       - All keys are lowercase for case-insensitive matching

    Returns:
        Dict[str, Dict]: Lookup table mapping food names/aliases to food data
    """
    db_path = os.path.join(os.path.dirname(__file__), Config.NUTRITION_DB_PATH)

    with open(db_path) as f:
        data = json.load(f)

    # Build lookup dictionary for O(1) search
    lookup = {}
    for food in data["foods"]:
        # Primary name: "Chicken Breast" -> lowercase "chicken breast"
        lookup[food["name"].lower()] = food

        # Aliases: ["chicken", "grilled chicken"] -> all point to same food
        for alias in food.get("aliases", []):
            lookup[alias.lower()] = food

    return lookup


# Load database once globally (not on every request)
NUTRITION_DB = load_nutrition_db()


def find_food(
    food_name: str, use_cnf_fallback: bool = False, use_usda_fallback: bool = False
) -> dict[str, Any]:
    """
    Find food in database by name or alias.
    Supports 3-tier fallback: Local DB → CNF API → USDA API.

    How it works:
    - Tier 1: Converts input to lowercase and looks up in our 47-food dictionary (O(1))
    - Tier 2: If not found and use_cnf_fallback=True, queries CNF API (5,690 foods)
    - Tier 3: If not found and use_usda_fallback=True, queries USDA API (500,000+ foods)
    - Returns food data if found, None if not

    Args:
        food_name: Name of food (case-insensitive)
        use_cnf_fallback: If True, query CNF API when not in static DB
        use_usda_fallback: If True, query USDA API when not in static DB or CNF

    Returns:
        Food data dict with nutrition info, or None if not found

    Example:
        find_food("chicken") -> local DB result
        find_food("gouda", use_cnf_fallback=True) -> CNF API result
        find_food("exotic_fruit", use_cnf_fallback=True, use_usda_fallback=True) -> USDA result
    """
    # Tier 1: Static database (47 foods)
    static_result = NUTRITION_DB.get(food_name.lower())

    if static_result:
        return static_result

    # Tier 2: CNF API (5,690 foods)
    if use_cnf_fallback:
        try:
            from cnf_client import get_cnf_client

            cnf_client = get_cnf_client()
            nutrition_data = cnf_client.get_nutrition_per_100g(food_name)

            if nutrition_data:
                # Convert CNF format to our internal format
                return {
                    "id": f"cnf_{food_name.lower().replace(' ', '_')}",
                    "name": food_name.title(),
                    "category": nutrition_data["category"],
                    "nutrition": {
                        "calories": nutrition_data["calories"],
                        "protein_g": nutrition_data["protein_g"],
                        "carbs_g": nutrition_data["carbs_g"],
                        "fat_g": nutrition_data["fat_g"],
                        "fiber_g": nutrition_data["fiber_g"],
                        "sodium_mg": nutrition_data["sodium_mg"],
                        "vitamin_c_mg": nutrition_data["vitamin_c_mg"],
                        "iron_mg": nutrition_data["iron_mg"],
                        "calcium_mg": nutrition_data["calcium_mg"],
                    },
                    "source": "cnf",
                }
        except Exception as e:
            print(f"CNF API fallback failed for '{food_name}': {e}")

    # Tier 3: USDA API (500,000+ foods)
    if use_usda_fallback:
        try:
            from usda_client import get_usda_client

            usda_client = get_usda_client()
            nutrition_data = usda_client.get_nutrition_per_100g(food_name)

            if nutrition_data:
                # Convert USDA format to our internal format
                return {
                    "id": f"usda_{food_name.lower().replace(' ', '_')}",
                    "name": food_name.title(),
                    "category": nutrition_data["category"],
                    "nutrition": {
                        "calories": nutrition_data["calories"],
                        "protein_g": nutrition_data["protein_g"],
                        "carbs_g": nutrition_data["carbs_g"],
                        "fat_g": nutrition_data["fat_g"],
                        "fiber_g": nutrition_data["fiber_g"],
                        "sodium_mg": nutrition_data["sodium_mg"],
                        "vitamin_c_mg": nutrition_data["vitamin_c_mg"],
                        "iron_mg": nutrition_data["iron_mg"],
                        "calcium_mg": nutrition_data["calcium_mg"],
                    },
                    "source": "usda",
                }
        except Exception as e:
            print(f"USDA API fallback failed for '{food_name}': {e}")

    return None


def calculate_nutrition(
    food_items: list[dict[str, Any]],
    use_cnf_fallback: bool = False,
    use_usda_fallback: bool = False,
) -> dict[str, Any]:
    """
    Calculate total nutrition from list of food items.
    Supports 3-tier fallback: Local DB → CNF API → USDA API.

    How it works:
    1. Initialize totals to zero for all nutrients
    2. Loop through each food item
    3. Find food in database (tries local, CNF, USDA in order)
    4. Multiply nutrition by quantity and add to totals
    5. Calculate macro percentages
    6. Return complete nutrition analysis

    Args:
        food_items: List of dicts with 'name' and optional 'quantity' (default 1.0)
                   Example: [{"name": "oatmeal", "quantity": 1},
                            {"name": "blueberries", "quantity": 0.5}]
        use_cnf_fallback: If True, query CNF API when not in static DB
        use_usda_fallback: If True, query USDA API when not in static DB or CNF

    Returns:
        Dict with:
        - total_nutrition: {calories, protein_g, carbs_g, fat_g, fiber_g, ...}
        - macro_percentages: {protein_pct, carbs_pct, fat_pct}
        - food_categories: ['grain', 'fruit'] (for rule engine)
        - unknown_foods: ['pizza'] (if any not found)
    """
    # Initialize all nutrients to 0
    total_nutrition = {
        "calories": 0,
        "protein_g": 0,
        "carbs_g": 0,
        "fat_g": 0,
        "fiber_g": 0,
        "sodium_mg": 0,
        "vitamin_c_mg": 0,
        "iron_mg": 0,
        "calcium_mg": 0,
    }

    food_categories = []  # Track categories for rules (e.g., 'fruit' -> vitamin insight)
    unknown_foods = []  # Track foods not in our database

    # Process each food item
    for item in food_items:
        food_name = item.get("name", "")
        quantity = float(item.get("quantity", 1.0))  # Default to 1 serving

        # Look up food in database (with 3-tier fallback)
        food_data = find_food(
            food_name, use_cnf_fallback=use_cnf_fallback, use_usda_fallback=use_usda_fallback
        )

        if not food_data:
            # Food not found - track it and skip
            unknown_foods.append(food_name)
            continue

        # Track unique categories (for rule engine)
        if food_data["category"] not in food_categories:
            food_categories.append(food_data["category"])

        # Aggregate nutrition (multiply by quantity)
        # Example: 0.5 servings of blueberries = 0.5 * 84 calories = 42 calories
        nutrition = food_data["nutrition"]
        for nutrient_key in total_nutrition:
            total_nutrition[nutrient_key] += nutrition[nutrient_key] * quantity

    # Round all values to 1 decimal place for clean output
    for key in total_nutrition:
        total_nutrition[key] = round(total_nutrition[key], 1)

    # Calculate what % of calories come from protein/carbs/fat
    macro_percentages = calculate_macro_percentages(
        total_nutrition["protein_g"], total_nutrition["carbs_g"], total_nutrition["fat_g"]
    )

    # Build result
    result = {
        "total_nutrition": total_nutrition,
        "macro_percentages": macro_percentages,
        "food_categories": food_categories,
    }

    # Include warning if any foods weren't recognized
    if unknown_foods:
        result["unknown_foods"] = unknown_foods
        result["warning"] = f"Could not find nutrition data for: {', '.join(unknown_foods)}"

    return result


def calculate_macro_percentages(protein_g: float, carbs_g: float, fat_g: float) -> dict[str, int]:
    """
    Calculate percentage of calories from each macronutrient.

    How it works:
    1. Convert grams to calories using standard conversion:
       - Protein: 4 calories per gram
       - Carbs: 4 calories per gram
       - Fat: 9 calories per gram
    2. Calculate % of total calories from each macro
    3. Round to whole numbers

    Args:
        protein_g: Grams of protein
        carbs_g: Grams of carbohydrates
        fat_g: Grams of fat

    Returns:
        Dict with protein_pct, carbs_pct, fat_pct

    Example:
        Input: 13g protein, 52g carbs, 18g fat
        Calculation:
        - Protein calories: 13 * 4 = 52 cal
        - Carbs calories: 52 * 4 = 208 cal
        - Fat calories: 18 * 9 = 162 cal
        - Total: 422 cal
        Output: {protein_pct: 12, carbs_pct: 49, fat_pct: 38}
    """
    # Convert grams to calories
    protein_cal = protein_g * 4
    carbs_cal = carbs_g * 4
    fat_cal = fat_g * 9

    total_cal = protein_cal + carbs_cal + fat_cal

    # Handle edge case: no food (avoid division by zero)
    if total_cal == 0:
        return {"protein_pct": 0, "carbs_pct": 0, "fat_pct": 0}

    # Calculate percentages
    return {
        "protein_pct": round((protein_cal / total_cal) * 100),
        "carbs_pct": round((carbs_cal / total_cal) * 100),
        "fat_pct": round((fat_cal / total_cal) * 100),
    }
