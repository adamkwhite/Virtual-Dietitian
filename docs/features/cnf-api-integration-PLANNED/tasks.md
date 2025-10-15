# CNF API Integration - Tasks

**Based on PRD:** `cnf-api-integration-PLANNED/prd.md`
**Status:** PLANNED
**Created:** 2025-10-14

---

## Relevant Files

### New Files
- `cloud-functions/nutrition-analyzer/cnf_client.py` - Canadian Nutrient File API client module
- `cloud-functions/nutrition-analyzer/test_cnf_client.py` - Unit tests for CNF client

### Modified Files
- `cloud-functions/nutrition-analyzer/nutrition_calculator.py` - Add CNF as middle tier in fallback logic
- `cloud-functions/nutrition-analyzer/main.py` - Update feature flag handling for CNF
- `cloud-functions/nutrition-analyzer/requirements.txt` - Add dependencies if needed (likely none)
- `README.md` - Add CNF setup instructions and environment variables
- `CLAUDE.md` - Update technology stack and API integrations section
- `docs/deployment/cloud-function-deployment.md` - Add CNF environment variable configuration

### Reference Files
- `cloud-functions/nutrition-analyzer/usda_client.py` - Reference implementation for structure and patterns
- `cloud-functions/nutrition-analyzer/test_usda_client.py` - Reference for test structure (when created)

### Notes

- Follow existing code style: black, isort, flake8
- Use pytest for unit tests with pytest-cov for coverage
- CNF client should mirror USDA client structure for consistency
- All API calls should have 5-second timeout
- Error handling should be graceful (log and continue to next tier)

---

## Tasks

- [ ] 1.0 Create CNF API Client Module
  - [ ] 1.1 Create `cloud-functions/nutrition-analyzer/cnf_client.py` file
  - [ ] 1.2 Implement `CNFClient` class with `__init__` method accepting optional API key
  - [ ] 1.3 Add `BASE_URL` constant for CNF API endpoint
  - [ ] 1.4 Implement `search_food(query, lang="en")` method to search CNF database
  - [ ] 1.5 Implement `get_nutrition_per_100g(food_name)` method as main entry point
  - [ ] 1.6 Implement `_normalize_nutrient_data(cnf_data)` to map CNF fields to our schema
  - [ ] 1.7 Implement `_infer_category(nutrition)` method (copy logic from USDA client)
  - [ ] 1.8 Add in-memory cache dictionary (`self._cache`) in `__init__`
  - [ ] 1.9 Add cache check at start of `get_nutrition_per_100g` method
  - [ ] 1.10 Add cache storage after successful API call
  - [ ] 1.11 Implement singleton pattern: `get_cnf_client()` function
  - [ ] 1.12 Add error handling with try/except for all HTTP requests
  - [ ] 1.13 Add 5-second timeout to all `requests.get()` calls
  - [ ] 1.14 Add logging for API errors (print statements for Cloud Function logs)
  - [ ] 1.15 Add docstrings to all methods following existing style

- [ ] 2.0 Update Nutrition Calculator with 3-Tier Fallback Logic
  - [ ] 2.1 Import `get_cnf_client` from `cnf_client` in `nutrition_calculator.py`
  - [ ] 2.2 Add `ENABLE_CNF_API` environment variable check (after imports)
  - [ ] 2.3 Locate the fallback logic in `calculate_nutrition()` function
  - [ ] 2.4 Insert CNF tier between local database and USDA checks
  - [ ] 2.5 Add conditional: `if ENABLE_CNF_API:` before CNF logic
  - [ ] 2.6 Call `get_cnf_client().get_nutrition_per_100g(food_name)`
  - [ ] 2.7 Check if CNF returned valid data (not None)
  - [ ] 2.8 If CNF succeeds, use the data and `continue` to next food item
  - [ ] 2.9 If CNF fails/disabled, fall through to existing USDA logic
  - [ ] 2.10 Ensure unknown_foods list only populated when all tiers fail
  - [ ] 2.11 Test logic flow: local → CNF → USDA → error

- [ ] 3.0 Add Environment Configuration and Feature Flags
  - [ ] 3.1 Update `main.py` to read `ENABLE_CNF_API` from environment
  - [ ] 3.2 Update `main.py` to read `CNF_API_KEY` from environment
  - [ ] 3.3 Add environment variable defaults (`ENABLE_CNF_API` defaults to "false")
  - [ ] 3.4 Document environment variables in code comments
  - [ ] 3.5 Create `.env.example` file if doesn't exist, add CNF variables
  - [ ] 3.6 Update local development `.env` file with CNF placeholders
  - [ ] 3.7 Test environment variable reading works correctly

