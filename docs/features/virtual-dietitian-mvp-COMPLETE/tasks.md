# Virtual Dietitian MVP - Task List

**Based on PRD:** `prd.md`
**Target Timeline:** 2-3 hours
**Last Updated:** October 12, 2025

---

## Relevant Files

### Data Files
- `data/nutrition_db.json` - Static JSON database with 50 common foods and their nutritional information
- `data/food_categories.json` - Food category mappings for rule engine (optional)

### Cloud Function (Webhook)
- `cloud-functions/nutrition-analyzer/main.py` - Cloud Function entry point and request handler
- `cloud-functions/nutrition-analyzer/nutrition_calculator.py` - Nutrient aggregation logic
- `cloud-functions/nutrition-analyzer/rule_engine.py` - Tiered rule engine implementation (3 rule types)
- `cloud-functions/nutrition-analyzer/requirements.txt` - Python dependencies
- `cloud-functions/nutrition-analyzer/test_nutrition_calculator.py` - Unit tests for nutrient calculations
- `cloud-functions/nutrition-analyzer/test_rule_engine.py` - Unit tests for rule logic

### Agent Configuration
- `agent-config/agent-instructions.txt` - Vertex AI Agent Builder prompt/instructions
- `agent-config/webhook-config.json` - Webhook integration configuration
- `agent-config/datastore-schema.json` - Vertex AI Search datastore schema definition

### Documentation
- `docs/architecture/data-flow-diagram.md` - Architecture diagram and explanation
- `docs/architecture/separation-of-concerns.md` - LLM vs deterministic logic explanation
- `docs/architecture/scalability-notes.md` - 1 to 1M users scaling approach
- `docs/demo/demo-script.md` - Demo walkthrough script for video recording
- `README.md` - Project overview with quick start instructions

### Scripts
- `scripts/setup_gcp.sh` - GCP project initialization script
- `scripts/deploy_function.sh` - Cloud Function deployment script
- `scripts/upload_datastore.sh` - Upload nutrition database to Vertex AI Search

### Notes

- Unit tests should be placed alongside the code files they are testing
- Use `pytest` for Python unit tests in the Cloud Function
- GCP deployment uses `gcloud` CLI commands
- Vertex AI Agent Builder configuration is done via GCP Console (UI)

---

## Tasks

### Session 1: GCP Setup & Environment Configuration (30 min)

- [ ] 1.0 GCP Project Setup & Environment Configuration
  - [ ] 1.1 Create new GCP project or select existing project
  - [ ] 1.2 Enable required APIs (Vertex AI Agent Builder, Cloud Functions, Vertex AI Search, Cloud Storage)
  - [ ] 1.3 Set up billing account and verify quotas
  - [ ] 1.4 Configure `gcloud` CLI with project ID and default region (us-central1)
  - [ ] 1.5 Create service account with necessary permissions (Agent Builder Admin, Cloud Functions Developer)
  - [ ] 1.6 Create GCS bucket for Cloud Function source code storage
  - [ ] 1.7 Initialize local project structure (create directories: `data/`, `cloud-functions/`, `agent-config/`, `scripts/`)
  - [ ] 1.8 Test basic GCP connectivity with `gcloud projects describe [PROJECT_ID]`

### Session 2: Nutrition Database Creation (30 min)

- [ ] 2.0 Nutrition Database Creation
  - [ ] 2.1 Research and identify 50 common foods across 6 categories (proteins, grains, fruits, vegetables, dairy, fats)
  - [ ] 2.2 Create `data/nutrition_db.json` with schema: `id`, `name`, `category`, `serving_size_g`, `nutrition` object
  - [ ] 2.3 Populate nutrition data for proteins (10 foods): chicken, salmon, tofu, eggs, Greek yogurt, almonds, etc.
  - [ ] 2.4 Populate nutrition data for grains (8 foods): oatmeal, rice, quinoa, whole wheat bread, pasta, etc.
  - [ ] 2.5 Populate nutrition data for fruits (8 foods): apple, banana, blueberries, strawberries, orange, etc.
  - [ ] 2.6 Populate nutrition data for vegetables (10 foods): broccoli, spinach, carrots, tomato, avocado, etc.
  - [ ] 2.7 Populate nutrition data for dairy (6 foods): milk, cheese, butter, yogurt, etc.
  - [ ] 2.8 Populate nutrition data for fats (4 foods): olive oil, almond butter, peanut butter, coconut oil
  - [ ] 2.9 Add common food aliases/synonyms to support variations (e.g., "oats" vs "oatmeal")
  - [ ] 2.10 Validate JSON schema and ensure all entries have required fields (calories, protein, carbs, fat, fiber, sodium)

### Session 3: Cloud Function Webhook Development (45 min)

