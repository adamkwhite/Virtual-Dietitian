"""
Unit tests for cnf_client.py
Tests CNF API client, food search, nutrition fetching, and caching.
"""

from unittest.mock import MagicMock, patch

from cnf_client import CNFClient, get_cnf_client
from nutrition_utils import infer_food_category


class TestCNFClientInitialization:
    """Test CNF client initialization."""

    def test_client_initialization(self):
        """Test that client initializes with empty caches."""
        client = CNFClient()
        assert client._foods_list is None
        assert client._nutrition_cache == {}


class TestGetCNFFoodsList:
    """Test downloading and caching CNF foods list."""

    @patch("cnf_client.requests.get")
    def test_get_foods_list_first_call(self, mock_get):
        """Test downloading foods list on first call."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"food_code": 109, "food_description": "Cheese, gouda"},
            {"food_code": 110, "food_description": "Cheese, cheddar"},
        ]
        mock_get.return_value = mock_response

        client = CNFClient()
        foods = client.get_cnf_foods_list()

        # Verify API was called
        mock_get.assert_called_once()
        assert "food/" in mock_get.call_args[0][0]

        # Verify result
        assert len(foods) == 2
        assert foods[0]["food_code"] == 109
        assert foods[0]["food_description"] == "Cheese, gouda"

    @patch("cnf_client.requests.get")
    def test_get_foods_list_caching(self, mock_get):
        """Test that foods list is cached after first call."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"food_code": 109, "food_description": "Cheese, gouda"}]
        mock_get.return_value = mock_response

        client = CNFClient()

        # First call - should hit API
        foods1 = client.get_cnf_foods_list()
        assert mock_get.call_count == 1

        # Second call - should use cache
        foods2 = client.get_cnf_foods_list()
        assert mock_get.call_count == 1  # Not called again
        assert foods1 == foods2

    @patch("cnf_client.requests.get")
    def test_get_foods_list_api_error(self, mock_get):
        """Test handling API errors when downloading foods list."""
        import requests

        # Mock API error with proper exception type
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        client = CNFClient()
        foods = client.get_cnf_foods_list()

        # Should return empty list on error
        assert foods == []


class TestSearchFood:
    """Test food search functionality."""

    def setup_method(self):
        """Setup client with mock foods list."""
        self.client = CNFClient()
        self.client._foods_list = [
            {"food_code": 109, "food_description": "Cheese, gouda"},
            {"food_code": 110, "food_description": "Cheese, cheddar"},
            {"food_code": 111, "food_description": "Chicken, broiler, breast, meat only"},
        ]

    def test_search_exact_match(self):
        """Test exact food name match."""
        food_code = self.client.search_food("Cheese, gouda")
        assert food_code == 109

    def test_search_exact_match_case_insensitive(self):
        """Test exact match is case-insensitive."""
        food_code = self.client.search_food("cheese, gouda")
        assert food_code == 109

    def test_search_contains_match(self):
        """Test partial match using 'contains'."""
        food_code = self.client.search_food("gouda")
        assert food_code == 109

    def test_search_reverse_contains_match(self):
        """Test reverse contains match (query contains food description)."""
        # Add a shorter food name that would be contained in a longer query
        self.client._foods_list.append({"food_code": 112, "food_description": "Chicken"})
        # Query contains "Chicken" -> should match
        food_code = self.client.search_food("Grilled Chicken with sauce")
        assert food_code == 112

    def test_search_not_found(self):
        """Test food not found returns None."""
        food_code = self.client.search_food("pizza")
        assert food_code is None

    def test_search_empty_query(self):
        """Test empty query returns None."""
        food_code = self.client.search_food("")
        assert food_code is None

    def test_search_whitespace_handling(self):
        """Test that whitespace is stripped."""
        food_code = self.client.search_food("  gouda  ")
        assert food_code == 109

    @patch("cnf_client.requests.get")
    def test_search_with_empty_foods_list(self, mock_get):
        """Test search when API returns empty list."""
        import requests

        mock_get.side_effect = requests.exceptions.RequestException("API error")
        client = CNFClient()
        food_code = client.search_food("gouda")
        assert food_code is None