- [ ] 4.0 Write Unit Tests for CNF Client
  - [ ] 4.1 Create `cloud-functions/nutrition-analyzer/test_cnf_client.py` file
  - [ ] 4.2 Import pytest, CNFClient, and necessary mocking libraries
  - [ ] 4.3 Write test: `test_cnf_client_initialization()` - verify API key handling
  - [ ] 4.4 Write test: `test_search_food_success()` - mock successful API search
  - [ ] 4.5 Write test: `test_search_food_api_error()` - mock API failure, verify graceful handling
  - [ ] 4.6 Write test: `test_get_nutrition_per_100g_success()` - mock successful nutrition retrieval
  - [ ] 4.7 Write test: `test_get_nutrition_per_100g_not_found()` - verify returns None when food not found
  - [ ] 4.8 Write test: `test_get_nutrition_per_100g_cached()` - verify cache hit returns cached data
  - [ ] 4.9 Write test: `test_normalize_nutrient_data()` - verify field mapping works correctly
  - [ ] 4.10 Write test: `test_infer_category()` - verify category inference for different food types
  - [ ] 4.11 Write test: `test_timeout_handling()` - verify 5-second timeout is respected
  - [ ] 4.12 Use `pytest.MonkeyPatch` or `unittest.mock.patch` for mocking requests
  - [ ] 4.13 Run tests: `pytest cloud-functions/nutrition-analyzer/test_cnf_client.py -v`
  - [ ] 4.14 Check coverage: `pytest --cov=cnf_client test_cnf_client.py`
  - [ ] 4.15 Ensure coverage is >80%, add tests if needed

- [ ] 5.0 Update Documentation and Deployment Guides
  - [ ] 5.1 Update README.md "Environment Variables" section with CNF variables
  - [ ] 5.2 Add "Obtaining CNF API Credentials" section to README or separate doc
  - [ ] 5.3 Document 3-tier fallback architecture in README
  - [ ] 5.4 Update CLAUDE.md "Technology Stack" with CNF API
  - [ ] 5.5 Update CLAUDE.md "APIs" section with CNF details
  - [ ] 5.6 Create or update `docs/deployment/environment-variables.md`
  - [ ] 5.7 Add CNF troubleshooting section: common errors and solutions
  - [ ] 5.8 Document how to test CNF locally without real API key (using mocks)
  - [ ] 5.9 Add example Cloud Function deployment command with CNF env vars
  - [ ] 5.10 Update `agent-config/SETUP_GUIDE_UPDATED.md` if CNF affects Agent Builder setup

- [ ] 6.0 Deploy and Validate in Cloud Function Environment
  - [ ] 6.1 Obtain CNF API credentials from Health Canada
  - [ ] 6.2 Test CNF client locally with real API key and sample queries
  - [ ] 6.3 Verify local 3-tier fallback works: local → CNF → USDA
  - [ ] 6.4 Run full test suite locally: `pytest cloud-functions/nutrition-analyzer/`
  - [ ] 6.5 Run linting: `black`, `isort`, `flake8` on modified files
  - [ ] 6.6 Set CNF environment variables in Cloud Function deployment
  - [ ] 6.7 Deploy to Cloud Function: `gcloud functions deploy nutrition-analyzer --set-env-vars ENABLE_CNF_API=true,CNF_API_KEY=xxx`
  - [ ] 6.8 Test deployed webhook directly with curl/Postman
  - [ ] 6.9 Test with Agent Builder using common foods
  - [ ] 6.10 Test fallback behavior: disable CNF, verify USDA works
  - [ ] 6.11 Test error handling: use invalid API key, verify graceful degradation
  - [ ] 6.12 Verify response times: <1s first call, <100ms cached
  - [ ] 6.13 Check Cloud Function logs for any errors or warnings
  - [ ] 6.14 Document any issues found and resolutions in implementation notes

---

## Implementation Notes

**Development Order:**
1. Start with Task 1 (CNF Client) - this is the foundation
2. Add unit tests (Task 4) alongside development for TDD approach
3. Update fallback logic (Task 2) once client is working
4. Add configuration (Task 3)
5. Update docs (Task 5)
6. Deploy and validate (Task 6)

**Testing Strategy:**
- Use mocks for all external API calls in unit tests
- Test locally with real API before deploying
- Keep USDA as safety net during CNF development

**Rollback Plan:**
- If CNF causes issues in production, set `ENABLE_CNF_API=false`
- System falls back to existing local → USDA flow
- Zero downtime rollback

**Time Estimates:**
- Task 1: 1.5 hours
- Task 2: 1 hour
- Task 3: 30 minutes
- Task 4: 1.5 hours
- Task 5: 1 hour
- Task 6: 1.5 hours
- **Total: ~7 hours**
