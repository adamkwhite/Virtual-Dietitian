"""
Unit tests for food label mapping and serving size assignment.

Tests use mocked CNF/USDA API clients to avoid actual API calls during testing.
"""

from unittest.mock import Mock

import pytest
from food_label_mapper import CATEGORY_KEYWORDS, STANDARD_SERVING_SIZES, FoodLabelMapper


@pytest.fixture
def sample_nutrition_db():
    """Sample nutrition database for testing."""
    return [
        {
            "name": "grilled chicken breast",
            "calories": 165,
            "protein": 31,
            "carbs": 0,
            "fat": 3.6,
            "category": "protein",
        },
        {
            "name": "brown rice",
            "calories": 112,
            "protein": 2.6,
            "carbs": 24,
            "fat": 0.9,
            "category": "grain",
        },
        {
            "name": "broccoli",
            "calories": 55,
            "protein": 3.7,
            "carbs": 11,
            "fat": 0.6,
            "category": "vegetable",
        },
        {
            "name": "strawberries",
            "calories": 49,
            "protein": 1,
            "carbs": 12,
            "fat": 0.5,
            "category": "fruit",
        },
    ]


@pytest.fixture
def mapper(sample_nutrition_db):
    """Fixture to create FoodLabelMapper instance."""
    return FoodLabelMapper(nutrition_db=sample_nutrition_db)


@pytest.fixture
def mapper_with_apis(sample_nutrition_db):
    """Fixture to create FoodLabelMapper with mocked API clients."""
    mock_cnf = Mock()
    mock_usda = Mock()
    return FoodLabelMapper(
        nutrition_db=sample_nutrition_db, cnf_client=mock_cnf, usda_client=mock_usda
    )


class TestStandardServingSizes:
    """Test standard serving sizes dictionary."""

    def test_all_categories_have_serving_sizes(self):
        """Test that all expected categories have serving sizes defined."""
        expected_categories = ["protein", "grain", "fruit", "vegetable", "dairy", "other"]
        for category in expected_categories:
            assert category in STANDARD_SERVING_SIZES
            assert STANDARD_SERVING_SIZES[category] > 0

    def test_serving_sizes_are_reasonable(self):
        """Test that serving sizes are in reasonable ranges (20-300g)."""
        for category, size in STANDARD_SERVING_SIZES.items():
            assert 20 <= size <= 300, f"{category} serving size {size}g is unreasonable"


class TestCategoryKeywords:
    """Test category keyword mappings."""

    def test_all_categories_have_keywords(self):
        """Test that major categories have keyword lists."""
        expected_categories = ["protein", "grain", "fruit", "vegetable", "dairy"]
        for category in expected_categories:
            assert category in CATEGORY_KEYWORDS
            assert len(CATEGORY_KEYWORDS[category]) > 0


