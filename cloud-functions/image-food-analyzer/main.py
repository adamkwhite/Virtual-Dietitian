"""
Cloud Function for image-based food detection and nutrition analysis.

This endpoint accepts image uploads, uses Google Cloud Vision API to detect
food items, maps them to nutrition database entries with serving sizes, and
returns structured data for nutrition calculation.

Endpoint: /analyze-food-image
Method: POST
Content-Type: multipart/form-data
"""

import io
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

import functions_framework
from cnf_client import CNFClient
from flask import jsonify
from food_label_mapper import FoodLabelMapper
from google.cloud import storage
from PIL import Image
from usda_client import USDAClient
from vision_client import VisionFoodDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Feature flags: Enable API fallbacks
ENABLE_CNF_API = os.environ.get("ENABLE_CNF_API", "false").lower() == "true"
ENABLE_USDA_API = os.environ.get("ENABLE_USDA_API", "false").lower() == "true"

# Load nutrition database at module level (cached across function invocations)
NUTRITION_DB = []
try:
    with open("nutrition_db.json", "r") as f:
        data = json.load(f)

    # Transform to simpler format for FoodLabelMapper
    # Original format: {"foods": [{"name": "X", "nutrition": {...}, ...}]}
    # Target format: [{"name": "x", "calories": N, "protein": N, ...}]
    for food in data["foods"]:
        # Add primary name (lowercase)
        NUTRITION_DB.append(
            {
                "name": food["name"].lower(),
                "calories": food["nutrition"]["calories"],
                "protein": food["nutrition"]["protein_g"],
                "carbs": food["nutrition"]["carbs_g"],
                "fat": food["nutrition"]["fat_g"],
                "fiber": food["nutrition"].get("fiber_g", 0),
                "sugar": food["nutrition"].get("sugar_g", 0),
                "category": food["category"],
            }
        )

        # Add aliases as separate entries (point to same food data)
        for alias in food.get("aliases", []):
            if alias.lower() != food["name"].lower():  # Skip duplicate primary name
                NUTRITION_DB.append(
                    {
                        "name": alias.lower(),
                        "calories": food["nutrition"]["calories"],
                        "protein": food["nutrition"]["protein_g"],
                        "carbs": food["nutrition"]["carbs_g"],
                        "fat": food["nutrition"]["fat_g"],
                        "fiber": food["nutrition"].get("fiber_g", 0),
                        "sugar": food["nutrition"].get("sugar_g", 0),
                        "category": food["category"],
                    }
                )

    logger.info(f"Loaded nutrition database: {len(NUTRITION_DB)} food entries")
except Exception as e:
    logger.error(f"Failed to load nutrition database: {e}")

# Initialize API clients (cached across function invocations)
CNF_CLIENT = None
USDA_CLIENT = None

if ENABLE_CNF_API:
    try:
        CNF_CLIENT = CNFClient()
        logger.info("CNF API client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize CNF client: {e}")

if ENABLE_USDA_API:
    try:
        USDA_CLIENT = USDAClient()
        logger.info("USDA API client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize USDA client: {e}")

# Cloud Storage configuration
BUCKET_NAME = "virtualdietitian-food-images"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {"image/jpeg", "image/png", "image/jpg"}
ALLOWED_MAGIC_BYTES = {
    b"\xff\xd8\xff": "jpeg",  # JPEG
    b"\x89PNG": "png",  # PNG
}


def validate_image(file_bytes: bytes, content_type: str) -> Optional[str]:
    """
    Validate image format and size.

    Args:
        file_bytes: Raw image bytes
        content_type: Content-Type header value

    Returns:
        Error message if validation fails, None if valid
    """
    # Check file size
    if len(file_bytes) > MAX_FILE_SIZE:
        return f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB"

    # Check content type
    if content_type.lower() not in ALLOWED_EXTENSIONS:
        return f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"

    # Check magic bytes (actual file format, not just extension)
    for magic_bytes, format_name in ALLOWED_MAGIC_BYTES.items():
        if file_bytes.startswith(magic_bytes):
            # Additional validation: try to open with PIL
            try:
                img = Image.open(io.BytesIO(file_bytes))
                img.verify()
                return None  # Valid image
            except Exception as e:
                return f"Invalid image file: {str(e)}"

    return "Invalid image format. Only JPEG and PNG are supported"


