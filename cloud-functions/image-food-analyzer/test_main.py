"""
Integration tests for image-based food detection Cloud Function.

Tests use mocked Vision API, Cloud Storage, and database to avoid external dependencies.
"""

import io
import json
from unittest.mock import Mock, patch

import pytest
from PIL import Image


# Import after fixtures are defined to allow mocking
@pytest.fixture(autouse=True)
def mock_env():
    """Mock environment variables before importing main."""
    with patch.dict("os.environ", {"ENABLE_CNF_API": "false", "ENABLE_USDA_API": "false"}):
        yield


@pytest.fixture
def mock_nutrition_db():
    """Mock nutrition database loading."""
    return [
        {
            "name": "chicken",
            "calories": 165,
            "protein": 31,
            "carbs": 0,
            "fat": 3.6,
            "fiber": 0,
            "sugar": 0,
            "category": "protein",
        },
        {
            "name": "rice",
            "calories": 130,
            "protein": 2.7,
            "carbs": 28,
            "fat": 0.3,
            "fiber": 0.4,
            "sugar": 0,
            "category": "grain",
        },
    ]


@pytest.fixture
def client():
    """Flask test client for the Cloud Function."""
    # Mock the module-level imports and database loading
    with patch(
        "main.NUTRITION_DB",
        [
            {
                "name": "chicken",
                "calories": 165,
                "protein": 31,
                "carbs": 0,
                "fat": 3.6,
                "category": "protein",
            },
            {
                "name": "rice",
                "calories": 130,
                "protein": 2.7,
                "carbs": 28,
                "fat": 0.3,
                "category": "grain",
            },
        ],
    ):
        # Create a mock request object
        class MockRequest:
            def __init__(self):
                self.files = {}
                self.form = {}
                self.method = "POST"

        yield MockRequest


@pytest.fixture
def sample_image_bytes():
    """Generate a valid JPEG image in bytes."""
    # Create a simple 100x100 red image
    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    return img_bytes.getvalue()


class TestValidateImage:
    """Test image validation logic."""

    def test_validate_image_valid_jpeg(self, sample_image_bytes):
        """Test validation passes for valid JPEG."""
        from main import validate_image

        error = validate_image(sample_image_bytes, "image/jpeg")
        assert error is None

    def test_validate_image_file_too_large(self):
        """Test validation fails when file exceeds size limit."""
        from main import validate_image

        large_bytes = b"x" * (11 * 1024 * 1024)  # 11MB
        error = validate_image(large_bytes, "image/jpeg")
        assert error is not None
        assert "too large" in error.lower()

    def test_validate_image_invalid_content_type(self, sample_image_bytes):
        """Test validation fails for invalid content type."""
        from main import validate_image

        error = validate_image(sample_image_bytes, "image/gif")
        assert error is not None
        assert "invalid file type" in error.lower()

    def test_validate_image_invalid_magic_bytes(self):
        """Test validation fails for invalid magic bytes (fake JPEG)."""
        from main import validate_image

        fake_jpeg = b"not a real jpeg file"
        error = validate_image(fake_jpeg, "image/jpeg")
        assert error is not None
        assert "invalid image" in error.lower()


class TestUploadToStorage:
    """Test Cloud Storage upload logic."""

    @patch("main.storage.Client")
    def test_upload_to_storage_success(self, mock_storage_client, sample_image_bytes):
        """Test successful upload to Cloud Storage."""
        from main import upload_to_storage

        # Mock bucket and blob
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        result = upload_to_storage(sample_image_bytes, "test_user")

        assert result is not None
        assert result.startswith("gs://virtualdietitian-food-images/")
        mock_blob.upload_from_string.assert_called_once()

    @patch("main.storage.Client")
    def test_upload_to_storage_failure(self, mock_storage_client, sample_image_bytes):
        """Test graceful handling of storage upload failure."""
        from main import upload_to_storage

        # Mock storage client to raise exception
        mock_storage_client.return_value.bucket.side_effect = Exception("Storage error")

        result = upload_to_storage(sample_image_bytes, "test_user")

        assert result is None  # Should return None on failure, not crash


