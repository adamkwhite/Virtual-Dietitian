#!/usr/bin/env python3
"""
Local test script for USDA API integration.
Tests both static database and USDA API fallback.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from nutrition_calculator import calculate_nutrition

def test_static_db_food():
    """Test with food in static database (should be fast)."""
    print("\n" + "="*60)
    print("TEST 1: Static Database Food (Chicken)")
    print("="*60)

    food_items = [{"name": "chicken", "quantity": 1}]
    result = calculate_nutrition(food_items, use_usda_fallback=False)

    print(f"✓ Calories: {result['total_nutrition']['calories']}")
    print(f"✓ Protein: {result['total_nutrition']['protein_g']}g")
    print(f"✓ Source: Static DB (fast)")
    return result

def test_usda_api_food():
    """Test with food NOT in static database (requires USDA API)."""
    print("\n" + "="*60)
    print("TEST 2: USDA API Food (Sushi)")
    print("="*60)

    # Check if USDA API is enabled
    enable_usda = os.environ.get("ENABLE_USDA_API", "false").lower() == "true"

    if not enable_usda:
        print("⚠️  ENABLE_USDA_API is not set to 'true' in .env")
        print("   Set ENABLE_USDA_API=true to test USDA API")
        return None

    api_key = os.environ.get("USDA_API_KEY", "")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("⚠️  USDA_API_KEY not set in .env")
        print("   Get your API key at: https://fdc.nal.usda.gov/api-key-signup.html")
        return None

    print(f"Using API key: {api_key[:10]}...")

    food_items = [{"name": "sushi", "quantity": 1}]

    print("\nQuerying USDA API (may take 1-2 seconds)...")
    result = calculate_nutrition(food_items, use_usda_fallback=True)

    if "unknown_foods" in result and "sushi" in result["unknown_foods"]:
        print("✗ Sushi not found in USDA API")
        print("  This might be due to:")
        print("  - Invalid API key")
        print("  - API rate limit exceeded")
        print("  - Network error")
        return None

    print(f"✓ Calories: {result['total_nutrition']['calories']}")
    print(f"✓ Protein: {result['total_nutrition']['protein_g']}g")
    print(f"✓ Source: USDA API (slower but 500,000+ foods)")
    return result

def test_mixed_foods():
    """Test with both static DB and USDA API foods."""
    print("\n" + "="*60)
    print("TEST 3: Mixed Foods (Chicken + Sushi)")
    print("="*60)

    enable_usda = os.environ.get("ENABLE_USDA_API", "false").lower() == "true"

    if not enable_usda:
        print("⚠️  Skipping - ENABLE_USDA_API not enabled")
        return None

    food_items = [
        {"name": "chicken", "quantity": 1},  # Static DB
        {"name": "sushi", "quantity": 1}     # USDA API
    ]

    print("\nProcessing mixed sources...")
    result = calculate_nutrition(food_items, use_usda_fallback=True)

    print(f"✓ Total Calories: {result['total_nutrition']['calories']}")
    print(f"✓ Total Protein: {result['total_nutrition']['protein_g']}g")
    print(f"✓ Fallback: Chicken (static) + Sushi (USDA)")
    return result

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("USDA API Integration - Local Testing")
    print("="*60)

    # Check environment setup
    print("\n📋 Environment Check:")
    enable_usda = os.environ.get("ENABLE_USDA_API", "false")
    api_key = os.environ.get("USDA_API_KEY", "")

    print(f"  ENABLE_USDA_API: {enable_usda}")
    print(f"  USDA_API_KEY: {'✓ Set' if api_key and api_key != 'YOUR_API_KEY_HERE' else '✗ Not set'}")

    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("\n⚠️  Setup Required:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your USDA API key to .env")
        print("  3. Run this script again")
        return

    # Run tests
    test_static_db_food()
    test_usda_api_food()
    test_mixed_foods()

    print("\n" + "="*60)
    print("✓ Testing Complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. If tests pass, deploy with: ./scripts/deploy_function_with_usda.sh YOUR_API_KEY")
    print("  2. Test deployed function with curl commands")
    print("  3. Try via the Virtual Dietitian chat interface")
    print()

if __name__ == "__main__":
    main()
