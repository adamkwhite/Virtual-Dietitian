"""
Unit tests for rule_engine.py
Tests all 3 rule types: Category, Threshold, and Macro Ratio rules.
"""

from rule_engine import CategoryRule, MacroRatioRule, ThresholdRule, apply_rules


class TestCategoryRule:
    """Test Rule Type 1: Category Detection."""

    def test_category_rule_triggers_when_present(self):
        """Test that category rule triggers when category is in meal."""
        rule = CategoryRule(
            category="fruit", message="Great source of vitamins", insight_type="benefit"
        )

        total_nutrition = {"calories": 100}
        macro_percentages = {}
        food_categories = ["fruit", "grain"]

        result = rule.evaluate(total_nutrition, macro_percentages, food_categories)

        assert result is not None
        assert result["type"] == "benefit"
        assert result["message"] == "Great source of vitamins"

    def test_category_rule_not_triggered_when_absent(self):
        """Test that category rule doesn't trigger when category absent."""
        rule = CategoryRule(
            category="fruit", message="Great source of vitamins", insight_type="benefit"
        )

        total_nutrition = {"calories": 100}
        macro_percentages = {}
        food_categories = ["protein", "grain"]  # No fruit

        result = rule.evaluate(total_nutrition, macro_percentages, food_categories)

        assert result is None

    def test_category_rule_multiple_categories(self):
        """Test category detection with multiple categories."""
        rule = CategoryRule(category="vegetable", message="Rich in nutrients")

        food_categories = ["protein", "vegetable", "grain"]

        result = rule.evaluate({}, {}, food_categories)

        assert result is not None
        assert "Rich in nutrients" in result["message"]


class TestThresholdRule:
    """Test Rule Type 2: Threshold Warnings."""

    def test_threshold_greater_than_triggers(self):
        """Test threshold rule with > operator."""
        rule = ThresholdRule(
            nutrient="sodium_mg",
            threshold=800,
            operator=">",
            message="High sodium warning",
            insight_type="warning",
        )

        total_nutrition = {"sodium_mg": 850}  # Above threshold
        result = rule.evaluate(total_nutrition, {}, [])

        assert result is not None
        assert result["type"] == "warning"
        assert "High sodium" in result["message"]

    def test_threshold_greater_than_not_triggered(self):
        """Test threshold rule doesn't trigger when below threshold."""
        rule = ThresholdRule(
            nutrient="sodium_mg", threshold=800, operator=">", message="High sodium warning"
        )

        total_nutrition = {"sodium_mg": 700}  # Below threshold
        result = rule.evaluate(total_nutrition, {}, [])

        assert result is None

    def test_threshold_less_than_triggers(self):
        """Test threshold rule with < operator."""
        rule = ThresholdRule(
            nutrient="fiber_g",
            threshold=5,
            operator="<",
            message="Low fiber",
            insight_type="recommendation",
        )

        total_nutrition = {"fiber_g": 3}  # Below threshold
        result = rule.evaluate(total_nutrition, {}, [])

        assert result is not None
        assert result["type"] == "recommendation"
        assert "Low fiber" in result["message"]

    def test_threshold_greater_equal(self):
        """Test threshold rule with >= operator."""
        rule = ThresholdRule(
            nutrient="calories", threshold=500, operator=">=", message="High calorie meal"
        )

        # Test exactly equal
        total_nutrition = {"calories": 500}
        result = rule.evaluate(total_nutrition, {}, [])
        assert result is not None

        # Test greater
        total_nutrition = {"calories": 600}
        result = rule.evaluate(total_nutrition, {}, [])
        assert result is not None

        # Test less
        total_nutrition = {"calories": 400}
        result = rule.evaluate(total_nutrition, {}, [])
        assert result is None

    def test_threshold_less_equal(self):
        """Test threshold rule with <= operator."""
        rule = ThresholdRule(nutrient="fat_g", threshold=10, operator="<=", message="Low fat meal")

        # Test exactly equal
        total_nutrition = {"fat_g": 10}
        result = rule.evaluate(total_nutrition, {}, [])
        assert result is not None

        # Test less
        total_nutrition = {"fat_g": 5}
        result = rule.evaluate(total_nutrition, {}, [])
        assert result is not None

        # Test greater
        total_nutrition = {"fat_g": 15}
        result = rule.evaluate(total_nutrition, {}, [])
        assert result is None