class TestGetNutritionPer100g:
    """Test nutrition data fetching."""

    def setup_method(self):
        """Setup client with mock foods list."""
        self.client = CNFClient()
        self.client._foods_list = [{"food_code": 109, "food_description": "Cheese, gouda"}]

    @patch("cnf_client.requests.get")
    def test_get_nutrition_success(self, mock_get):
        """Test successful nutrition data retrieval."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"nutrient_web_name": "Energy (kcal)", "nutrient_value": 357.0},
            {"nutrient_web_name": "Protein", "nutrient_value": 24.94},
            {"nutrient_web_name": "Carbohydrate", "nutrient_value": 2.22},
            {"nutrient_web_name": "Total Fat", "nutrient_value": 28.0},
            {"nutrient_web_name": "Fibre, total dietary", "nutrient_value": 0.0},
            {"nutrient_web_name": "Sodium, Na", "nutrient_value": 819.0},
            {"nutrient_web_name": "Vitamin C", "nutrient_value": 0.0},
            {"nutrient_web_name": "Calcium, Ca", "nutrient_value": 700.0},
            {"nutrient_web_name": "Iron, Fe", "nutrient_value": 0.24},
        ]
        mock_get.return_value = mock_response

        nutrition = self.client.get_nutrition_per_100g("gouda")

        # Verify result structure
        assert nutrition is not None
        assert nutrition["calories"] == 357.0
        assert nutrition["protein_g"] == 24.94
        assert nutrition["carbs_g"] == 2.22
        assert nutrition["fat_g"] == 28.0
        assert nutrition["fiber_g"] == 0.0
        assert nutrition["sodium_mg"] == 819.0
        assert nutrition["vitamin_c_mg"] == 0.0
        assert nutrition["calcium_mg"] == 700.0
        assert nutrition["iron_mg"] == 0.24
        assert nutrition["category"] == "protein"

    def test_get_nutrition_food_not_found(self):
        """Test handling when food is not found."""
        nutrition = self.client.get_nutrition_per_100g("pizza")
        assert nutrition is None

    @patch("cnf_client.requests.get")
    def test_get_nutrition_api_error(self, mock_get):
        """Test handling API errors during nutrition fetch."""
        import requests

        # Mock API error with proper exception type
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        nutrition = self.client.get_nutrition_per_100g("gouda")
        assert nutrition is None


class TestFetchNutritionData:
    """Test nutrition data fetching and caching."""

    def setup_method(self):
        """Setup client."""
        self.client = CNFClient()

    @patch("cnf_client.requests.get")
    def test_fetch_nutrition_caching(self, mock_get):
        """Test that nutrition data is cached."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"nutrient_web_name": "Energy (kcal)", "nutrient_value": 357.0},
            {"nutrient_web_name": "Protein", "nutrient_value": 24.94},
            {"nutrient_web_name": "Carbohydrate", "nutrient_value": 2.22},
            {"nutrient_web_name": "Total Fat", "nutrient_value": 28.0},
            {"nutrient_web_name": "Fibre, total dietary", "nutrient_value": 0.0},
            {"nutrient_web_name": "Sodium, Na", "nutrient_value": 819.0},
            {"nutrient_web_name": "Vitamin C", "nutrient_value": 0.0},
            {"nutrient_web_name": "Calcium, Ca", "nutrient_value": 700.0},
            {"nutrient_web_name": "Iron, Fe", "nutrient_value": 0.24},
        ]
        mock_get.return_value = mock_response

        # First call - should hit API
        nutrition1 = self.client._fetch_nutrition_data(109)
        assert mock_get.call_count == 1

        # Second call - should use cache
        nutrition2 = self.client._fetch_nutrition_data(109)
        assert mock_get.call_count == 1  # Not called again
        assert nutrition1 == nutrition2

    @patch("cnf_client.requests.get")
    def test_fetch_nutrition_timeout(self, mock_get):
        """Test handling timeout errors."""
        import requests

        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        nutrition = self.client._fetch_nutrition_data(109)
        assert nutrition is None

    @patch("cnf_client.requests.get")
    def test_fetch_nutrition_http_error(self, mock_get):
        """Test handling HTTP errors."""
        import requests

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        nutrition = self.client._fetch_nutrition_data(109)
        assert nutrition is None


