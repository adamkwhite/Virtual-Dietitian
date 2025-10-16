# PRD: Image-Based Food Logging Pipeline

**Status:** PLANNED
**Created:** October 15, 2025
**Target Audience:** Junior Developer
**Scope:** Experimental Branch (Phase 3)

---

## Overview

Add image upload capability to Virtual Dietitian, allowing users to take photos of their meals and automatically extract food items using Google Cloud Vision API. Detected foods will be logged with standard serving sizes and sent to the existing nutrition analysis pipeline.

This complements (not replaces) the current text-based meal description workflow, providing users with a faster, less tedious way to log meals.

---

## Problem Statement

**Current Pain Point:** Manual food logging via text descriptions is tedious and time-consuming. Users must type out each food item, remember exact names, and estimate portions manually.

**User Impact:**
- Friction in daily logging reduces engagement
- Users may skip logging meals due to effort required
- Text input is slower than visual capture on mobile devices

**Context:**
- Virtual Dietitian currently supports text-based meal descriptions in English, French, and Spanish
- Users can query 47 local foods + 5,690 CNF foods + 500k+ USDA foods via 3-tier fallback
- Agent Builder interface handles conversational NLU/NLG
- Cloud Function webhook provides deterministic nutrition calculations

**Justification:**
Image-based logging is the industry standard for modern nutrition apps (MyFitnessPal, Lose It!, Yazio). Users expect this feature as table stakes for food tracking applications.

---

## Goals

### Primary Goals
1. **Reduce logging friction:** Enable users to log meals in <10 seconds (photo → confirm → done)
2. **Maintain accuracy:** Achieve 80%+ food detection accuracy using Google Cloud Vision API Label Detection
3. **Stay within budget:** Use free tier (1,000 images/month) for demo/POC phase
4. **Preserve existing workflow:** Text-based logging remains available as fallback

### Secondary Goals
1. **Gather training data:** Store images for future custom ML model training
2. **Learn user patterns:** Track which foods are frequently photographed vs typed
3. **Validate ML approach:** Determine if Vision API is sufficient or if specialized food API (LogMeal, Clarifai) is needed

---

## Success Criteria

- [ ] Users can upload food images from desktop (file picker)
- [ ] System detects 2+ food items with 80%+ confidence in 80% of test images
- [ ] Detected foods map to standard serving sizes (e.g., "banana" → "1 medium banana, 118g")
- [ ] Users can edit detected food list before logging (add/remove items, adjust quantities)
- [ ] Zero-food-detected cases show helpful error message with text fallback option
- [ ] Images stored in Cloud Storage with metadata (user ID, timestamp, detected labels)
- [ ] Integration works in both Agent Builder chat and static demo webpage
- [ ] End-to-end latency <5 seconds (upload → detection → nutrition response)
- [ ] Free tier budget (1,000 images/month) not exceeded during demo phase
- [ ] Existing text-based workflow unaffected (no regressions)

---

## Requirements

### Functional Requirements

**FR1: Image Upload**
- FR1.1: Users can upload JPEG/PNG images up to 10MB via file picker (desktop)
- FR1.2: Image preview shown before submission
- FR1.3: Upload button disabled until valid image selected
- FR1.4: Upload progress indicator shown during processing

**FR2: Food Detection**
- FR2.1: System sends image to Google Cloud Vision API Label Detection
- FR2.2: Filter labels to food-related categories only (exclude "plate", "table", "utensils", etc.)
- FR2.3: Return only labels with 80%+ confidence score
- FR2.4: Map Vision API labels to foods in nutrition database (Local DB → CNF → USDA)
- FR2.5: If label not found in any database, exclude from results

**FR3: Portion Size Assignment**
- FR3.1: Assign standard serving sizes based on food category:
  - Fruits: "1 medium [fruit]" (e.g., "1 medium banana, 118g")
  - Proteins: "100g" (e.g., "100g chicken breast")
  - Grains: "1 cup cooked" (e.g., "1 cup cooked rice, 195g")
  - Dairy: "1 serving" (e.g., "1 serving cheese, 28g")