def upload_to_storage(image_bytes: bytes, user_id: str = "anonymous") -> Optional[str]:
    """
    Upload image to Cloud Storage.

    Args:
        image_bytes: Raw image bytes
        user_id: User identifier (default: "anonymous" for demo)

    Returns:
        Public URL of uploaded image, or None if upload fails
    """
    try:
        # Create storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)

        # Generate unique filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        date_path = datetime.utcnow().strftime("%Y/%m/%d")
        blob_name = f"{date_path}/{user_id}_{timestamp}.jpg"

        # Upload to Cloud Storage
        blob = bucket.blob(blob_name)
        blob.upload_from_string(image_bytes, content_type="image/jpeg", timeout=30)

        # Return gs:// URL (not public HTTP URL since bucket is private)
        gs_url = f"gs://{BUCKET_NAME}/{blob_name}"
        logger.info(f"Image uploaded successfully: {gs_url}")
        return gs_url

    except Exception as e:
        logger.error(f"Failed to upload image to Cloud Storage: {e}")
        return None


def build_detected_foods_response(vision_results: List[Dict], mapped_foods: List[Dict]) -> Dict:
    """
    Build response JSON with detected foods and serving sizes.

    Args:
        vision_results: Raw Vision API detection results
        mapped_foods: Mapped foods from FoodLabelMapper

    Returns:
        Response dictionary with detected foods
    """
    detected_foods = []

    for vision_result, mapped_food in zip(vision_results, mapped_foods):
        if mapped_food is None:
            # Label detected but not mapped to database
            detected_foods.append(
                {
                    "label": vision_result["label"],
                    "confidence": vision_result["confidence"],
                    "category": vision_result["category"],
                    "status": "not_found",
                    "message": f"'{vision_result['label']}' detected but not in nutrition database",
                }
            )
        else:
            # Successfully mapped to database food
            detected_foods.append(
                {
                    "label": vision_result["label"],
                    "confidence": vision_result["confidence"],
                    "food_name": mapped_food["name"],
                    "serving_size_grams": mapped_food["grams"],
                    "category": mapped_food["category"],
                    "source": mapped_food["source"],
                    "status": "found",
                }
            )

    return {"detected_foods": detected_foods, "total_detected": len(vision_results)}