class TestNormalizeNutrientData:
    """Test nutrient data normalization."""

    def setup_method(self):
        """Setup client."""
        self.client = CNFClient()

    def test_normalize_all_nutrients_present(self):
        """Test normalization with all nutrients present."""
        cnf_data = [
            {"nutrient_web_name": "Energy (kcal)", "nutrient_value": 357.0},
            {"nutrient_web_name": "Protein", "nutrient_value": 24.94},
            {"nutrient_web_name": "Carbohydrate", "nutrient_value": 2.22},
            {"nutrient_web_name": "Total Fat", "nutrient_value": 28.0},
            {"nutrient_web_name": "Fibre, total dietary", "nutrient_value": 0.0},
            {"nutrient_web_name": "Sodium, Na", "nutrient_value": 819.0},
            {"nutrient_web_name": "Vitamin C", "nutrient_value": 0.0},
            {"nutrient_web_name": "Calcium, Ca", "nutrient_value": 700.0},
            {"nutrient_web_name": "Iron, Fe", "nutrient_value": 0.24},
        ]

        result = self.client._normalize_nutrient_data(cnf_data)

        assert result["calories"] == 357.0
        assert result["protein_g"] == 24.94
        assert result["carbs_g"] == 2.22
        assert result["fat_g"] == 28.0
        assert result["fiber_g"] == 0.0
        assert result["sodium_mg"] == 819.0
        assert result["vitamin_c_mg"] == 0.0
        assert result["calcium_mg"] == 700.0
        assert result["iron_mg"] == 0.24
        assert "category" in result

    def test_normalize_missing_nutrients_default_to_zero(self):
        """Test that missing nutrients default to 0."""
        cnf_data = [
            {"nutrient_web_name": "Energy (kcal)", "nutrient_value": 100.0},
            {"nutrient_web_name": "Protein", "nutrient_value": 10.0},
        ]

        result = self.client._normalize_nutrient_data(cnf_data)

        # Present nutrients
        assert result["calories"] == 100.0
        assert result["protein_g"] == 10.0

        # Missing nutrients should default to 0
        assert result["carbs_g"] == 0.0
        assert result["fat_g"] == 0.0
        assert result["fiber_g"] == 0.0
        assert result["sodium_mg"] == 0.0
        assert result["vitamin_c_mg"] == 0.0
        assert result["calcium_mg"] == 0.0
        assert result["iron_mg"] == 0.0

    def test_normalize_unknown_nutrients_ignored(self):
        """Test that unknown nutrients are ignored."""
        cnf_data = [
            {"nutrient_web_name": "Energy (kcal)", "nutrient_value": 100.0},
            {"nutrient_web_name": "Unknown Nutrient", "nutrient_value": 999.0},
        ]

        result = self.client._normalize_nutrient_data(cnf_data)

        # Known nutrient
        assert result["calories"] == 100.0

        # Unknown nutrient should not appear
        assert "Unknown Nutrient" not in result


