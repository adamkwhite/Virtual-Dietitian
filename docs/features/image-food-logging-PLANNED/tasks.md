# Image-Based Food Logging - Task List

**Generated from:** `prd.md`
**Status:** PLANNED
**Created:** October 15, 2025

---

## Relevant Files

### Backend (Cloud Functions)
- `cloud-functions/image-food-analyzer/main.py` - Entry point for image upload and analysis endpoint
- `cloud-functions/image-food-analyzer/vision_client.py` - Google Cloud Vision API integration for food detection
- `cloud-functions/image-food-analyzer/food_label_mapper.py` - Maps Vision labels to nutrition database foods with serving sizes
- `cloud-functions/image-food-analyzer/requirements.txt` - Python dependencies (add google-cloud-vision, google-cloud-storage, Pillow)
- `cloud-functions/image-food-analyzer/test_vision_client.py` - Unit tests for Vision API client
- `cloud-functions/image-food-analyzer/test_food_label_mapper.py` - Unit tests for food label mapping
- `cloud-functions/image-food-analyzer/test_main.py` - Integration tests for image upload endpoint

### Frontend (Demo Webpage)
- `docs/demo/index.html` - Add image upload section with preview and detected foods table
- `docs/demo/styles.css` - Styles for image upload UI components
- `docs/demo/app.js` - JavaScript for image upload, detection display, and confirmation

### Infrastructure
- `scripts/setup-image-processing.sh` - Bash script to enable Vision API, create service account, set up Cloud Storage (CREATED)
- `scripts/deploy-image-analyzer.sh` - Deploy script for image-food-analyzer Cloud Function

### Testing
- `tests/fixtures/food-images/` - Sample food images for integration testing (add 10-20 test images)

### Documentation
- `docs/features/image-food-logging-PLANNED/prd.md` - Product requirements document
- `docs/features/image-food-logging-PLANNED/tasks.md` - This file
- `docs/features/image-food-logging-PLANNED/status.md` - Implementation progress tracker

### Notes
- Unit tests should be placed in the same directory as source files
- Use `pytest --cov=. --cov-report=html` to run tests with coverage
- Vision API requires service account JSON key (stored in `~/.gcp/virtualdietitian-vision-sa.json`)

---

## Tasks

### Phase 1: Infrastructure & Backend

- [x] **1.0 Set up Google Cloud Platform infrastructure for image processing**
  - [x] 1.1 Enable Vision API in GCP project `virtualdietitian`
  - [x] 1.2 Create service account `vision-api-sa` with Vision API and Cloud Storage permissions
  - [x] 1.3 Download service account JSON key and store securely in `~/.gcp/virtualdietitian-vision-sa.json`
  - [x] 1.4 Create Cloud Storage bucket `virtualdietitian-food-images` in `us-central1` region
  - [x] 1.5 Configure bucket lifecycle policy to delete objects after 90 days
  - [x] 1.6 Set bucket permissions to private (authenticated access only)
  - [x] 1.7 Enable CORS on bucket for demo webpage uploads
  - [x] 1.8 Create bash script `scripts/setup-image-processing.sh` to automate setup
  - [x] 1.9 Test bucket access by uploading a test image via `gsutil`

- [ ] **2.0 Build Vision API client for food detection**
  - [ ] 2.1 Create `cloud-functions/image-food-analyzer/vision_client.py` module
  - [ ] 2.2 Implement `VisionFoodDetector` class with `__init__` method (initialize Vision API client)
  - [ ] 2.3 Implement `detect_food(image_bytes, min_confidence=0.8)` method to call Vision API Label Detection
  - [ ] 2.4 Add `_is_food_label(label)` helper to filter food-related labels (use `FOOD_CATEGORIES` whitelist)
  - [ ] 2.5 Add `_infer_category(label)` helper to classify as protein/grain/fruit/vegetable/dairy/other
  - [ ] 2.6 Define `FOOD_CATEGORIES` constant with food-related keywords (food, dish, fruit, vegetable, etc.)
  - [ ] 2.7 Filter out non-food items (plate, table, fork, knife, spoon, bowl, cup)
  - [ ] 2.8 Return list of dicts: `[{"label": "Chicken", "confidence": 0.94, "category": "protein"}]`
  - [ ] 2.9 Handle Vision API errors gracefully (return empty list on failure, log error)
  - [ ] 2.10 Create `test_vision_client.py` with unit tests (mock Vision API responses)
  - [ ] 2.11 Test food detection with 5 sample images locally