- FR3.2: Include gram equivalents in parentheses
- FR3.3: Default to "1 serving, 100g" for unclassified foods

**FR4: User Confirmation & Editing**
- FR4.1: Display detected foods in editable list before logging
- FR4.2: Users can remove individual food items
- FR4.3: Users can manually add foods missed by detection (text input)
- FR4.4: Users can adjust portion sizes (dropdown: 0.5x, 1x, 1.5x, 2x)
- FR4.5: "Confirm & Log" button sends final list to nutrition calculator

**FR5: Zero Food Detection Handling**
- FR5.1: If no food labels detected (or all <80% confidence), show friendly error:
  - "Hmm, I couldn't identify any food in this image."
- FR5.2: Offer alternatives:
  - "Try taking another photo with better lighting"
  - "Or describe your meal in text"
- FR5.3: Optionally show non-food labels detected (e.g., "I detected: table, plate, utensils")
- FR5.4: Provide button to switch to text input mode

**FR6: Image Storage**
- FR6.1: Upload images to Cloud Storage bucket: `gs://virtualdietitian-food-images/`
- FR6.2: Organize by date: `YYYY/MM/DD/{user_id}_{timestamp}.jpg`
- FR6.3: Store metadata in Firestore:
  - Image URL (Cloud Storage path)
  - User ID (anonymous or authenticated)
  - Upload timestamp
  - Vision API labels with confidence scores
  - Final logged foods (after user edits)
  - Nutrition calculation results
- FR6.4: Images retained for 90 days, then auto-deleted (lifecycle policy)

**FR7: Integration Points**
- FR7.1: Add "Upload Image" button to Agent Builder chat interface (if supported)
- FR7.2: Add image upload section to static demo webpage
- FR7.3: New Cloud Function endpoint: `POST /analyze-food-image`
- FR7.4: Existing `POST /analyze-nutrition` endpoint unaffected
- FR7.5: Response format consistent with text-based workflow

### Technical Requirements

**TR1: Google Cloud Vision API Setup**
- TR1.1: Enable Vision API in GCP project `virtualdietitian`
- TR1.2: Create service account with Vision API permissions
- TR1.3: Configure Label Detection feature (not Object Detection or Safe Search)
- TR1.4: Set up usage monitoring to track free tier (1,000 requests/month)

**TR2: Cloud Storage Setup**
- TR2.1: Create Cloud Storage bucket: `virtualdietitian-food-images`
- TR2.2: Configure lifecycle policy: delete objects after 90 days
- TR2.3: Set bucket permissions: private (authenticated access only)
- TR2.4: Enable CORS for demo webpage uploads

**TR3: Cloud Function Endpoint**
- TR3.1: New Cloud Function: `image-food-analyzer` (Gen2, Python 3.12)
- TR3.2: Accepts multipart/form-data (image file upload)
- TR3.3: Max request size: 10MB
- TR3.4: Timeout: 60 seconds
- TR3.5: Memory: 512Mi (same as existing function)
- TR3.6: Region: us-central1
- TR3.7: Allow unauthenticated access (demo mode)

**TR4: Python Dependencies**
- TR4.1: Add `google-cloud-vision==3.*` to requirements.txt
- TR4.2: Add `google-cloud-storage==2.*` to requirements.txt
- TR4.3: Add `Pillow==10.*` for image preprocessing (resize, format conversion)
- TR4.4: Reuse existing `requests`, `functions-framework`, `pytest` dependencies

**TR5: Food Label Mapping**
- TR5.1: Create `food_label_mapper.py` module with:
  - `VISION_API_FOOD_CATEGORIES` - whitelist of food-related labels
  - `STANDARD_SERVING_SIZES` - mapping from food category to default portions
  - `map_label_to_food(label: str) -> Optional[str]` - Vision label → database food name
  - `assign_serving_size(food_name: str, category: str) -> Dict` - portion logic

