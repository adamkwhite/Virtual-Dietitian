"""
Live test script for Vision API food detection.

This script uses REAL Vision API calls (not mocked) to test food detection
with actual images. Requires service account credentials.

Usage:
    export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/virtualdietitian-vision-sa.json
    python test_vision_live.py <image_path>
"""

import os
import sys

from vision_client import VisionFoodDetector


def test_image_detection(image_path: str):
    """Test food detection on a real image."""
    print(f"\n{'='*60}")
    print(f"Testing Vision API with: {image_path}")
    print(f"{'='*60}\n")

    # Check if image exists
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at {image_path}")
        return

    # Read image bytes
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    print(f"✅ Image loaded: {len(image_bytes)} bytes\n")

    # Initialize detector
    try:
        detector = VisionFoodDetector()
        print("✅ Vision API client initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize Vision API client: {e}")
        print("\nMake sure GOOGLE_APPLICATION_CREDENTIALS is set:")
        print("export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/virtualdietitian-vision-sa.json")
        return

    # Detect food with default threshold (0.8)
    print("Detecting food with 80% confidence threshold...\n")
    detected_foods = detector.detect_food(image_bytes, min_confidence=0.8)

    # Display results
    if detected_foods:
        print(f"✅ Detected {len(detected_foods)} food items:\n")
        for i, food in enumerate(detected_foods, 1):
            print(f"{i}. {food['label']}")
            print(f"   Confidence: {food['confidence']:.2%}")
            print(f"   Category: {food['category']}")
            print()
    else:
        print("❌ No food detected (or all labels below 80% confidence)")
        print("\nTrying again with 60% confidence threshold...\n")

        # Retry with lower threshold
        detected_foods = detector.detect_food(image_bytes, min_confidence=0.6)
        if detected_foods:
            print(f"✅ Detected {len(detected_foods)} food items:\n")
            for i, food in enumerate(detected_foods, 1):
                print(f"{i}. {food['label']}")
                print(f"   Confidence: {food['confidence']:.2%}")
                print(f"   Category: {food['category']}")
                print()
        else:
            print("❌ Still no food detected")

    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_vision_live.py <image_path>")
        print("\nExample:")
        print("  export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/virtualdietitian-vision-sa.json")
        print("  python test_vision_live.py /path/to/food_image.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    test_image_detection(image_path)