class TestFoodLabelMapper:
    """Test suite for FoodLabelMapper class."""

    def test_init_local_db_only(self, sample_nutrition_db):
        """Test initialization with local database only."""
        mapper = FoodLabelMapper(nutrition_db=sample_nutrition_db)
        assert mapper.nutrition_db == sample_nutrition_db
        assert mapper.cnf_client is None
        assert mapper.usda_client is None

    def test_init_with_api_clients(self, sample_nutrition_db):
        """Test initialization with API clients."""
        mock_cnf = Mock()
        mock_usda = Mock()
        mapper = FoodLabelMapper(
            nutrition_db=sample_nutrition_db, cnf_client=mock_cnf, usda_client=mock_usda
        )
        assert mapper.cnf_client == mock_cnf
        assert mapper.usda_client == mock_usda

    def test_search_local_db_exact_match(self, mapper):
        """Test exact match (case-insensitive) in local database."""
        result = mapper._search_local_db("Grilled Chicken Breast", "protein")
        assert result is not None
        assert result["name"] == "grilled chicken breast"
        assert result["category"] == "protein"

    def test_search_local_db_contains_match(self, mapper):
        """Test contains match (label in food name)."""
        result = mapper._search_local_db("chicken", "protein")
        assert result is not None
        assert "chicken" in result["name"]
        assert result["category"] == "protein"

    def test_search_local_db_reverse_contains_match(self, mapper):
        """Test reverse contains match (food name in label)."""
        result = mapper._search_local_db("grilled chicken breast salad", "protein")
        assert result is not None
        assert result["name"] == "grilled chicken breast"

    def test_search_local_db_category_keyword_match(self, mapper):
        """Test category-based keyword matching."""
        # Label "Poultry dish" contains keyword "poultry" → should match first protein
        result = mapper._search_local_db("Poultry dish", "protein")
        assert result is not None
        assert result["category"] == "protein"

    def test_search_local_db_no_match(self, mapper):
        """Test when no match is found in local database."""
        result = mapper._search_local_db("pizza", "other")
        assert result is None

    def test_map_label_to_food_local_match(self, mapper):
        """Test mapping label to food with local database match."""
        result = mapper.map_label_to_food("chicken", "protein")
        assert result is not None
        assert result["name"] == "grilled chicken breast"
        assert result["source"] == "local"

    def test_map_label_to_food_cnf_fallback(self, mapper_with_apis):
        """Test CNF API fallback when local database has no match."""
        # Mock CNF API response
        mapper_with_apis.cnf_client.search_food = Mock(
            return_value=[{"food_code": "123", "description": "Cheddar Cheese"}]
        )
        mapper_with_apis.cnf_client.get_nutrition = Mock(
            return_value={
                "energy_kcal": 403,
                "protein_g": 25,
                "carbohydrate_g": 1.3,
                "fat_g": 33,
                "fibre_g": 0,
                "sugars_g": 0.5,
            }
        )

        result = mapper_with_apis.map_label_to_food("cheddar cheese", "dairy")
        assert result is not None
        assert result["name"] == "cheddar cheese"
        assert result["source"] == "cnf"
        assert result["calories"] == 403
        assert result["protein"] == 25

    def test_map_label_to_food_usda_fallback(self, mapper_with_apis):
        """Test USDA API fallback when CNF API has no match."""
        # Mock CNF API returning no results
        mapper_with_apis.cnf_client.search_food = Mock(return_value=[])

        # Mock USDA API response
        mapper_with_apis.usda_client.search_food = Mock(
            return_value=[{"fdcId": 456, "description": "Pizza, cheese"}]
        )
        mapper_with_apis.usda_client.get_nutrition = Mock(
            return_value={
                "energy_kcal": 266,
                "protein_g": 11,
                "carbohydrate_g": 33,
                "fat_g": 10,
                "fiber_g": 2.5,
                "sugar_g": 3.8,
            }
        )

        result = mapper_with_apis.map_label_to_food("pizza", "other")
        assert result is not None
        assert result["name"] == "pizza, cheese"
        assert result["source"] == "usda"
        assert result["calories"] == 266

    def test_map_label_to_food_no_match(self, mapper):
        """Test when no match is found in any source."""
        result = mapper.map_label_to_food("unknown exotic food", "other")
        assert result is None

    def test_map_label_to_food_cnf_api_error(self, mapper_with_apis):
        """Test graceful handling of CNF API errors."""
        # Mock CNF API throwing exception
        mapper_with_apis.cnf_client.search_food = Mock(side_effect=Exception("API error"))

        # Should fall back to USDA
        mapper_with_apis.usda_client.search_food = Mock(
            return_value=[{"fdcId": 789, "description": "Mango"}]
        )
        mapper_with_apis.usda_client.get_nutrition = Mock(
            return_value={
                "energy_kcal": 60,
                "protein_g": 0.8,
                "carbohydrate_g": 15,
                "fat_g": 0.4,
                "fiber_g": 1.6,
                "sugar_g": 14,
            }
        )

        result = mapper_with_apis.map_label_to_food("mango", "other")
        assert result is not None
        assert result["source"] == "usda"

    def test_assign_serving_size_protein(self, mapper):
        """Test serving size assignment for protein category."""
        size = mapper.assign_serving_size("chicken", "protein")
        assert size == 85

    def test_assign_serving_size_grain(self, mapper):
        """Test serving size assignment for grain category."""
        size = mapper.assign_serving_size("rice", "grain")
        assert size == 50

    def test_assign_serving_size_fruit(self, mapper):
        """Test serving size assignment for fruit category."""
        size = mapper.assign_serving_size("apple", "fruit")
        assert size == 150

    def test_assign_serving_size_vegetable(self, mapper):
        """Test serving size assignment for vegetable category."""
        size = mapper.assign_serving_size("broccoli", "vegetable")
        assert size == 85

    def test_assign_serving_size_dairy(self, mapper):
        """Test serving size assignment for dairy category."""
        size = mapper.assign_serving_size("milk", "dairy")
        assert size == 240

    def test_assign_serving_size_other(self, mapper):
        """Test serving size assignment for other category."""
        size = mapper.assign_serving_size("soup", "other")
        assert size == 100

    def test_assign_serving_size_unknown_category(self, mapper):
        """Test serving size assignment for unknown category (defaults to 'other')."""
        size = mapper.assign_serving_size("mystery food", "unknown_category")
        assert size == 100  # Should default to 'other'

    def test_process_vision_result_success(self, mapper):
        """Test processing Vision API result into meal component."""
        vision_result = {
            "label": "Chicken",
            "confidence": 0.94,
            "category": "protein",
        }

        result = mapper.process_vision_result(vision_result)
        assert result is not None
        assert result["name"] == "grilled chicken breast"
        assert result["grams"] == 85
        assert result["category"] == "protein"
        assert result["source"] == "local"
        assert result["confidence"] == 0.94

    def test_process_vision_result_no_match(self, mapper):
        """Test processing Vision API result when no food match found."""
        vision_result = {
            "label": "Unknown food item",
            "confidence": 0.75,
            "category": "other",
        }

        result = mapper.process_vision_result(vision_result)
        assert result is None

    def test_process_vision_result_with_cnf_match(self, mapper_with_apis):
        """Test processing Vision API result with CNF API match."""
        # Mock CNF API response
        mapper_with_apis.cnf_client.search_food = Mock(
            return_value=[{"food_code": "999", "description": "Yogurt, plain"}]
        )
        mapper_with_apis.cnf_client.get_nutrition = Mock(
            return_value={
                "energy_kcal": 61,
                "protein_g": 3.5,
                "carbohydrate_g": 4.7,
                "fat_g": 3.3,
                "fibre_g": 0,
                "sugars_g": 4.7,
            }
        )

        vision_result = {
            "label": "Yogurt",
            "confidence": 0.89,
            "category": "dairy",
        }

        result = mapper_with_apis.process_vision_result(vision_result)
        assert result is not None
        assert result["name"] == "yogurt, plain"
        assert result["grams"] == 240  # Dairy serving size
        assert result["source"] == "cnf"

    def test_search_cnf_api_none_client(self, mapper):
        """Test CNF API search when client is None."""
        result = mapper._search_cnf_api("cheese", "dairy")
        assert result is None

    def test_search_usda_api_none_client(self, mapper):
        """Test USDA API search when client is None."""
        result = mapper._search_usda_api("pizza", "other")
        assert result is None