- [ ] 3.0 Cloud Function Webhook Development
  - [ ] 3.1 Create `cloud-functions/nutrition-analyzer/main.py` with Flask request handler
  - [ ] 3.2 Implement request parsing to extract food items from Agent Builder webhook payload
  - [ ] 3.3 Create `nutrition_calculator.py` with nutrient aggregation function (sum calories, macros, micros)
  - [ ] 3.4 Implement macro percentage calculation (protein/carbs/fat as % of total calories)
  - [ ] 3.5 Create `rule_engine.py` with base Rule class structure
  - [ ] 3.6 Implement Rule Type 1: Category Detection (fruit → vitamin insight, grain → fiber insight)
  - [ ] 3.7 Implement Rule Type 2: Threshold Warnings (sodium > 800mg, sugar > 50g, saturated fat > 20g)
  - [ ] 3.8 Implement Rule Type 3: Macro Ratio Recommendations (protein < 15% or > 35%, suggest adjustments)
  - [ ] 3.9 Create webhook response formatter with structure: `total_nutrition`, `macro_percentages`, `insights[]`, `follow_up`
  - [ ] 3.10 Add error handling for unknown foods, missing data, malformed requests
  - [ ] 3.11 Create `requirements.txt` with dependencies (Flask, pytest, requests)
  - [ ] 3.12 Write unit tests in `test_nutrition_calculator.py` (test aggregation with 5 meal scenarios)
  - [ ] 3.13 Write unit tests in `test_rule_engine.py` (test each rule type with edge cases)
  - [ ] 3.14 Run local tests with `pytest` and verify 100% pass rate
  - [ ] 3.15 Create `scripts/deploy_function.sh` with `gcloud functions deploy` command
  - [ ] 3.16 Deploy Cloud Function to GCP with HTTP trigger and test endpoint with curl

### Session 4: Vertex AI Agent Builder Configuration (45 min)

- [ ] 4.0 Vertex AI Agent Builder Configuration
  - [ ] 4.1 Navigate to Vertex AI Agent Builder in GCP Console
  - [ ] 4.2 Create new agent with name "Virtual Dietitian MVP"
  - [ ] 4.3 Configure agent greeting message and default fallback responses
  - [ ] 4.4 Create Vertex AI Search datastore for nutrition database
  - [ ] 4.5 Upload `data/nutrition_db.json` to datastore using `scripts/upload_datastore.sh`
  - [ ] 4.6 Configure datastore schema mapping (food name, nutrition fields, category)
  - [ ] 4.7 Create agent intent: `log_meal` with training phrases (10+ examples like "I ate X", "I had Y for lunch")
  - [ ] 4.8 Write agent instructions in `agent-config/agent-instructions.txt` (extract food items, quantities, call webhook)
  - [ ] 4.9 Configure webhook integration: add Cloud Function URL, set authentication
  - [ ] 4.10 Map webhook parameters: send `food_items[]` array to Cloud Function
  - [ ] 4.11 Configure webhook response handling: use `insights[]` and `follow_up` in agent reply
  - [ ] 4.12 Write response template for natural language generation (include calorie breakdown, insights, follow-up)
  - [ ] 4.13 Test agent in Agent Builder simulator with "I had oatmeal with blueberries"
  - [ ] 4.14 Debug and refine agent instructions based on test results
  - [ ] 4.15 Test edge cases: unknown food, ambiguous input, multiple meals
  - [ ] 4.16 Publish agent and obtain public shareable link

### Session 5: End-to-End Testing & Demo Preparation (30 min)

- [ ] 5.0 End-to-End Testing & Demo Preparation
  - [ ] 5.1 Run Test Case 1: Balanced breakfast (oatmeal, blueberries, almond butter) - verify vitamin insight
  - [ ] 5.2 Run Test Case 2: High sodium meal (bacon, sausage, cheese) - verify sodium warning
  - [ ] 5.3 Run Test Case 3: Protein-rich meal (chicken, quinoa, broccoli) - verify positive feedback
  - [ ] 5.4 Run Test Case 4: Fruit snack (apple, banana) - verify protein recommendation
  - [ ] 5.5 Run Test Case 5: Unknown food - verify graceful fallback
  - [ ] 5.6 Document test results and any issues in `docs/testing/test-results.md`
  - [ ] 5.7 Create architecture diagram in `docs/architecture/data-flow-diagram.md` (user → agent → datastore → webhook → response)
  - [ ] 5.8 Write `docs/architecture/separation-of-concerns.md` explaining LLM vs rule engine responsibilities
  - [ ] 5.9 Write `docs/architecture/scalability-notes.md` with 1/10K/1M user scaling approach
  - [ ] 5.10 Create demo script in `docs/demo/demo-script.md` with 3 example interactions
  - [ ] 5.11 Record 2-3 minute demo video showing agent interaction, webhook logs, and architecture
  - [ ] 5.12 Update `README.md` with project overview, quick start, demo link, architecture summary
  - [ ] 5.13 Commit all code and documentation to GitHub with meaningful commit message
  - [ ] 5.14 Verify agent public link is accessible and functional
