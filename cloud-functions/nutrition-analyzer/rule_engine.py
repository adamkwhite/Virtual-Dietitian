"""
Tiered rule engine for nutrition insights.
Implements 3 types of deterministic business rules.
"""

from typing import Dict, List


class Rule:
    """
    Base class for nutrition rules.

    Each rule evaluates nutrition data and returns an insight if triggered.
    This is DETERMINISTIC logic - same input always produces same output.
    No LLM involved in rule evaluation.
    """

    def __init__(self, rule_type: str):
        """
        Args:
            rule_type: Type of rule ('category', 'threshold', 'recommendation')
        """
        self.rule_type = rule_type

    def evaluate(
        self, total_nutrition: Dict, macro_percentages: Dict, food_categories: List[str]
    ) -> Dict[str, str]:
        """
        Evaluate rule against nutrition data.

        Args:
            total_nutrition: Aggregated nutrients {calories, protein_g, ...}
            macro_percentages: {protein_pct, carbs_pct, fat_pct}
            food_categories: ['grain', 'fruit', ...] from foods in meal

        Returns:
            Insight dict with 'type' and 'message', or None if rule doesn't trigger
        """
        raise NotImplementedError("Subclasses must implement evaluate()")


# ============================================================================
# RULE TYPE 1: CATEGORY DETECTION
# ============================================================================


class CategoryRule(Rule):
    """
    Category-based insights.

    How it works:
    - Check if specific food category is present in meal
    - If found, provide relevant nutritional insight

    Examples:
    - Fruit → "Great source of Vitamin C and antioxidants"
    - Grain → "Good source of fiber for digestive health"
    """

    def __init__(self, category: str, message: str, insight_type: str = "benefit"):
        """
        Args:
            category: Food category to detect ('fruit', 'grain', 'vegetable', etc.)
            message: Insight message to display if category found
            insight_type: Type of insight ('benefit', 'info')
        """
        super().__init__("category")
        self.category = category
        self.message = message
        self.insight_type = insight_type

    def evaluate(
        self, total_nutrition: Dict, macro_percentages: Dict, food_categories: List[str]
    ) -> Dict[str, str]:
        """Check if target category is in the meal."""
        if self.category in food_categories:
            return {"type": self.insight_type, "message": self.message}
        return None


# ============================================================================
# RULE TYPE 2: THRESHOLD WARNINGS
# ============================================================================


class ThresholdRule(Rule):
    """
    Nutrient threshold warnings.

    How it works:
    - Check if a specific nutrient exceeds (or falls below) a threshold
    - If condition met, provide warning or recommendation

    Examples:
    - Sodium > 800mg → "This meal is high in sodium"
    - Fiber < 5g → "Consider adding more fiber-rich foods"
    """

    def __init__(
        self,
        nutrient: str,
        threshold: float,
        operator: str,
        message: str,
        insight_type: str = "warning",
    ):
        """
        Args:
            nutrient: Nutrient key from total_nutrition ('sodium_mg', 'fiber_g', etc.)
            threshold: Threshold value to compare against
            operator: Comparison operator ('>', '<', '>=', '<=')
            message: Warning/recommendation message
            insight_type: Type of insight ('warning', 'caution')
        """
        super().__init__("threshold")
        self.nutrient = nutrient
        self.threshold = threshold
        self.operator = operator
        self.message = message
        self.insight_type = insight_type

    def evaluate(
        self, total_nutrition: Dict, macro_percentages: Dict, food_categories: List[str]
    ) -> Dict[str, str]:
        """Check if nutrient meets threshold condition."""
        nutrient_value = total_nutrition.get(self.nutrient, 0)

        # Evaluate condition based on operator
        triggered = False
        if self.operator == ">":
            triggered = nutrient_value > self.threshold
        elif self.operator == "<":
            triggered = nutrient_value < self.threshold
        elif self.operator == ">=":
            triggered = nutrient_value >= self.threshold
        elif self.operator == "<=":
            triggered = nutrient_value <= self.threshold

        if triggered:
            return {"type": self.insight_type, "message": self.message}
        return None


# ============================================================================
# RULE TYPE 3: MACRO RATIO RECOMMENDATIONS
# ============================================================================


