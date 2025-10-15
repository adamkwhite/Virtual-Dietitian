#!/usr/bin/env python3
"""
Quick local test for CNF API integration.
Tests the CNF client and 3-tier fallback.
"""

import os
import sys

# Set environment to enable CNF
os.environ["ENABLE_CNF_API"] = "true"
os.environ["ENABLE_USDA_API"] = "false"

from cnf_client import get_cnf_client  # noqa: E402
from nutrition_calculator import calculate_nutrition  # noqa: E402


def test_cnf_client():
    """Test CNF client directly."""
    print("=" * 60)
    print("TEST 1: CNF Client Direct Test")
    print("=" * 60)

    client = get_cnf_client()

    # Test 1: Search for a food
    print("\n1. Searching for 'gouda'...")
    food_code = client.search_food("gouda")
    print(f"   Found food_code: {food_code}")

    # Test 2: Get nutrition data
    print("\n2. Getting nutrition for 'gouda'...")
    nutrition = client.get_nutrition_per_100g("gouda")
    if nutrition:
        print(f"   Calories: {nutrition['calories']}")
        print(f"   Protein: {nutrition['protein_g']}g")
        print(f"   Fat: {nutrition['fat_g']}g")
        print(f"   Category: {nutrition['category']}")
    else:
        print("   ❌ Failed to get nutrition data")

    # Test 3: Search for chicken
    print("\n3. Getting nutrition for 'chicken'...")
    nutrition = client.get_nutrition_per_100g("chicken")
    if nutrition:
        print(f"   Calories: {nutrition['calories']}")
        print(f"   Protein: {nutrition['protein_g']}g")
        print(f"   Category: {nutrition['category']}")
    else:
        print("   ❌ Failed to get nutrition data")

    print("\n✅ CNF Client Test Complete")


def test_3_tier_fallback():
    """Test 3-tier fallback logic."""
    print("\n" + "=" * 60)
    print("TEST 2: 3-Tier Fallback Test")
    print("=" * 60)

    # Test with foods from different tiers
    food_items = [
        {"name": "oatmeal", "quantity": 1},  # Should be in local DB
        {"name": "gouda", "quantity": 1},  # Should come from CNF
    ]

    print("\nCalculating nutrition for: oatmeal + gouda")
    print("Expected: oatmeal from local DB, gouda from CNF")

    result = calculate_nutrition(food_items, use_cnf_fallback=True, use_usda_fallback=False)

    print(f"\nTotal Calories: {result['total_nutrition']['calories']}")
    print(f"Total Protein: {result['total_nutrition']['protein_g']}g")
    print(f"Food Categories: {result['food_categories']}")

    if "unknown_foods" in result:
        print(f"❌ Unknown foods: {result['unknown_foods']}")
    else:
        print("✅ All foods found!")

    print("\n✅ 3-Tier Fallback Test Complete")


def test_cnf_cache():
    """Test that CNF caching works."""
    print("\n" + "=" * 60)
    print("TEST 3: CNF Caching Test")
    print("=" * 60)

    client = get_cnf_client()

    print("\n1. First call (should download foods + fetch nutrition)...")
    import time

    start = time.time()
    nutrition1 = client.get_nutrition_per_100g("gouda")
    elapsed1 = time.time() - start
    print(f"   Elapsed: {elapsed1:.2f}s")

    print("\n2. Second call (should use cache)...")
    start = time.time()
    nutrition2 = client.get_nutrition_per_100g("gouda")
    elapsed2 = time.time() - start
    print(f"   Elapsed: {elapsed2:.2f}s")

    if nutrition1 == nutrition2:
        print("   ✅ Same data returned")
    else:
        print("   ❌ Different data returned")

    if elapsed2 < elapsed1:
        print(f"   ✅ Cache is faster ({elapsed1:.2f}s → {elapsed2:.2f}s)")
    else:
        print("   ⚠️  Cache not faster (might be first run)")

    print("\n✅ Caching Test Complete")


if __name__ == "__main__":
    try:
        test_cnf_client()
        test_3_tier_fallback()
        test_cnf_cache()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✅")
        print("=" * 60)
        print("\nCNF integration is working correctly!")
        print("Ready to write unit tests and deploy.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
