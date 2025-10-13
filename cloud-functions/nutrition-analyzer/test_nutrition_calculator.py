"""
Unit tests for nutrition_calculator.py
Tests nutrient aggregation, macro calculations, and database lookups.
"""

from nutrition_calculator import calculate_macro_percentages, calculate_nutrition, find_food


class TestFindFood:
    """Test food lookup functionality."""

    def test_find_food_by_name(self):
        """Test finding food by exact name."""
        food = find_food("Chicken Breast")
        assert food is not None
        assert food["name"] == "Chicken Breast"
        assert food["category"] == "protein"

    def test_find_food_by_alias(self):
        """Test finding food by alias."""
        food = find_food("chicken")
        assert food is not None
        assert food["name"] == "Chicken Breast"

    def test_find_food_case_insensitive(self):
        """Test case-insensitive search."""
        food1 = find_food("CHICKEN")
        food2 = find_food("chicken")
        food3 = find_food("Chicken")
        assert food1 == food2 == food3

    def test_find_food_not_found(self):
        """Test handling of unknown foods."""
        food = find_food("pizza")  # Not in our 47-food database
        assert food is None


class TestCalculateNutrition:
    """Test nutrition calculation and aggregation."""

    def test_single_food(self):
        """Test calculation with single food item."""
        result = calculate_nutrition([{"name": "oatmeal", "quantity": 1}])

        assert result["total_nutrition"]["calories"] == 150
        assert result["total_nutrition"]["protein_g"] == 5
        assert result["total_nutrition"]["carbs_g"] == 27
        assert result["total_nutrition"]["fat_g"] == 3
        assert "grain" in result["food_categories"]

    def test_multiple_foods(self):
        """Test calculation with multiple food items."""
        result = calculate_nutrition(
            [
                {"name": "oatmeal", "quantity": 1},
                {"name": "blueberries", "quantity": 1},
                {"name": "almond butter", "quantity": 1},
            ]
        )

        # Oatmeal: 150 cal, Blueberries: 84 cal, Almond butter: 98 cal
        # Total: 332 calories
        assert result["total_nutrition"]["calories"] == 332
        assert "grain" in result["food_categories"]
        assert "fruit" in result["food_categories"]
        assert "fat" in result["food_categories"]

    def test_quantity_multiplier(self):
        """Test calculation with quantity multipliers."""
        result = calculate_nutrition([{"name": "chicken breast", "quantity": 2}])  # 2 servings

        # Chicken: 165 cal per serving * 2 = 330 cal
        assert result["total_nutrition"]["calories"] == 330
        assert result["total_nutrition"]["protein_g"] == 62  # 31 * 2

    def test_fractional_quantity(self):
        """Test calculation with fractional quantities."""
        result = calculate_nutrition([{"name": "blueberries", "quantity": 0.5}])  # Half serving

        # Blueberries: 84 cal * 0.5 = 42 cal
        assert result["total_nutrition"]["calories"] == 42

    def test_unknown_food_handling(self):
        """Test graceful handling of unknown foods."""
        result = calculate_nutrition(
            [{"name": "chicken", "quantity": 1}, {"name": "pizza", "quantity": 1}]  # Unknown food
        )

        # Should calculate chicken, skip pizza
        assert result["total_nutrition"]["calories"] == 165
        assert "pizza" in result["unknown_foods"]
        assert "warning" in result

    def test_macro_percentages_calculated(self):
        """Test that macro percentages are included in result."""
        result = calculate_nutrition([{"name": "chicken breast", "quantity": 1}])

        assert "macro_percentages" in result
        assert "protein_pct" in result["macro_percentages"]
        assert "carbs_pct" in result["macro_percentages"]
        assert "fat_pct" in result["macro_percentages"]


class TestCalculateMacroPercentages:
    """Test macro percentage calculations."""

    def test_macro_percentages_balanced_meal(self):
        """Test macro calculation for balanced meal."""
        # 25g protein (100 cal), 50g carbs (200 cal), 20g fat (180 cal)
        # Total: 480 cal
        result = calculate_macro_percentages(25, 50, 20)

        assert result["protein_pct"] == 21  # 100/480 = 20.8% → 21%
        assert result["carbs_pct"] == 42  # 200/480 = 41.7% → 42%
        assert result["fat_pct"] == 38  # 180/480 = 37.5% → 38%

    def test_macro_percentages_high_protein(self):
        """Test macro calculation for high-protein meal."""
        # 50g protein (200 cal), 10g carbs (40 cal), 5g fat (45 cal)
        # Total: 285 cal
        result = calculate_macro_percentages(50, 10, 5)

        assert result["protein_pct"] == 70  # High protein percentage
        assert result["carbs_pct"] == 14
        assert result["fat_pct"] == 16

    def test_macro_percentages_zero_values(self):
        """Test macro calculation with zero totals."""
        result = calculate_macro_percentages(0, 0, 0)

        assert result["protein_pct"] == 0
        assert result["carbs_pct"] == 0
        assert result["fat_pct"] == 0

    def test_macro_percentages_sum_to_100(self):
        """Test that percentages sum to approximately 100%."""
        result = calculate_macro_percentages(30, 40, 15)

        # Due to rounding, sum should be close to 100
        total = result["protein_pct"] + result["carbs_pct"] + result["fat_pct"]
        assert 99 <= total <= 101  # Allow 1% rounding variance


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_food_list(self):
        """Test with empty food list."""
        result = calculate_nutrition([])

        assert result["total_nutrition"]["calories"] == 0
        assert result["macro_percentages"]["protein_pct"] == 0

    def test_missing_quantity_defaults_to_one(self):
        """Test that missing quantity defaults to 1."""
        result = calculate_nutrition([{"name": "chicken"}])  # No quantity specified

        assert result["total_nutrition"]["calories"] == 165  # 1 serving

    def test_all_unknown_foods(self):
        """Test with all unknown foods."""
        result = calculate_nutrition([{"name": "pizza"}, {"name": "burger"}])

        assert result["total_nutrition"]["calories"] == 0
        assert len(result["unknown_foods"]) == 2
        assert "warning" in result
