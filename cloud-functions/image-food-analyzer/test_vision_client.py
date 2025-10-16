"""
Unit tests for Vision API food detection client.

Tests use mocked Vision API responses to avoid actual API calls during testing.
"""

from unittest.mock import Mock, patch

import pytest
from vision_client import VisionFoodDetector


@pytest.fixture
def vision_detector():
    """Fixture to create VisionFoodDetector instance with mocked client."""
    with patch("vision_client.vision.ImageAnnotatorClient"):
        detector = VisionFoodDetector()
        return detector


class TestVisionFoodDetector:
    """Test suite for VisionFoodDetector class."""

    def test_init_success(self):
        """Test successful initialization of Vision API client."""
        with patch("vision_client.vision.ImageAnnotatorClient") as mock_client:
            detector = VisionFoodDetector()
            assert detector.client is not None
            mock_client.assert_called_once()

    def test_init_failure(self):
        """Test initialization failure when Vision API client cannot be created."""
        with patch(
            "vision_client.vision.ImageAnnotatorClient", side_effect=Exception("API init failed")
        ):
            with pytest.raises(Exception, match="API init failed"):
                VisionFoodDetector()

    def test_detect_food_success(self, vision_detector):
        """Test successful food detection with multiple food items."""
        # Mock Vision API response
        mock_response = Mock()
        mock_response.error.message = ""
        mock_response.label_annotations = [
            Mock(description="Chicken", score=0.94),
            Mock(description="Rice", score=0.87),
            Mock(description="Broccoli", score=0.91),
            Mock(description="Plate", score=0.95),  # Non-food, should be filtered
        ]

        vision_detector.client.label_detection = Mock(return_value=mock_response)

        result = vision_detector.detect_food(b"fake_image_bytes")

        assert len(result) == 3  # Plate filtered out
        assert result[0]["label"] == "Chicken"
        assert result[0]["confidence"] == 0.94
        assert result[0]["category"] == "protein"
        assert result[1]["label"] == "Rice"
        assert result[1]["category"] == "grain"
        assert result[2]["label"] == "Broccoli"
        assert result[2]["category"] == "vegetable"

    def test_detect_food_with_confidence_threshold(self, vision_detector):
        """Test that labels below confidence threshold are filtered out."""
        mock_response = Mock()
        mock_response.error.message = ""
        mock_response.label_annotations = [
            Mock(description="Chicken", score=0.94),  # Above threshold
            Mock(description="Rice", score=0.75),  # Below 0.8 threshold
        ]

        vision_detector.client.label_detection = Mock(return_value=mock_response)

        result = vision_detector.detect_food(b"fake_image_bytes", min_confidence=0.8)

        assert len(result) == 1
        assert result[0]["label"] == "Chicken"

    def test_detect_food_no_food_detected(self, vision_detector):
        """Test when Vision API detects no food items."""
        mock_response = Mock()
        mock_response.error.message = ""
        mock_response.label_annotations = [
            Mock(description="Table", score=0.95),
            Mock(description="Fork", score=0.89),
        ]

        vision_detector.client.label_detection = Mock(return_value=mock_response)

        result = vision_detector.detect_food(b"fake_image_bytes")

        assert len(result) == 0

    def test_detect_food_api_error(self, vision_detector):
        """Test graceful handling of Vision API errors."""
        mock_response = Mock()
        mock_response.error.message = "API quota exceeded"

        vision_detector.client.label_detection = Mock(return_value=mock_response)

        result = vision_detector.detect_food(b"fake_image_bytes")

        # Should return empty list on error (graceful degradation)
        assert result == []

    def test_detect_food_exception(self, vision_detector):
        """Test handling of exceptions during Vision API call."""
        vision_detector.client.label_detection = Mock(side_effect=Exception("Network error"))

        result = vision_detector.detect_food(b"fake_image_bytes")

        # Should return empty list on exception
        assert result == []

    def test_is_food_label_food_items(self, vision_detector):
        """Test that food-related labels are correctly identified."""
        assert vision_detector._is_food_label("Chicken") is True
        assert vision_detector._is_food_label("Fresh fruit") is True
        assert vision_detector._is_food_label("Vegetable") is True
        assert vision_detector._is_food_label("Dairy product") is True
        assert vision_detector._is_food_label("Bread") is True
        assert vision_detector._is_food_label("Rice dish") is True

    def test_is_food_label_non_food_items(self, vision_detector):
        """Test that non-food items are correctly filtered out."""
        assert vision_detector._is_food_label("Plate") is False
        assert vision_detector._is_food_label("Table") is False
        assert vision_detector._is_food_label("Fork") is False
        assert vision_detector._is_food_label("Knife") is False
        assert vision_detector._is_food_label("Spoon") is False
        assert vision_detector._is_food_label("Bowl") is False
        assert vision_detector._is_food_label("Cup") is False

    def test_is_food_label_ambiguous_items(self, vision_detector):
        """Test handling of ambiguous labels."""
        # "Dish" can be food or tableware - should be filtered as non-food
        assert vision_detector._is_food_label("Dish") is False
        # "Food" keyword should pass through
        assert vision_detector._is_food_label("Food") is True

    def test_infer_category_protein(self, vision_detector):
        """Test category inference for protein foods."""
        assert vision_detector._infer_category("Chicken") == "protein"
        assert vision_detector._infer_category("Beef steak") == "protein"
        assert vision_detector._infer_category("Salmon") == "protein"
        assert vision_detector._infer_category("Turkey") == "protein"
        assert vision_detector._infer_category("Egg") == "protein"
        assert vision_detector._infer_category("Grilled fish") == "protein"

    def test_infer_category_grain(self, vision_detector):
        """Test category inference for grain foods."""
        assert vision_detector._infer_category("Rice") == "grain"
        assert vision_detector._infer_category("Pasta") == "grain"
        assert vision_detector._infer_category("Bread") == "grain"
        assert vision_detector._infer_category("Quinoa") == "grain"
        assert vision_detector._infer_category("Oatmeal") == "grain"

    def test_infer_category_fruit(self, vision_detector):
        """Test category inference for fruits."""
        assert vision_detector._infer_category("Apple") == "fruit"
        assert vision_detector._infer_category("Banana") == "fruit"
        assert vision_detector._infer_category("Orange") == "fruit"
        assert vision_detector._infer_category("Strawberry") == "fruit"
        assert vision_detector._infer_category("Blueberry") == "fruit"

    def test_infer_category_vegetable(self, vision_detector):
        """Test category inference for vegetables."""
        assert vision_detector._infer_category("Broccoli") == "vegetable"
        assert vision_detector._infer_category("Carrot") == "vegetable"
        assert vision_detector._infer_category("Lettuce") == "vegetable"
        assert vision_detector._infer_category("Tomato") == "vegetable"
        assert vision_detector._infer_category("Spinach") == "vegetable"

    def test_infer_category_dairy(self, vision_detector):
        """Test category inference for dairy products."""
        assert vision_detector._infer_category("Cheese") == "dairy"
        assert vision_detector._infer_category("Milk") == "dairy"
        assert vision_detector._infer_category("Yogurt") == "dairy"
        assert vision_detector._infer_category("Butter") == "dairy"

    def test_infer_category_other(self, vision_detector):
        """Test category inference for uncategorized foods."""
        assert vision_detector._infer_category("Soup") == "other"
        assert vision_detector._infer_category("Sandwich") == "other"
        assert vision_detector._infer_category("Unknown food") == "other"

    def test_detect_food_empty_response(self, vision_detector):
        """Test handling of empty Vision API response."""
        mock_response = Mock()
        mock_response.error.message = ""
        mock_response.label_annotations = []

        vision_detector.client.label_detection = Mock(return_value=mock_response)

        result = vision_detector.detect_food(b"fake_image_bytes")

        assert result == []

    def test_detect_food_case_insensitive(self, vision_detector):
        """Test that label matching is case-insensitive."""
        mock_response = Mock()
        mock_response.error.message = ""
        mock_response.label_annotations = [
            Mock(description="CHICKEN", score=0.94),  # Uppercase
            Mock(description="RiCe", score=0.87),  # Mixed case
        ]

        vision_detector.client.label_detection = Mock(return_value=mock_response)

        result = vision_detector.detect_food(b"fake_image_bytes")

        assert len(result) == 2
        assert result[0]["category"] == "protein"  # CHICKEN → protein
        assert result[1]["category"] == "grain"  # RiCe → grain