- [ ] **3.0 Create food label mapping and serving size logic**
  - [ ] 3.1 Create `cloud-functions/image-food-analyzer/food_label_mapper.py` module
  - [ ] 3.2 Define `STANDARD_SERVING_SIZES` dictionary with category-specific serving sizes (fruit, protein, grain, vegetable, dairy, other)
  - [ ] 3.3 Add specific serving sizes for common foods (apple: 182g, banana: 118g, rice: 195g, etc.)
  - [ ] 3.4 Add `_default` fallback for each category
  - [ ] 3.5 Implement `assign_serving_size(food_name, category)` function
  - [ ] 3.6 Return dict: `{"serving_size": "1 medium banana (118g)", "grams": 118}`
  - [ ] 3.7 Implement `map_label_to_food(label)` function to search Local DB → CNF → USDA
  - [ ] 3.8 Handle case-insensitive matching and partial matches (e.g., "Chicken breast" → "chicken")
  - [ ] 3.9 Return `None` if label not found in any database
  - [ ] 3.10 Create `test_food_label_mapper.py` with unit tests for all serving size categories
  - [ ] 3.11 Test edge cases (unknown foods, empty labels, None values)

- [ ] **4.0 Implement Cloud Function endpoint for image analysis**
  - [ ] 4.1 Create `cloud-functions/image-food-analyzer/` directory
  - [ ] 4.2 Create `main.py` with `@functions_framework.http` decorator for `analyze_food_image` function
  - [ ] 4.3 Add request validation (check Content-Type is multipart/form-data, file size <10MB)
  - [ ] 4.4 Extract image bytes from request (`request.files['image'].read()`)
  - [ ] 4.5 Validate image format (JPEG/PNG, check magic bytes not just extension)
  - [ ] 4.6 Call `VisionFoodDetector.detect_food(image_bytes)` to get food labels
  - [ ] 4.7 For each detected label, call `map_label_to_food()` to find database match
  - [ ] 4.8 For each matched food, call `assign_serving_size()` to get standard portion
  - [ ] 4.9 Upload image to Cloud Storage: `gs://virtualdietitian-food-images/YYYY/MM/DD/{user_id}_{timestamp}.jpg`
  - [ ] 4.10 Build response JSON with detected foods, serving sizes, image URL
  - [ ] 4.11 Handle zero food detection (return `status: "no_food_detected"` with suggestions)
  - [ ] 4.12 Handle errors (Vision API failure, storage failure) with graceful fallback
  - [ ] 4.13 Add CORS headers (`Access-Control-Allow-Origin: *`)
  - [ ] 4.14 Create `requirements.txt` with dependencies (google-cloud-vision==3.*, google-cloud-storage==2.*, Pillow==10.*)
  - [ ] 4.15 Create `test_main.py` with integration tests using sample images
  - [ ] 4.16 Test locally with `functions-framework --target=analyze_food_image --debug`

### Phase 2: Frontend Integration

- [ ] **5.0 Add image upload UI to demo webpage**
  - [ ] 5.1 Update `docs/demo/index.html` with new section "Or Upload a Photo"
  - [ ] 5.2 Add file input: `<input type="file" id="imageInput" accept="image/jpeg,image/png" style="display:none">`
  - [ ] 5.3 Add "Select Image" button that triggers file picker
  - [ ] 5.4 Add image preview section with `<img id="previewImg">` and "Analyze Image" button
  - [ ] 5.5 Add detected foods section with `<table id="foodTable">` (columns: Food, Serving Size, Portion, Action)
  - [ ] 5.6 Add error message div: `<div id="uploadError" class="alert alert-warning">`
  - [ ] 5.7 Update `docs/demo/app.js` with image selection handler (read file, display preview)
  - [ ] 5.8 Add upload handler to send FormData to `/analyze-food-image` endpoint
  - [ ] 5.9 Add loading state for "Analyze Image" button (disable, show "Analyzing...")
  - [ ] 5.10 Add `displayDetectedFoods(foods)` function to populate table rows
  - [ ] 5.11 Add portion dropdown for each food (0.5x, 1x, 1.5x, 2x options)
  - [ ] 5.12 Add "Remove" button for each food row
  - [ ] 5.13 Add "Confirm & Log Nutrition" button to send final list to `/analyze-nutrition`
  - [ ] 5.14 Add `showError(message, suggestions)` function for zero-food-detected and errors
  - [ ] 5.15 Add "Switch to text input" button in error message
  - [ ] 5.16 Update `docs/demo/styles.css` with styles for upload section (preview, table, buttons)
  - [ ] 5.17 Test end-to-end flow in browser (select image → preview → upload → edit → confirm → nutrition)

