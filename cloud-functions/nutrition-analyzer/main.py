"""
Cloud Function webhook for Virtual Dietitian AI Agent.
Handles nutrition analysis requests from Vertex AI Agent Builder.
"""

import os
import re

import functions_framework
from flask import jsonify
from nutrition_calculator import NUTRITION_DB, calculate_nutrition
from rule_engine import apply_rules

# Feature flags: Enable API fallbacks
# Set env vars to enable 3-tier fallback: Local DB → CNF API → USDA API
ENABLE_CNF_API = os.environ.get("ENABLE_CNF_API", "false").lower() == "true"
ENABLE_USDA_API = os.environ.get("ENABLE_USDA_API", "false").lower() == "true"

# Multi-language food name translations
# Maps French/Spanish food names to English equivalents in nutrition_db.json
FOOD_TRANSLATIONS = {
    # French
    "avoine": "oatmeal",
    "flocons": "oatmeal",  # "flocons d'avoine" = oatmeal flakes
    "myrtilles": "blueberries",
    "poulet": "chicken",
    "riz": "rice",
    "quinoa": "quinoa",
    "pomme": "apple",
    "banane": "banana",
    "lait": "milk",
    "œuf": "egg",
    "oeuf": "egg",  # alternate spelling without accent
    "œufs": "egg",
    "oeufs": "egg",
    # Spanish
    "avena": "oatmeal",
    "arándanos": "blueberries",
    "arandanos": "blueberries",  # without accent
    "pollo": "chicken",
    "arroz": "rice",
    "brócoli": "broccoli",
    "brocoli": "broccoli",  # without accent
    "manzana": "apple",
    "plátano": "banana",
    "platano": "banana",  # without accent
    "leche": "milk",
    "huevo": "egg",
    "huevos": "egg",
}


def parse_meal_description(meal_description: str):
    """
    Parse natural language meal description into food items.

    Simple word-matching approach for MVP:
    - Split description into words
    - Translate French/Spanish food names to English
    - Check each word (and 2-word phrases) against database
    - Return list of found foods with default quantity = 1

    Args:
        meal_description: Natural language meal description (English, French, or Spanish)

    Returns:
        List of dicts: [{"name": "oatmeal", "quantity": 1}, ...]
    """
    # Normalize: lowercase, remove extra punctuation
    text = meal_description.lower()

    # Remove French/Spanish contractions (l', d', etc.) to get base words
    text = re.sub(r"\b[ld]'", "", text)  # l'avoine → avoine, d'orange → orange

    # Remove commas and periods
    text = re.sub(r"[,.]", " ", text)

    words = text.split()

    # Translate non-English food names to English
    translated_words = []
    for word in words:
        # Clean up any remaining apostrophes or special chars (ASCII + Unicode quotes)
        clean_word = re.sub(r"['\u2018\u2019]", "", word)

        if clean_word in FOOD_TRANSLATIONS:
            translated_words.append(FOOD_TRANSLATIONS[clean_word])
        elif word in NUTRITION_DB:
            # Already English, keep as-is
            translated_words.append(word)
        elif clean_word in NUTRITION_DB:
            # Cleaned version is in DB
            translated_words.append(clean_word)
        else:
            # Not recognized, keep original
            translated_words.append(word)

    found_foods = []
    i = 0

    while i < len(translated_words):
        # Try 2-word phrases first (e.g., "almond butter")
        if i < len(translated_words) - 1:
            two_word = f"{translated_words[i]} {translated_words[i+1]}"
            if two_word in NUTRITION_DB:
                found_foods.append({"name": two_word, "quantity": 1.0})
                i += 2
                continue

        # Try single word (e.g., "oatmeal")
        if translated_words[i] in NUTRITION_DB:
            found_foods.append({"name": translated_words[i], "quantity": 1.0})

        i += 1

    return found_foods


@functions_framework.http
def analyze_nutrition(request):
    """
    HTTP Cloud Function entry point.

    Accepts two request formats:

    Format 1 (Agent Builder - natural language):
    {
        "meal_description": "oatmeal with blueberries and almond butter"
    }

    Format 2 (Direct API - structured):
    {
        "food_items": [
            {"name": "oatmeal", "quantity": 1},
            {"name": "blueberries", "quantity": 0.5},
            {"name": "almond butter", "quantity": 1}
        ]
    }

    Returns:
    {
        "total_nutrition": {...},
        "macro_percentages": {...},
        "insights": [...],
        "follow_up": "..."
    }
    """
    # Handle CORS preflight
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type",
        }
        return ("", 204, headers)

    # Set CORS headers for main request
    headers = {"Access-Control-Allow-Origin": "*"}

    try:
        # Parse request
        request_json = request.get_json(silent=True)

        if not request_json:
            return jsonify({"error": "Invalid request format. Expected JSON payload"}), 400, headers

        # Support both formats:
        # 1. Agent Builder format: {"meal_description": "oatmeal with blueberries"}
        # 2. Direct format: {"food_items": [{"name": "oatmeal", "quantity": 1}]}

        if "meal_description" in request_json:
            # Parse natural language meal description into food items
            meal_description = request_json["meal_description"]
            food_items = parse_meal_description(meal_description)
        elif "food_items" in request_json:
            # Use provided food items directly
            food_items = request_json["food_items"]
        else:
            error_msg = (
                "Invalid request format. Expected "
                '{"meal_description": "..."} or {"food_items": [...]}'
            )
            return (
                jsonify({"error": error_msg}),
                400,
                headers,
            )

        if not isinstance(food_items, list) or len(food_items) == 0:
            error_msg = "No food items could be extracted from the meal description"
            return (
                jsonify({"error": error_msg}),
                400,
                headers,
            )

        # Calculate total nutrition (with 3-tier fallback: Local → CNF → USDA)
        nutrition_result = calculate_nutrition(
            food_items, use_cnf_fallback=ENABLE_CNF_API, use_usda_fallback=ENABLE_USDA_API
        )

        if "error" in nutrition_result:
            return jsonify(nutrition_result), 400, headers

        # Apply business rules
        insights = apply_rules(
            nutrition_result["total_nutrition"],
            nutrition_result["macro_percentages"],
            nutrition_result["food_categories"],
        )

        # Build response
        response = {
            "total_nutrition": nutrition_result["total_nutrition"],
            "macro_percentages": nutrition_result["macro_percentages"],
            "insights": insights,
            "follow_up": generate_follow_up(insights),
        }

        return jsonify(response), 200, headers

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500, headers


def generate_follow_up(insights):
    """Generate a contextual follow-up question based on insights."""
    if not insights:
        return "Would you like nutritional suggestions for your next meal?"

    # Prioritize follow-ups based on insight types
    for insight in insights:
        if insight["type"] == "warning":
            return "Would you like suggestions for lower-sodium alternatives?"
        elif insight["type"] == "recommendation":
            return "Would you like ideas for adding more protein to your meals?"

    # Default follow-up for positive insights
    return "Would you like to know more about the health benefits of your meal?"