**TR6: Frontend Changes**
- TR6.1: Update `docs/demo/index.html` with image upload section:
  - File input (`<input type="file" accept="image/jpeg,image/png">`)
  - Preview canvas
  - Upload button with loading state
- TR6.2: JavaScript to handle:
  - Image selection and preview
  - FormData upload to `/analyze-food-image`
  - Display detected foods in editable table
  - Send final list to `/analyze-nutrition`

### Non-Functional Requirements

**NFR1: Performance**
- NFR1.1: Image upload and detection complete in <5 seconds (95th percentile)
- NFR1.2: Vision API call timeout: 10 seconds
- NFR1.3: Cloud Storage upload timeout: 15 seconds
- NFR1.4: Total request timeout: 60 seconds (Cloud Function limit)

**NFR2: Reliability**
- NFR2.1: Graceful degradation if Vision API unavailable (suggest text input)
- NFR2.2: Retry logic for transient Vision API errors (3 retries with exponential backoff)
- NFR2.3: Log all errors to Cloud Logging for debugging

**NFR3: Security**
- NFR3.1: Validate image file types (JPEG/PNG only, check magic bytes not just extension)
- NFR3.2: Reject images >10MB
- NFR3.3: Sanitize Vision API responses before storing
- NFR3.4: No PII (personally identifiable information) in image filenames

**NFR4: Maintainability**
- NFR4.1: 90%+ test coverage on new Python modules (`food_label_mapper.py`, `vision_client.py`)
- NFR4.2: SonarCloud quality gates passing (no code smells, no duplications >10%)
- NFR4.3: Pre-commit hooks (black, isort, flake8) enforced
- NFR4.4: Inline documentation for Vision API integration logic

**NFR5: Cost Management**
- NFR5.1: Track Vision API usage in Cloud Monitoring dashboard
- NFR5.2: Alert if approaching 1,000 requests/month (80% threshold)
- NFR5.3: Document upgrade path if free tier exceeded (LogMeal, Clarifai alternatives)

---

## User Stories

### Persona: Sarah (Busy Professional)

**Story 1: Quick Meal Logging**
> As a busy professional, I want to log my lunch by taking a photo, so that I don't waste time typing out each ingredient.

**Acceptance Criteria:**
- Sarah can upload a photo of her chicken salad from desktop
- System detects "chicken", "lettuce", "tomato", "cheese" with 80%+ confidence
- Sarah confirms the list (removes "cheese", keeps others)
- Nutrition data displayed in <5 seconds

**Story 2: Handling Ambiguous Photos**
> As a user, I want helpful feedback when my photo doesn't work, so that I know how to fix it.

**Acceptance Criteria:**
- Sarah uploads a dark, blurry photo
- System shows: "I couldn't identify food. Try better lighting or describe your meal in text."
- Sarah clicks "Describe in text" and uses existing workflow

**Story 3: Editing Detected Foods**
> As a user, I want to adjust detected foods before logging, so that I can fix mistakes.