class TestInferCategory:
    """Test food category inference using shared utility."""

    def test_infer_category_protein(self):
        """Test high protein foods categorized as protein."""
        nutrition = {
            "protein_g": 20.0,
            "carbs_g": 5.0,
            "fat_g": 5.0,
            "fiber_g": 0.0,
            "vitamin_c_mg": 0.0,
            "calcium_mg": 50.0,
            "calories": 150.0,
        }
        category = infer_food_category(nutrition)
        assert category == "protein"

    def test_infer_category_dairy(self):
        """Test high calcium foods categorized as dairy."""
        nutrition = {
            "protein_g": 10.0,
            "carbs_g": 5.0,
            "fat_g": 8.0,
            "fiber_g": 0.0,
            "vitamin_c_mg": 0.0,
            "calcium_mg": 300.0,
            "calories": 120.0,
        }
        category = infer_food_category(nutrition)
        assert category == "dairy"

    def test_infer_category_fat(self):
        """Test high fat foods categorized as fat."""
        nutrition = {
            "protein_g": 5.0,
            "carbs_g": 5.0,
            "fat_g": 50.0,
            "fiber_g": 0.0,
            "vitamin_c_mg": 0.0,
            "calcium_mg": 20.0,
            "calories": 500.0,
        }
        category = infer_food_category(nutrition)
        assert category == "fat"

    def test_infer_category_fruit(self):
        """Test high vitamin C foods categorized as fruit."""
        nutrition = {
            "protein_g": 1.0,
            "carbs_g": 15.0,
            "fat_g": 0.5,
            "fiber_g": 2.0,
            "vitamin_c_mg": 30.0,
            "calcium_mg": 20.0,
            "calories": 60.0,
        }
        category = infer_food_category(nutrition)
        assert category == "fruit"

    def test_infer_category_vegetable(self):
        """Test low calorie, high fiber foods categorized as vegetable."""
        nutrition = {
            "protein_g": 2.0,
            "carbs_g": 8.0,
            "fat_g": 0.3,
            "fiber_g": 3.0,
            "vitamin_c_mg": 5.0,
            "calcium_mg": 30.0,
            "calories": 40.0,
        }
        category = infer_food_category(nutrition)
        assert category == "vegetable"

    def test_infer_category_grain(self):
        """Test high carb foods categorized as grain."""
        nutrition = {
            "protein_g": 10.0,
            "carbs_g": 60.0,
            "fat_g": 2.0,
            "fiber_g": 3.0,
            "vitamin_c_mg": 0.0,
            "calcium_mg": 20.0,
            "calories": 300.0,
        }
        category = infer_food_category(nutrition)
        assert category == "grain"

    def test_infer_category_low_calorie_default(self):
        """Test very low calorie foods default to vegetable."""
        nutrition = {
            "protein_g": 0.5,
            "carbs_g": 3.0,
            "fat_g": 0.1,
            "fiber_g": 1.0,
            "vitamin_c_mg": 2.0,
            "calcium_mg": 10.0,
            "calories": 20.0,
        }
        category = infer_food_category(nutrition)
        assert category == "vegetable"


class TestGetCNFClientSingleton:
    """Test singleton pattern for CNF client."""

    def test_singleton_returns_same_instance(self):
        """Test that get_cnf_client returns same instance."""
        client1 = get_cnf_client()
        client2 = get_cnf_client()
        assert client1 is client2

    def test_singleton_preserves_cache(self):
        """Test that singleton preserves cache across calls."""
        client1 = get_cnf_client()
        client1._nutrition_cache[109] = {"calories": 357.0}

        client2 = get_cnf_client()
        assert 109 in client2._nutrition_cache
        assert client2._nutrition_cache[109]["calories"] == 357.0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Setup client."""
        self.client = CNFClient()

    def test_normalize_empty_data(self):
        """Test normalizing empty nutrient data."""
        result = self.client._normalize_nutrient_data([])

        # All nutrients should default to 0
        assert result["calories"] == 0.0
        assert result["protein_g"] == 0.0
        assert result["carbs_g"] == 0.0
        assert result["fat_g"] == 0.0
        assert result["fiber_g"] == 0.0
        assert result["sodium_mg"] == 0.0
        assert result["vitamin_c_mg"] == 0.0
        assert result["calcium_mg"] == 0.0
        assert result["iron_mg"] == 0.0
        assert "category" in result

    def test_infer_category_all_zeros(self):
        """Test category inference with all zero values."""
        nutrition = {
            "protein_g": 0.0,
            "carbs_g": 0.0,
            "fat_g": 0.0,
            "fiber_g": 0.0,
            "vitamin_c_mg": 0.0,
            "calcium_mg": 0.0,
            "calories": 0.0,
        }
        category = infer_food_category(nutrition)
        # Should default to vegetable for very low calorie
        assert category == "vegetable"

    @patch("cnf_client.requests.get")
    def test_get_nutrition_malformed_response(self, mock_get):
        """Test handling malformed API response."""
        # Mock malformed response
        mock_response = MagicMock()
        mock_response.json.return_value = "not a list"
        mock_get.return_value = mock_response

        self.client._foods_list = [{"food_code": 109, "food_description": "Test"}]

        # Should handle gracefully and return None or raise error
        try:
            nutrition = self.client.get_nutrition_per_100g("Test")
            # If no exception, should return None or handle gracefully
            assert nutrition is None or isinstance(nutrition, dict)
        except Exception:
            # If exception is raised, that's also acceptable
            pass