class MacroRatioRule(Rule):
    """
    Macronutrient ratio recommendations.

    How it works:
    - Check if protein/carbs/fat percentage is outside healthy range
    - Provide actionable recommendation to improve balance

    Examples:
    - Protein < 15% → "Consider adding protein (chicken, eggs, tofu)"
    - Fat > 35% → "Consider reducing high-fat foods"

    Healthy ranges (from USDA Dietary Guidelines):
    - Protein: 15-35% of total calories
    - Carbs: 45-65% of total calories
    - Fat: 20-35% of total calories
    """

    def __init__(
        self, macro: str, min_pct: float, max_pct: float, below_message: str, above_message: str
    ):
        """
        Args:
            macro: Macro type ('protein', 'carbs', 'fat')
            min_pct: Minimum healthy percentage
            max_pct: Maximum healthy percentage
            below_message: Recommendation if below min
            above_message: Recommendation if above max
        """
        super().__init__("macro_ratio")
        self.macro = macro
        self.min_pct = min_pct
        self.max_pct = max_pct
        self.below_message = below_message
        self.above_message = above_message

    def evaluate(
        self, total_nutrition: Dict, macro_percentages: Dict, food_categories: List[str]
    ) -> Dict[str, str]:
        """Check if macro percentage is outside healthy range."""
        macro_key = f"{self.macro}_pct"
        macro_value = macro_percentages.get(macro_key, 0)

        if macro_value < self.min_pct:
            return {"type": "recommendation", "message": self.below_message}
        elif macro_value > self.max_pct:
            return {"type": "recommendation", "message": self.above_message}

        return None


# ============================================================================
# RULE DEFINITIONS & APPLICATION
# ============================================================================

# Define all rules that will be evaluated
RULES = [
    # Category Detection Rules
    CategoryRule(
        category="fruit",
        message="Excellent source of Vitamin C and antioxidants",
        insight_type="benefit",
    ),
    CategoryRule(
        category="grain",
        message="Good source of fiber for digestive health",
        insight_type="benefit",
    ),
    CategoryRule(
        category="vegetable",
        message="Rich in vitamins, minerals, and antioxidants",
        insight_type="benefit",
    ),
    # Threshold Warning Rules
    ThresholdRule(
        nutrient="sodium_mg",
        threshold=800,
        operator=">",
        message=(
            "This meal is high in sodium. Consider reducing salt or "
            "choosing lower-sodium options."
        ),
        insight_type="warning",
    ),
    ThresholdRule(
        nutrient="fiber_g",
        threshold=5,
        operator="<",
        message=(
            "This meal is low in fiber. Consider adding vegetables, " "fruits, or whole grains."
        ),
        insight_type="recommendation",
    ),
    # Macro Ratio Recommendation Rules
    MacroRatioRule(
        macro="protein",
        min_pct=15,
        max_pct=35,
        below_message=(
            "Consider adding more protein (chicken, fish, eggs, tofu, beans) "
            "to reach 15-35% of calories."
        ),
        above_message=(
            "This meal is very high in protein. Consider balancing with more "
            "carbs or healthy fats."
        ),
    ),
    MacroRatioRule(
        macro="fat",
        min_pct=20,
        max_pct=35,
        below_message=(
            "Consider adding healthy fats (avocado, nuts, olive oil) "
            "to reach 20-35% of calories."
        ),
        above_message=(
            "This meal is high in fat. Consider choosing leaner proteins or " "reducing added fats."
        ),
    ),
]


def apply_rules(
    total_nutrition: Dict, macro_percentages: Dict, food_categories: List[str]
) -> List[Dict[str, str]]:
    """
    Apply all rules to nutrition data and collect insights.

    How it works:
    1. Loop through all defined rules
    2. Evaluate each rule against the nutrition data
    3. Collect all insights that trigger (rules return non-None)
    4. Return list of insights

    Args:
        total_nutrition: Aggregated nutrients from calculator
        macro_percentages: Macro % from calculator
        food_categories: Food categories from calculator

    Returns:
        List of insight dicts: [{'type': 'benefit', 'message': '...'}, ...]

    Example output:
        [
            {'type': 'benefit', 'message': 'Excellent source of Vitamin C...'},
            {'type': 'recommendation', 'message': 'Consider adding more protein...'}
        ]
    """
    insights = []

    for rule in RULES:
        # Evaluate rule - returns insight dict or None
        insight = rule.evaluate(total_nutrition, macro_percentages, food_categories)

        # If rule triggered, add insight to results
        if insight:
            insights.append(insight)

    return insights
