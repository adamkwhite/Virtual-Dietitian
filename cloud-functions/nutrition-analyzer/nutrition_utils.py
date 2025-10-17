"""
Shared utility functions for nutrition data processing.
Used by CNF and USDA API clients.
"""


def infer_food_category(nutrition: dict) -> str:
    """
    Infer food category based on nutritional profile.

    Categories match nutrition_db.json:
    - protein: High protein (>15g per 100g)
    - dairy: Calcium-rich (>100mg)
    - fat: High fat (>40g)
    - fruit: High vitamin C (>20mg)
    - vegetable: Low cal (<100 kcal) with fiber (>2g)
    - grain: High carbs (>50g)

    Args:
        nutrition: Dict with nutritional values per 100g

    Returns:
        Category string: "protein", "dairy", "fat", "fruit", "vegetable", or "grain"
    """
    protein = nutrition.get("protein_g", 0)
    carbs = nutrition.get("carbs_g", 0)
    fat = nutrition.get("fat_g", 0)
    fiber = nutrition.get("fiber_g", 0)
    vitamin_c = nutrition.get("vitamin_c_mg", 0)
    calcium = nutrition.get("calcium_mg", 0)
    calories = nutrition.get("calories", 0)

    # High protein (>15g per 100g)
    if protein > 15:
        return "protein"

    # High calcium (dairy)
    if calcium > 100:
        return "dairy"

    # High fat
    if fat > 40:
        return "fat"

    # High vitamin C (likely fruit)
    if vitamin_c > 20:
        return "fruit"

    # Low calorie with fiber (likely vegetable)
    if calories < 100 and fiber > 2:
        return "vegetable"

    # High carbs (likely grain)
    if carbs > 50:
        return "grain"

    # Default to vegetable for low-calorie items
    if calories < 50:
        return "vegetable"

    # Default
    return "grain"