### Phase 3: Quality & Deployment

- [ ] **6.0 Implement error handling and monitoring**
  - [ ] 6.1 Add retry logic to `vision_client.py` (3 retries with exponential backoff for transient errors)
  - [ ] 6.2 Add timeout handling (Vision API call timeout: 10s, total function timeout: 60s)
  - [ ] 6.3 Log all Vision API requests to Cloud Logging (include image URL, labels, confidence scores)
  - [ ] 6.4 Log all errors with stack traces (Vision API failures, storage failures, validation errors)
  - [ ] 6.5 Create Cloud Monitoring dashboard for Vision API usage (requests/day, error rate, latency)
  - [ ] 6.6 Set up usage alert: email notification when approaching 800 requests/month (80% of free tier)
  - [ ] 6.7 Add client-side error messages for common failures (file too large, invalid format, network error)
  - [ ] 6.8 Test error scenarios: Vision API down, storage down, invalid image format, >10MB file

- [ ] **7.0 Write comprehensive tests and ensure quality gates**
  - [ ] 7.1 Write unit tests for `vision_client.py` (10+ tests, mock Vision API responses)
  - [ ] 7.2 Write unit tests for `food_label_mapper.py` (15+ tests, all serving size categories)
  - [ ] 7.3 Write integration tests for `main.py` (8+ tests, use sample images from `tests/fixtures/food-images/`)
  - [ ] 7.4 Add 10-20 sample food images to `tests/fixtures/food-images/` (fruits, proteins, grains, mixed meals)
  - [ ] 7.5 Run `pytest --cov=. --cov-report=html` and ensure 90%+ coverage on new modules
  - [ ] 7.6 Run pre-commit hooks (black, isort, flake8) and fix all issues
  - [ ] 7.7 Push code and check SonarCloud analysis (ensure no code smells, <10% duplication)
  - [ ] 7.8 Fix any SonarCloud quality gate failures
  - [ ] 7.9 Verify all 93+ existing tests still pass (no regressions)
  - [ ] 7.10 Test on different browsers (Chrome, Firefox, Safari) for frontend compatibility

- [ ] **8.0 Deploy to production and create documentation**
  - [ ] 8.1 Create `scripts/deploy-image-analyzer.sh` deployment script
  - [ ] 8.2 Deploy Cloud Function: `gcloud functions deploy image-food-analyzer --gen2 --runtime=python312 --region=us-central1 --source=./cloud-functions/image-food-analyzer --entry-point=analyze_food_image --trigger-http --allow-unauthenticated --timeout=60s --memory=512Mi`
  - [ ] 8.3 Test deployed endpoint with curl (upload sample image, verify response)
  - [ ] 8.4 Update demo webpage to use production Cloud Function URL
  - [ ] 8.5 Test end-to-end in production (upload image from demo page → nutrition response)
  - [ ] 8.6 Update main `README.md` with image upload feature description
  - [ ] 8.7 Create `docs/features/image-food-logging-PLANNED/api-docs.md` with endpoint specs and examples
  - [ ] 8.8 Record demo video showing image upload workflow (select → preview → detect → edit → nutrition)
  - [ ] 8.9 Update `CLAUDE.md` with Session 11 details (image processing pipeline added)
  - [ ] 8.10 Update `docs/features/image-food-logging-PLANNED/status.md` to IN_PROGRESS → COMPLETED
  - [ ] 8.11 Rename directory to `image-food-logging-COMPLETED`

---

**Estimated Timeline:** 32 hours total (1 week solo developer, 4 days pair programming)
- Phase 1: 20 hours
- Phase 2: 8 hours
- Phase 3: 12 hours

**Next Steps:**
- Review task list with stakeholders
- Create experimental branch: `git checkout -b feature/image-food-logging`
- Begin with Task 1.0 (GCP infrastructure setup)