@functions_framework.http
def analyze_food_image(request):
    """
    HTTP Cloud Function entry point for image-based food detection.

    Request Format (multipart/form-data):
    - image: Image file (JPEG/PNG, <10MB)
    - user_id (optional): User identifier for storage organization

    Response Format:
    {
        "status": "success",
        "detected_foods": [
            {
                "label": "Salad",
                "confidence": 0.95,
                "food_name": "mixed green salad",
                "serving_size_grams": 85,
                "category": "vegetable",
                "source": "local",
                "status": "found"
            }
        ],
        "total_detected": 3,
        "image_url": "gs://virtualdietitian-food-images/2025/10/16/user_20251016_123456_789.jpg"
    }

    Error Response:
    {
        "status": "error",
        "error": "Error message",
        "suggestions": ["Try a clearer image", "Ensure good lighting"]
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
        # Validate request has file
        if "image" not in request.files:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "No image file provided",
                        "suggestions": [
                            "Ensure you're sending a file with key 'image'",
                            "Use Content-Type: multipart/form-data",
                        ],
                    }
                ),
                400,
                headers,
            )

        file = request.files["image"]
        user_id = request.form.get("user_id", "anonymous")

        # Read image bytes
        image_bytes = file.read()
        content_type = file.content_type or "application/octet-stream"

        logger.info(
            f"Received image upload: size={len(image_bytes)} bytes, "
            f"type={content_type}, user_id={user_id}"
        )

        # Validate image
        validation_error = validate_image(image_bytes, content_type)
        if validation_error:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": validation_error,
                        "suggestions": [
                            "Upload a JPEG or PNG image",
                            "Ensure file size is under 10MB",
                            "Verify image is not corrupted",
                        ],
                    }
                ),
                400,
                headers,
            )

        # Detect food using Vision API
        logger.info("Calling Vision API for food detection...")
        detector = VisionFoodDetector()
        vision_results = detector.detect_food(image_bytes, min_confidence=0.75)

        if not vision_results:
            return (
                jsonify(
                    {
                        "status": "no_food_detected",
                        "error": "No food items detected in the image",
                        "suggestions": [
                            "Try a clearer image with better lighting",
                            "Ensure food items are clearly visible",
                            "Avoid images with too many non-food objects",
                            "Use text input instead if image detection fails",
                        ],
                    }
                ),
                200,
                headers,
            )

        logger.info(f"Vision API detected {len(vision_results)} food items")

        # Map Vision labels to database foods with serving sizes
        # Use 3-tier fallback: Local DB → CNF API → USDA API
        mapper = FoodLabelMapper(
            nutrition_db=NUTRITION_DB, cnf_client=CNF_CLIENT, usda_client=USDA_CLIENT
        )

        mapped_foods = []
        for vision_result in vision_results:
            mapped_food = mapper.process_vision_result(vision_result)
            mapped_foods.append(mapped_food)
            if mapped_food:
                logger.info(
                    f"Mapped '{vision_result['label']}' → '{mapped_food['name']}' "
                    f"({mapped_food['grams']}g, source: {mapped_food['source']})"
                )
            else:
                logger.warning(f"Could not map '{vision_result['label']}' to nutrition database")

        # Upload image to Cloud Storage
        logger.info("Uploading image to Cloud Storage...")
        image_url = upload_to_storage(image_bytes, user_id)

        if not image_url:
            logger.warning("Image upload failed, continuing without storage URL")

        # Build response
        response_data = build_detected_foods_response(vision_results, mapped_foods)
        response_data["status"] = "success"

        if image_url:
            response_data["image_url"] = image_url

        logger.info(
            f"Successfully processed image: {response_data['total_detected']} foods detected"
        )

        return jsonify(response_data), 200, headers

    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "status": "error",
                    "error": f"Internal server error: {str(e)}",
                    "suggestions": [
                        "Try uploading a different image",
                        "Contact support if the problem persists",
                    ],
                }
            ),
            500,
            headers,
        )


def download_from_gcs(image_url: str) -> Optional[bytes]:
    """
    Download image from Google Cloud Storage URL.

    Args:
        image_url: GCS URL in format gs://bucket/path or https://storage.googleapis.com/bucket/path

    Returns:
        Image bytes if successful, None otherwise
    """
    try:
        # Convert https URL to gs:// format if needed
        if image_url.startswith("https://storage.googleapis.com/"):
            # Extract bucket and path from https URL
            # https://storage.googleapis.com/bucket-name/path/to/file.jpg
            parts = image_url.replace("https://storage.googleapis.com/", "").split("/", 1)
            bucket_name = parts[0]
            blob_name = parts[1] if len(parts) > 1 else ""
        elif image_url.startswith("gs://"):
            # gs://bucket-name/path/to/file.jpg
            parts = image_url.replace("gs://", "").split("/", 1)
            bucket_name = parts[0]
            blob_name = parts[1] if len(parts) > 1 else ""
        else:
            logger.error(f"Invalid GCS URL format: {image_url}")
            return None

        # Download from GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        image_bytes = blob.download_as_bytes()
        logger.info(f"Downloaded {len(image_bytes)} bytes from {image_url}")
        return image_bytes

    except Exception as e:
        logger.error(f"Failed to download from GCS: {e}")
        return None


@functions_framework.http
def analyze_from_url(request):
    """
    HTTP Cloud Function entry point for analyzing images from GCS URLs.

    This endpoint is designed for Agent Builder integration where the agent
    receives a GCS URL from file uploads in Dialogflow Messenger.

    Request Format (application/json):
    {
        "image_url": "gs://bucket/path/to/image.jpg"
    }

    Response Format:
    {
        "status": "success",
        "detected_foods": [...],
        "food_list": "broccoli, chicken, rice",
        "total_detected": 3
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

    # Set CORS headers
    headers = {"Access-Control-Allow-Origin": "*"}

    try:
        # Parse JSON request
        request_json = request.get_json(silent=True)
        if not request_json or "image_url" not in request_json:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Missing 'image_url' in request body",
                        "suggestions": [
                            "Provide a Google Cloud Storage URL in the request body",
                            'Format: {"image_url": "gs://bucket/path/to/image.jpg"}',
                        ],
                    }
                ),
                400,
                headers,
            )

        image_url = request_json["image_url"]
        logger.info(f"Received image URL: {image_url}")

        # Download image from GCS
        image_bytes = download_from_gcs(image_url)
        if not image_bytes:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Failed to download image from GCS",
                        "suggestions": [
                            "Verify the GCS URL is correct",
                            "Ensure the Cloud Function has access to the bucket",
                            "Check if the file exists at the specified path",
                        ],
                    }
                ),
                400,
                headers,
            )

        # Validate image
        validation_error = validate_image(image_bytes, "image/jpeg")
        if validation_error:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": validation_error,
                        "suggestions": ["Ensure the file is a valid JPEG or PNG image"],
                    }
                ),
                400,
                headers,
            )

        # Detect food using Vision API
        logger.info("Calling Vision API for food detection...")
        detector = VisionFoodDetector()
        vision_results = detector.detect_food(image_bytes, min_confidence=0.75)

        if not vision_results:
            return (
                jsonify(
                    {
                        "status": "no_food_detected",
                        "error": "No food items detected in the image",
                        "detected_foods": [],
                        "food_list": "",
                        "total_detected": 0,
                    }
                ),
                200,
                headers,
            )

        logger.info(f"Vision API detected {len(vision_results)} food items")

        # Map Vision labels to database foods
        mapper = FoodLabelMapper(
            nutrition_db=NUTRITION_DB, cnf_client=CNF_CLIENT, usda_client=USDA_CLIENT
        )

        mapped_foods = []
        for vision_result in vision_results:
            mapped_food = mapper.process_vision_result(vision_result)
            mapped_foods.append(mapped_food)
            if mapped_food:
                logger.info(
                    f"Mapped '{vision_result['label']}' → '{mapped_food['name']}' "
                    f"({mapped_food['grams']}g, source: {mapped_food['source']})"
                )

        # Build response
        response_data = build_detected_foods_response(vision_results, mapped_foods)
        response_data["status"] = "success"

        # Add food_list for easy agent parsing (deduplicated, no generic terms)
        generic_terms = ["food", "produce", "ingredient", "dish", "meal"]
        food_names = [
            f["food_name"]
            for f in response_data["detected_foods"]
            if f.get("status") == "found" and f["food_name"] not in generic_terms
        ]
        unique_foods = list(dict.fromkeys(food_names))  # Preserve order while deduplicating
        response_data["food_list"] = ", ".join(unique_foods)

        logger.info(f"Successfully processed image: food_list={response_data['food_list']}")

        return jsonify(response_data), 200, headers

    except Exception as e:
        logger.error(f"Error processing image from URL: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "status": "error",
                    "error": f"Internal server error: {str(e)}",
                    "suggestions": [
                        "Try uploading a different image",
                        "Contact support if the problem persists",
                    ],
                }
            ),
            500,
            headers,
        )
