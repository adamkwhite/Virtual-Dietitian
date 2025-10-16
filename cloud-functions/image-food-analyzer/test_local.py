"""
Local test script for Cloud Function image analysis endpoint.

This script simulates a browser uploading an image to test the full pipeline:
Vision API → Food Mapper → Response
"""

import sys

import requests


def test_image_upload(image_path: str, endpoint_url: str = "http://localhost:8080"):
    """
    Test image upload to local Cloud Function.

    Args:
        image_path: Path to image file
        endpoint_url: Cloud Function URL (default: localhost:8080)
    """
    print(f"\n{'='*60}")
    print("Testing Image Analysis Endpoint")
    print(f"{'='*60}\n")
    print(f"Image: {image_path}")
    print(f"Endpoint: {endpoint_url}\n")

    # Read image file
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        print(f"✅ Image loaded: {len(image_data)} bytes\n")
    except FileNotFoundError:
        print(f"❌ Error: Image not found at {image_path}")
        return

    # Prepare multipart/form-data request
    files = {"image": ("test-meal.jpg", image_data, "image/jpeg")}
    data = {"user_id": "test_user"}

    # Send POST request
    print("Sending image to Cloud Function...\n")
    try:
        response = requests.post(endpoint_url, files=files, data=data, timeout=30)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}\n")

        # Parse JSON response
        try:
            result = response.json()
            print(f"{'='*60}")
            print("RESPONSE:")
            print(f"{'='*60}\n")

            import json

            print(json.dumps(result, indent=2))

            # Display detected foods in readable format
            if result.get("status") == "success":
                print(f"\n{'='*60}")
                print("DETECTED FOODS:")
                print(f"{'='*60}\n")

                for i, food in enumerate(result.get("detected_foods", []), 1):
                    if food["status"] == "found":
                        print(f"{i}. {food['label']} ({food['confidence']:.0%} confidence)")
                        print(f"   → Mapped to: {food['food_name']}")
                        print(f"   → Serving: {food['serving_size_grams']}g")
                        print(f"   → Category: {food['category']}")
                        print(f"   → Source: {food['source']}")
                        print()
                    else:
                        print(f"{i}. {food['label']} ({food['confidence']:.0%} confidence)")
                        print(f"   → ⚠️ {food['message']}")
                        print()

                print(f"Total Detected: {result['total_detected']} items")
                if "image_url" in result:
                    print(f"Image URL: {result['image_url']}")

            elif result.get("status") == "no_food_detected":
                print("\n⚠️ No food detected")
                print("Suggestions:")
                for suggestion in result.get("suggestions", []):
                    print(f"  - {suggestion}")

            else:
                print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
                if "suggestions" in result:
                    print("Suggestions:")
                    for suggestion in result["suggestions"]:
                        print(f"  - {suggestion}")

        except ValueError:
            print("Error: Response is not valid JSON")
            print(f"Raw response: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {endpoint_url}")
        print("\nMake sure the Cloud Function is running:")
        print("  functions-framework --target=analyze_food_image --debug")

    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out (>30s)")

    except Exception as e:
        print(f"❌ Error: {e}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to test image
        image_path = "../../tests/fixtures/food-images/test-meal-1.jpg"
        print("Using default test image (test-meal-1.jpg)")
    else:
        image_path = sys.argv[1]

    test_image_upload(image_path)
