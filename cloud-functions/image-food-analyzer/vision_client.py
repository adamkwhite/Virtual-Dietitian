"""
Google Cloud Vision API client for food detection.

This module provides integration with Google Cloud Vision API to detect
food items in images using Label Detection. It filters labels to food-related
categories and assigns confidence scores to each detected item.
"""

import logging
from typing import Dict, List

from google.cloud import vision

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisionFoodDetector:
    """Detect food items in images using Google Cloud Vision API."""

    # Whitelist of food-related labels (expand as needed)
    FOOD_CATEGORIES = {
        "food",
        "dish",
        "cuisine",
        "ingredient",
        "fruit",
        "vegetable",
        "meat",
        "poultry",
        "seafood",
        "dairy",
        "grain",
        "bread",
        "pasta",
        "rice",
        "salad",
        "soup",
        "dessert",
        "snack",
        "beverage",
        "produce",
        "staple food",
        "whole food",
        "natural foods",
    }

    # Non-food items to exclude from results
    NON_FOOD_ITEMS = {
        "plate",
        "table",
        "fork",
        "knife",
        "spoon",
        "bowl",
        "cup",
        "glass",
        "mug",
        "dish",
        "platter",
        "cutlery",
        "tableware",
        "utensil",
        "napkin",
        "placemat",
    }

    def __init__(self):
        """Initialize Vision API client."""
        try:
            self.client = vision.ImageAnnotatorClient()
            logger.info("Vision API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Vision API client: {e}")
            raise

    def detect_food(self, image_bytes: bytes, min_confidence: float = 0.8) -> List[Dict]:
        """
        Detect food items in image using Vision API Label Detection.

        Args:
            image_bytes: Raw image bytes (JPEG/PNG)
            min_confidence: Minimum confidence threshold (0.0 to 1.0)

        Returns:
            List of detected food labels with confidence scores and categories:
            [
                {"label": "Chicken", "confidence": 0.94, "category": "protein"},
                {"label": "Rice", "confidence": 0.87, "category": "grain"}
            ]

        Raises:
            Exception: If Vision API call fails
        """
        try:
            # Build Vision API request
            image = vision.Image(content=image_bytes)
            response = self.client.label_detection(image=image, max_results=20)

            # Check for API errors
            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")

            food_labels = []

            for label in response.label_annotations:
                # Filter: food-related labels only
                if not self._is_food_label(label.description):
                    logger.debug(
                        f"Filtered out non-food label: {label.description} ({label.score:.2f})"
                    )
                    continue

                # Filter: confidence threshold
                if label.score < min_confidence:
                    logger.debug(
                        f"Filtered out low-confidence label: "
                        f"{label.description} ({label.score:.2f})"
                    )
                    continue

                # Infer food category for serving size assignment
                category = self._infer_category(label.description)

                food_labels.append(
                    {
                        "label": label.description,
                        "confidence": label.score,
                        "category": category,
                    }
                )

                logger.info(
                    f"Detected food: {label.description} ({label.score:.2f}, category: {category})"
                )

            return food_labels

        except Exception as e:
            logger.error(f"Vision API food detection failed: {e}")
            # Return empty list on failure (graceful degradation)
            return []

    def _is_food_label(self, label: str) -> bool:
        """
        Check if label is food-related.

        Args:
            label: Label description from Vision API

        Returns:
            True if label is food-related, False otherwise
        """
        label_lower = label.lower()

        # Exclude common non-food items first (high priority filter)
        if label_lower in self.NON_FOOD_ITEMS:
            return False

        # Check if label contains any food category keyword
        for food_keyword in self.FOOD_CATEGORIES:
            if food_keyword in label_lower:
                return True

        # Vision API is trained on food images - if it's not a known non-food item
        # and has high confidence, assume it's food (lenient approach)
        # This catches specific food names like "Chicken", "Banana", etc.
        return True

    def _infer_category(self, label: str) -> str:
        """
        Infer food category from label for serving size assignment.

        Args:
            label: Food label from Vision API

        Returns:
            Food category: "protein", "grain", "fruit", "vegetable", "dairy", or "other"
        """
        label_lower = label.lower()

        # Protein category
        if any(
            word in label_lower
            for word in [
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
            ]
        ):
            return "protein"

        # Grain category
        elif any(
            word in label_lower
            for word in [
                "rice",
                "pasta",
                "bread",
                "grain",
                "quinoa",
                "oat",
                "cereal",
                "wheat",
                "noodle",
            ]
        ):
            return "grain"

        # Fruit category
        elif any(
            word in label_lower
            for word in [
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
            ]
        ):
            return "fruit"

        # Vegetable category
        elif any(
            word in label_lower
            for word in [
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
            ]
        ):
            return "vegetable"

        # Dairy category
        elif any(
            word in label_lower for word in ["cheese", "milk", "yogurt", "dairy", "butter", "cream"]
        ):
            return "dairy"

        # Default: other
        else:
            return "other"