class TestMacroRatioRule:
    """Test Rule Type 3: Macro Ratio Recommendations."""

    def test_macro_below_minimum(self):
        """Test macro rule triggers when below minimum."""
        rule = MacroRatioRule(
            macro="protein",
            min_pct=15,
            max_pct=35,
            below_message="Add more protein",
            above_message="Too much protein",
        )

        macro_percentages = {"protein_pct": 12}  # Below 15%
        result = rule.evaluate({}, macro_percentages, [])

        assert result is not None
        assert result["type"] == "recommendation"
        assert result["message"] == "Add more protein"

    def test_macro_above_maximum(self):
        """Test macro rule triggers when above maximum."""
        rule = MacroRatioRule(
            macro="fat",
            min_pct=20,
            max_pct=35,
            below_message="Add more fat",
            above_message="Too much fat",
        )

        macro_percentages = {"fat_pct": 40}  # Above 35%
        result = rule.evaluate({}, macro_percentages, [])

        assert result is not None
        assert result["type"] == "recommendation"
        assert result["message"] == "Too much fat"

    def test_macro_within_range(self):
        """Test macro rule doesn't trigger when in healthy range."""
        rule = MacroRatioRule(
            macro="protein",
            min_pct=15,
            max_pct=35,
            below_message="Add more protein",
            above_message="Too much protein",
        )

        macro_percentages = {"protein_pct": 25}  # Within 15-35%
        result = rule.evaluate({}, macro_percentages, [])

        assert result is None

    def test_macro_at_boundary_values(self):
        """Test macro rule at exact boundary values."""
        rule = MacroRatioRule(
            macro="carbs",
            min_pct=45,
            max_pct=65,
            below_message="Add carbs",
            above_message="Too many carbs",
        )

        # At minimum boundary (should not trigger)
        macro_percentages = {"carbs_pct": 45}
        result = rule.evaluate({}, macro_percentages, [])
        assert result is None

        # At maximum boundary (should not trigger)
        macro_percentages = {"carbs_pct": 65}
        result = rule.evaluate({}, macro_percentages, [])
        assert result is None


class TestApplyRules:
    """Test the apply_rules function with multiple rules."""

    def test_apply_rules_multiple_triggers(self):
        """Test that multiple rules can trigger for same meal."""
        total_nutrition = {
            "calories": 430,
            "protein_g": 13,
            "carbs_g": 52,
            "fat_g": 18,
            "sodium_mg": 150,
            "fiber_g": 8,
        }
        macro_percentages = {
            "protein_pct": 12,  # Below 15% (triggers protein rule)
            "carbs_pct": 48,
            "fat_pct": 40,  # Above 35% (triggers fat rule)
        }
        food_categories = ["fruit", "grain"]  # Triggers fruit + grain rules

        insights = apply_rules(total_nutrition, macro_percentages, food_categories)

        # Should have at least 4 insights:
        # - Fruit benefit
        # - Grain benefit
        # - Low protein recommendation
        # - High fat recommendation
        assert len(insights) >= 4

        insight_messages = [i["message"] for i in insights]
        assert any("Vitamin C" in msg or "antioxidants" in msg for msg in insight_messages)
        assert any("fiber" in msg for msg in insight_messages)
        assert any("protein" in msg for msg in insight_messages)

    def test_apply_rules_no_triggers(self):
        """Test apply_rules when no rules trigger."""
        total_nutrition = {"calories": 300, "sodium_mg": 200, "fiber_g": 10}  # Below 800  # Above 5
        macro_percentages = {
            "protein_pct": 25,  # Within 15-35%
            "carbs_pct": 50,  # Within 45-65% (if we had that rule)
            "fat_pct": 25,  # Within 20-35%
        }
        food_categories = ["protein"]  # Only protein, no fruit/grain/veg

        insights = apply_rules(total_nutrition, macro_percentages, food_categories)

        # Only protein category doesn't have a rule, so no insights
        # (our RULES list doesn't have protein category rule)
        # Macros are in range, thresholds not exceeded
        assert len(insights) == 0

    def test_apply_rules_high_sodium_meal(self):
        """Test apply_rules with high sodium meal."""
        total_nutrition = {"sodium_mg": 900}  # Above 800mg threshold
        macro_percentages = {}
        food_categories = []

        insights = apply_rules(total_nutrition, macro_percentages, food_categories)

        # Should have sodium warning
        assert any("sodium" in insight["message"].lower() for insight in insights)
        assert any(insight["type"] == "warning" for insight in insights)