**Acceptance Criteria:**
- System detects "apple, banana, orange"
- Sarah removes "orange" (wasn't in her bowl)
- Sarah manually adds "yogurt" (missed by detection)
- Sarah adjusts banana to "0.5x" portion (only ate half)
- Nutrition calculated with final edited list

### Persona: Dev Team (Junior Developer)

**Story 4: Testing ML Integration**
> As a developer, I want to test the Vision API integration locally, so that I can debug issues before deploying.

**Acceptance Criteria:**
- Unit tests mock Vision API responses
- Integration tests use test images in `tests/fixtures/food-images/`
- pytest runs all tests with `--cov` flag showing 90%+ coverage
- Clear error messages for Vision API failures

---

## Technical Specifications

### API Endpoint: `POST /analyze-food-image`

**Request:**
```http
POST https://image-food-analyzer-epp4v6loga-uc.a.run.app
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="image"; filename="lunch.jpg"
Content-Type: image/jpeg

[binary image data]
--boundary--
```

**Response (Success):**
```json
{
  "status": "success",
  "detected_foods": [
    {
      "label": "Chicken",
      "confidence": 0.94,
      "mapped_food": "chicken breast",
      "serving_size": "100g",
      "quantity": 1.0,
      "category": "protein"
    },
    {
      "label": "Rice",
      "confidence": 0.87,
      "mapped_food": "rice",
      "serving_size": "1 cup cooked (195g)",
      "quantity": 1.0,
      "category": "grain"
    }
  ],
  "image_url": "gs://virtualdietitian-food-images/2025/10/15/user123_1729012345.jpg",
  "message": "Found 2 food items. Review and confirm before logging."
}
```

**Response (No Food Detected):**
```json
{
  "status": "no_food_detected",
  "detected_foods": [],
  "message": "I couldn't identify any food in this image.",
  "suggestions": [
    "Try taking another photo with better lighting or closer angle",
    "Describe your meal in text instead"
  ],
  "detected_objects": ["Table", "Plate", "Fork"],
  "image_url": "gs://virtualdietitian-food-images/2025/10/15/user123_1729012345.jpg"
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "Vision API unavailable. Please try again or use text input.",
  "fallback_url": "/analyze-nutrition"
}
```

### Vision API Integration

**Python Code Example:**
```python
"""Google Cloud Vision API client for food detection."""

from typing import Dict, List, Optional
from google.cloud import vision
import io

class VisionFoodDetector:
    """Detect food items in images using Google Cloud Vision API."""

    # Whitelist of food-related labels (not exhaustive, expand as needed)
    FOOD_CATEGORIES = {
        "food", "dish", "cuisine", "ingredient", "fruit", "vegetable",
        "meat", "poultry", "seafood", "dairy", "grain", "bread", "pasta",
        "rice", "salad", "soup", "dessert", "snack", "beverage"
    }

    def __init__(self):
        """Initialize Vision API client."""
        self.client = vision.ImageAnnotatorClient()

    def detect_food(self, image_bytes: bytes, min_confidence: float = 0.8) -> List[Dict]:
        """
        Detect food items in image.

        Args:
            image_bytes: Raw image bytes (JPEG/PNG)
            min_confidence: Minimum confidence threshold (0.0 to 1.0)

        Returns:
            List of detected food labels:
            [
                {"label": "Chicken", "confidence": 0.94, "category": "protein"},
                {"label": "Rice", "confidence": 0.87, "category": "grain"}
            ]
        """
        # Build Vision API request
        image = vision.Image(content=image_bytes)
        response = self.client.label_detection(image=image, max_results=20)

        food_labels = []

        for label in response.label_annotations:
            # Filter: food-related labels only
            if not self._is_food_label(label.description):
                continue

            # Filter: confidence threshold
            if label.score < min_confidence:
                continue

            food_labels.append({
                "label": label.description,
                "confidence": label.score,
                "category": self._infer_category(label.description)
            })

        return food_labels

    def _is_food_label(self, label: str) -> bool:
        """Check if label is food-related."""
        label_lower = label.lower()

        # Check if label contains any food category keyword
        for food_keyword in self.FOOD_CATEGORIES:
            if food_keyword in label_lower:
                return True

        # Exclude common non-food items
        non_food = {"plate", "table", "fork", "knife", "spoon", "bowl", "cup"}
        if label_lower in non_food:
            return False

        return False  # Default: not food

    def _infer_category(self, label: str) -> str:
        """Infer food category from label (for serving size assignment)."""
        label_lower = label.lower()

        if any(word in label_lower for word in ["chicken", "beef", "pork", "fish", "egg"]):
            return "protein"
        elif any(word in label_lower for word in ["rice", "pasta", "bread", "grain"]):
            return "grain"
        elif any(word in label_lower for word in ["apple", "banana", "orange", "berry"]):
            return "fruit"
        elif any(word in label_lower for word in ["broccoli", "carrot", "lettuce", "tomato"]):
            return "vegetable"
        elif any(word in label_lower for word in ["cheese", "milk", "yogurt"]):
            return "dairy"
        else:
            return "other"
```

### Standard Serving Sizes Mapping

**Configuration (food_label_mapper.py):**
```python
"""Map Vision API labels to nutrition database foods with standard serving sizes."""

from typing import Dict, Optional

# Map food categories to standard serving sizes
STANDARD_SERVING_SIZES = {
    "fruit": {
        "apple": {"serving": "1 medium apple", "grams": 182},
        "banana": {"serving": "1 medium banana", "grams": 118},
        "orange": {"serving": "1 medium orange", "grams": 131},
        "_default": {"serving": "1 medium fruit", "grams": 150}
    },
    "protein": {
        "_default": {"serving": "100g", "grams": 100}
    },
    "grain": {
        "rice": {"serving": "1 cup cooked", "grams": 195},
        "pasta": {"serving": "1 cup cooked", "grams": 140},
        "_default": {"serving": "1 cup cooked", "grams": 150}
    },
    "vegetable": {
        "_default": {"serving": "1 cup", "grams": 100}
    },
    "dairy": {
        "cheese": {"serving": "1 serving", "grams": 28},
        "_default": {"serving": "1 serving", "grams": 100}
    },
    "other": {
        "_default": {"serving": "1 serving", "grams": 100}
    }
}

def assign_serving_size(food_name: str, category: str) -> Dict:
    """
    Assign standard serving size based on food and category.

    Args:
        food_name: Name of food (e.g., "chicken breast", "banana")
        category: Food category (e.g., "protein", "fruit")

    Returns:
        {"serving_size": "1 medium banana (118g)", "grams": 118}
    """
    category_servings = STANDARD_SERVING_SIZES.get(category, STANDARD_SERVING_SIZES["other"])

    # Try exact match first
    if food_name in category_servings:
        serving_data = category_servings[food_name]
    else:
        # Use category default
        serving_data = category_servings["_default"]

    return {
        "serving_size": f"{serving_data['serving']} ({serving_data['grams']}g)",
        "grams": serving_data["grams"]
    }
```

### Frontend Integration (Demo Webpage)

**HTML Addition (docs/demo/index.html):**
```html
<!-- Image Upload Section (add after existing meal description input) -->
<div class="upload-section">
  <h3>Or Upload a Photo</h3>

  <input type="file" id="imageInput" accept="image/jpeg,image/png" style="display:none">
  <button id="selectImageBtn" class="btn btn-secondary">Select Image</button>

  <div id="imagePreview" style="display:none; margin-top: 10px;">
    <img id="previewImg" style="max-width: 400px; max-height: 300px;">
    <button id="uploadImageBtn" class="btn btn-primary">Analyze Image</button>
  </div>

  <div id="detectedFoods" style="display:none; margin-top: 20px;">
    <h4>Detected Foods</h4>
    <table id="foodTable" class="table">
      <thead>
        <tr>
          <th>Food</th>
          <th>Serving Size</th>
          <th>Portion</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody id="foodTableBody"></tbody>
    </table>
    <button id="confirmFoodsBtn" class="btn btn-success">Confirm & Log Nutrition</button>
  </div>

  <div id="uploadError" class="alert alert-warning" style="display:none;"></div>
</div>
```

**JavaScript Example:**
```javascript
// Handle image upload and detection
document.getElementById('selectImageBtn').addEventListener('click', () => {
  document.getElementById('imageInput').click();
});

document.getElementById('imageInput').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;

  // Show preview
  const reader = new FileReader();
  reader.onload = (e) => {
    document.getElementById('previewImg').src = e.target.result;
    document.getElementById('imagePreview').style.display = 'block';
  };
  reader.readAsDataURL(file);
});

document.getElementById('uploadImageBtn').addEventListener('click', async () => {
  const file = document.getElementById('imageInput').files[0];
  if (!file) return;

  // Show loading state
  const btn = document.getElementById('uploadImageBtn');
  btn.disabled = true;
  btn.textContent = 'Analyzing...';

  // Upload to Cloud Function
  const formData = new FormData();
  formData.append('image', file);

  try {
    const response = await fetch('https://image-food-analyzer-epp4v6loga-uc.a.run.app', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();

    if (result.status === 'success') {
      displayDetectedFoods(result.detected_foods);
    } else if (result.status === 'no_food_detected') {
      showError(result.message, result.suggestions);
    } else {
      showError(result.error);
    }
  } catch (error) {
    showError('Upload failed. Please try again or use text input.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analyze Image';
  }
});

function displayDetectedFoods(foods) {
  const tbody = document.getElementById('foodTableBody');
  tbody.innerHTML = '';

  foods.forEach((food, index) => {
    const row = tbody.insertRow();
    row.innerHTML = `
      <td>${food.mapped_food}</td>
      <td>${food.serving_size}</td>
      <td>
        <select id="portion_${index}">
          <option value="0.5">0.5x</option>
          <option value="1" selected>1x</option>
          <option value="1.5">1.5x</option>
          <option value="2">2x</option>
        </select>
      </td>
      <td><button onclick="removeFood(${index})">Remove</button></td>
    `;
  });

  document.getElementById('detectedFoods').style.display = 'block';
}

function showError(message, suggestions = []) {
  const errorDiv = document.getElementById('uploadError');
  errorDiv.innerHTML = `
    <p>${message}</p>
    ${suggestions.map(s => `<li>${s}</li>`).join('')}
  `;
  errorDiv.style.display = 'block';
}
```

---

## Dependencies

### External Dependencies
- **Google Cloud Vision API** - Label detection for food identification
- **Google Cloud Storage** - Image storage with lifecycle policies
- **GCP Project:** `virtualdietitian` (existing)
- **Service Account:** New account with Vision API + Storage permissions

### Internal Dependencies
- **Existing nutrition calculator** (`nutrition_calculator.py`) - Reuse for final nutrition calculation
- **Existing 3-tier fallback** (Local DB → CNF → USDA) - Map Vision labels to foods
- **Existing rule engine** (`rule_engine.py`) - Generate insights from detected meal
- **Agent Builder integration** - Optional: add image upload to chat interface

### Python Libraries (new)
- `google-cloud-vision==3.*`
- `google-cloud-storage==2.*`
- `Pillow==10.*`

---

## Timeline

### Phase 1: Foundation (Week 1) - 12 hours
- **Hour 1-2:** GCP setup (enable Vision API, create service account, Cloud Storage bucket)
- **Hour 3-5:** Build `vision_client.py` with unit tests (mock Vision API responses)
- **Hour 6-8:** Build `food_label_mapper.py` with serving size logic and tests
- **Hour 9-10:** Create Cloud Function `image-food-analyzer` endpoint (image upload → Vision → storage)
- **Hour 11-12:** Integration test with sample food images

### Phase 2: Frontend Integration (Week 1) - 8 hours
- **Hour 1-3:** Update demo webpage HTML/CSS for image upload section
- **Hour 4-6:** JavaScript for image preview, upload, detected foods table
- **Hour 7-8:** End-to-end testing (upload → detect → edit → log nutrition)

### Phase 3: Edge Cases & Polish (Week 2) - 8 hours
- **Hour 1-2:** Implement zero-food-detected error handling
- **Hour 3-4:** Add Vision API retry logic and error logging
- **Hour 5-6:** Cost monitoring dashboard (Cloud Monitoring alerts)
- **Hour 7-8:** Documentation (README update, API docs, demo video)

### Phase 4: Testing & Deployment (Week 2) - 4 hours
- **Hour 1-2:** SonarCloud quality gates (ensure 90%+ coverage, no code smells)
- **Hour 3:** Deploy to Cloud Functions (experimental branch)
- **Hour 4:** User acceptance testing with 10 sample food images

**Total Estimate:** 32 hours (~1 week for solo developer, ~4 days for pair programming)

---

## Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation Strategy |
|------|--------|------------|---------------------|
| **Vision API poor food detection accuracy** | High - Users get frustrated, abandon feature | Medium | Test with 50+ diverse food images before launch; document accuracy metrics; prepare LogMeal upgrade path if <70% accuracy |
| **Free tier (1,000 images/month) exceeded** | Medium - Unexpected costs | Low (demo phase) | Set Cloud Monitoring alert at 800 requests/month; implement rate limiting (10 uploads/user/day); display usage warning in UI |
| **Vision API downtime** | Medium - Feature unavailable | Low (99.9% SLA) | Implement retry logic (3 attempts); graceful fallback to text input; clear error messaging |
| **Image uploads timeout (>60s)** | Medium - Poor UX | Low | Resize large images client-side before upload (max 1024x1024); compress JPEG quality to 85%; use async processing if needed |
| **Serving size estimates inaccurate** | High - Nutrition data wrong | High | Clearly label as "estimated standard serving"; allow users to edit portions; add disclaimer: "Adjust portions for accuracy" |
| **Storage costs grow unexpectedly** | Low - Cloud Storage cheap | Medium | Enforce 10MB image size limit; 90-day lifecycle policy; monitor storage usage in dashboard |
| **Agent Builder doesn't support image upload** | Medium - Can't integrate with chat | Medium | Focus on demo webpage first; document Agent Builder limitations; file feature request with Google |

---

## Out of Scope

The following features are **explicitly excluded** from this initial version:

❌ **Mobile app camera integration** - Desktop file picker only (Phase 4 consideration)
❌ **Real-time portion size estimation** - Standard servings only (requires LogMeal API, $$$)
❌ **Multiple food detection confidence UI** - Show single confidence score per food, not per-nutrient confidence
❌ **Custom ML model training** - Use Vision API out-of-box (gather images for future training)
❌ **Barcode scanning** - Image-based only, no nutrition label OCR
❌ **Video upload** - Static images only
❌ **Social sharing** - No "share my meal" functionality
❌ **Meal history browsing** - No image gallery or past meal retrieval (Phase 3: persistence)
❌ **Multi-user authentication** - Anonymous uploads only (add user IDs when auth implemented)
❌ **Recipe suggestions** - No "similar meals" or "healthier alternatives" based on image

---

## Acceptance Criteria

### Grouped Validation Criteria

**Image Upload & Processing:**
- [ ] User can select JPEG/PNG image via file picker (desktop)
- [ ] Image preview displays before upload
- [ ] Upload completes in <5 seconds (95th percentile)
- [ ] Images >10MB rejected with clear error message
- [ ] Invalid file types (PDF, GIF) rejected with error

**Food Detection:**
- [ ] Vision API detects 2+ food items in 80% of test cases (50 test images)
- [ ] Only labels with 80%+ confidence returned
- [ ] Non-food labels (plate, table, fork) filtered out
- [ ] Detected labels mapped to foods in nutrition database (Local → CNF → USDA)
- [ ] Labels not found in any database excluded from results

**Serving Size Assignment:**
- [ ] Fruits assigned: "1 medium [fruit] (Xg)" (e.g., "1 medium banana (118g)")
- [ ] Proteins assigned: "100g"
- [ ] Grains assigned: "1 cup cooked (Xg)"
- [ ] Dairy assigned: "1 serving (28g)" for cheese, "100g" for others
- [ ] Unknown foods default to: "1 serving (100g)"

**User Editing:**
- [ ] Detected foods displayed in editable table
- [ ] User can remove individual foods
- [ ] User can adjust portion sizes (0.5x, 1x, 1.5x, 2x dropdown)
- [ ] User can manually add foods via text input (missed by detection)
- [ ] "Confirm & Log" button sends final list to `/analyze-nutrition` endpoint

**Zero Food Detection:**
- [ ] Friendly error message shown: "I couldn't identify any food in this image."
- [ ] Suggestions displayed: "Try better lighting" and "Describe your meal in text"
- [ ] Optional: Non-food labels shown (e.g., "I detected: table, plate")
- [ ] "Switch to text input" button returns user to existing workflow

**Image Storage:**
- [ ] Images uploaded to Cloud Storage: `gs://virtualdietitian-food-images/YYYY/MM/DD/{user_id}_{timestamp}.jpg`
- [ ] Metadata stored in Firestore (image URL, timestamp, Vision labels, logged foods, nutrition results)
- [ ] Lifecycle policy auto-deletes images after 90 days
- [ ] Storage usage <1GB during demo phase

**Integration:**
- [ ] Demo webpage (`docs/demo/index.html`) includes image upload section
- [ ] New Cloud Function `image-food-analyzer` deployed to us-central1
- [ ] Existing `/analyze-nutrition` endpoint works with image-detected foods
- [ ] End-to-end flow: upload → detect → edit → nutrition → insights

**Cost & Performance:**
- [ ] Free tier (1,000 images/month) not exceeded during demo
- [ ] Cloud Monitoring alert configured at 800 requests/month
- [ ] End-to-end latency <5 seconds (upload → nutrition response)
- [ ] Vision API calls timeout at 10 seconds with retry logic

**Quality:**
- [ ] 90%+ test coverage on `vision_client.py` and `food_label_mapper.py`
- [ ] SonarCloud quality gates passing (no code smells, <10% duplication)
- [ ] Pre-commit hooks enforced (black, isort, flake8)
- [ ] All 93+ existing tests still passing (no regressions)

---

## Open Questions

1. **Agent Builder image upload:** Does Vertex AI Agent Builder support image upload in chat interface? If not, demo webpage only?
   - **Action:** Research Agent Builder multimodal capabilities, file feature request if needed

2. **User authentication:** How to associate images with users if no auth system exists yet?
   - **Action:** Use anonymous user IDs for now (generate UUID client-side), add proper auth in Phase 3

3. **Vision API accuracy testing:** What's acceptable accuracy threshold for launch (70%? 80%? 90%)?
   - **Action:** Run pilot test with 50 diverse food images, measure precision/recall, set baseline

4. **LogMeal upgrade path:** If Vision API accuracy <70%, when to switch to specialized food API?
   - **Action:** Define decision criteria: if accuracy <70% after 100 test images → upgrade to LogMeal trial

5. **Firestore vs Cloud SQL:** Store image metadata in Firestore (NoSQL) or Cloud SQL (relational)?
   - **Action:** Use Firestore for demo (simpler, no schema), migrate to Cloud SQL in Phase 3 if relational queries needed

6. **Image compression:** Should images be compressed server-side before storage?
   - **Action:** Yes, use Pillow to resize to max 1024x1024 and compress JPEG quality to 85% (reduce storage costs)

7. **Multi-language support:** Should Vision API detect non-English food labels (e.g., "poulet" → "chicken")?
   - **Action:** Vision API returns English labels only; existing translation dictionary handles text input; no change needed

---

## Related Work

- **PRD:** `docs/features/image-food-logging-PLANNED/prd.md` (this document)
- **GitHub Issues:** TBD (create after PRD approval)
- **Experimental Branch:** `feature/image-food-logging`
- **Reference Documentation:**
  - [Google Cloud Vision API Docs](https://cloud.google.com/vision/docs)
  - [Vision API Label Detection](https://cloud.google.com/vision/docs/labels)
  - [Cloud Storage Lifecycle Policies](https://cloud.google.com/storage/docs/lifecycle)

---

**Next Steps:**
1. Review PRD with stakeholders (user approval required)
2. Break down into GitHub issues using `generate-tasks.md` (if user approves)
3. Create experimental branch: `git checkout -b feature/image-food-logging`
4. Begin Phase 1: GCP setup and Vision API integration

---

*PRD created using Claude Code following create-prd.md guidelines*
*Target: Junior developer implementation*
*Status: PLANNED - Awaiting approval*