class TestBuildDetectedFoodsResponse:
    """Test response building logic."""

    def test_build_response_all_foods_found(self):
        """Test response when all foods are successfully mapped."""
        from main import build_detected_foods_response

        vision_results = [
            {"label": "Chicken", "confidence": 0.94, "category": "protein"},
            {"label": "Rice", "confidence": 0.87, "category": "grain"},
        ]
        mapped_foods = [
            {"name": "chicken", "grams": 85, "category": "protein", "source": "local"},
            {"name": "rice", "grams": 50, "category": "grain", "source": "local"},
        ]

        response = build_detected_foods_response(vision_results, mapped_foods)

        assert response["total_detected"] == 2
        assert len(response["detected_foods"]) == 2
        assert response["detected_foods"][0]["status"] == "found"
        assert response["detected_foods"][1]["status"] == "found"

    def test_build_response_some_foods_not_found(self):
        """Test response when some foods cannot be mapped."""
        from main import build_detected_foods_response

        vision_results = [
            {"label": "Chicken", "confidence": 0.94, "category": "protein"},
            {"label": "Unknown Food", "confidence": 0.65, "category": "other"},
        ]
        mapped_foods = [
            {"name": "chicken", "grams": 85, "category": "protein", "source": "local"},
            None,  # Not found
        ]

        response = build_detected_foods_response(vision_results, mapped_foods)

        assert response["total_detected"] == 2
        assert response["detected_foods"][0]["status"] == "found"
        assert response["detected_foods"][1]["status"] == "not_found"
        assert "not in nutrition database" in response["detected_foods"][1]["message"]


class TestAnalyzeFoodImageEndpoint:
    """Integration tests for the main Cloud Function endpoint."""

    @patch("main.VisionFoodDetector")
    @patch("main.FoodLabelMapper")
    @patch("main.upload_to_storage")
    def test_analyze_food_image_success(
        self, mock_upload, mock_mapper_class, mock_detector_class, sample_image_bytes
    ):
        """Test successful end-to-end image analysis."""
        from main import analyze_food_image

        # Mock Vision API detector
        mock_detector = Mock()
        mock_detector.detect_food.return_value = [
            {"label": "Chicken", "confidence": 0.94, "category": "protein"}
        ]
        mock_detector_class.return_value = mock_detector

        # Mock FoodLabelMapper
        mock_mapper = Mock()
        mock_mapper.process_vision_result.return_value = {
            "name": "chicken",
            "grams": 85,
            "category": "protein",
            "source": "local",
            "confidence": 0.94,
        }
        mock_mapper_class.return_value = mock_mapper

        # Mock storage upload
        mock_upload.return_value = "gs://virtualdietitian-food-images/test.jpg"

        # Create mock request
        mock_file = Mock()
        mock_file.read.return_value = sample_image_bytes
        mock_file.content_type = "image/jpeg"

        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.files = {"image": mock_file}
        mock_request.form = {"user_id": "test_user"}

        # Call endpoint
        response, status_code, headers = analyze_food_image(mock_request)

        assert status_code == 200
        response_data = json.loads(response.data)
        assert response_data["status"] == "success"
        assert response_data["total_detected"] == 1
        assert "image_url" in response_data

    def test_analyze_food_image_no_file(self):
        """Test error response when no image file provided."""
        from main import analyze_food_image

        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.files = {}

        response, status_code, headers = analyze_food_image(mock_request)

        assert status_code == 400
        response_data = json.loads(response.data)
        assert response_data["status"] == "error"
        assert "no image file" in response_data["error"].lower()

    @patch("main.validate_image")
    def test_analyze_food_image_invalid_image(self, mock_validate):
        """Test error response when image validation fails."""
        from main import analyze_food_image

        # Mock validation to return error
        mock_validate.return_value = "File too large"

        mock_file = Mock()
        mock_file.read.return_value = b"fake image data"
        mock_file.content_type = "image/jpeg"

        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.files = {"image": mock_file}
        mock_request.form = {}

        response, status_code, headers = analyze_food_image(mock_request)

        assert status_code == 400
        response_data = json.loads(response.data)
        assert response_data["status"] == "error"

    @patch("main.VisionFoodDetector")
    def test_analyze_food_image_no_food_detected(self, mock_detector_class, sample_image_bytes):
        """Test response when Vision API detects no food."""
        from main import analyze_food_image

        # Mock Vision API to return empty list
        mock_detector = Mock()
        mock_detector.detect_food.return_value = []
        mock_detector_class.return_value = mock_detector

        mock_file = Mock()
        mock_file.read.return_value = sample_image_bytes
        mock_file.content_type = "image/jpeg"

        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.files = {"image": mock_file}
        mock_request.form = {}

        response, status_code, headers = analyze_food_image(mock_request)

        assert status_code == 200
        response_data = json.loads(response.data)
        assert response_data["status"] == "no_food_detected"
        assert "suggestions" in response_data

    def test_analyze_food_image_cors_preflight(self):
        """Test CORS preflight (OPTIONS) request."""
        from main import analyze_food_image

        mock_request = Mock()
        mock_request.method = "OPTIONS"

        response, status_code, headers = analyze_food_image(mock_request)

        assert status_code == 204
        assert headers["Access-Control-Allow-Origin"] == "*"
        assert "POST" in headers["Access-Control-Allow-Methods"]
