# Canadian Nutrient File (CNF) API Integration - PRD

**Status:** PLANNED
**Created:** 2025-10-14
**Owner:** adamkwhite
**Priority:** Medium

---

## Overview

Add the Canadian Nutrient File (CNF) API as a secondary fallback nutrition data source between the local nutrition database and USDA FoodData Central API. This creates a 3-tier lookup system: local nutrition_db.json → CNF API → USDA API, improving overall food recognition rates while providing better coverage for both Canadian and international foods.

---

## Problem Statement

The current nutrition lookup system has only 2 tiers:
1. Local nutrition database (47 foods)
2. USDA FoodData Central API (500,000+ foods)

**Limitations:**
- USDA API sometimes has availability issues or rate limits
- Single external API dependency creates a single point of failure
- No redundancy if USDA API is unavailable

**Context:**
- This is a demo application for stakeholder presentation
- Primary goal is demonstrating robust architecture with fallback mechanisms
- Success depends on reliable API responses during demos

**Why CNF:**
- Health Canada's official nutrition database
- Well-documented REST API
- Provides additional coverage and redundancy
- Demonstrates multi-source data integration capability

---

## Goals

### Primary Goals
1. Improve food recognition reliability by adding a second external API fallback
2. Reduce dependency on single external API (USDA)
3. Demonstrate multi-source nutrition data integration architecture

### Secondary Goals
1. Provide better coverage for Canadian food products
2. Add response caching to reduce API call volume
3. Maintain consistent response times across all fallback tiers

---

## Success Criteria

- [ ] CNF API client successfully searches for food items
- [ ] CNF API returns nutrition data in normalized format matching nutrition_db.json schema
- [ ] 3-tier fallback works: local → CNF → USDA
- [ ] CNF API responses are cached to reduce redundant calls
- [ ] Feature can be enabled/disabled via environment variable flag
- [ ] Unit tests cover CNF client with >80% code coverage
- [ ] Documentation includes CNF API credential setup instructions
- [ ] Average response time remains < 1 second for cached results
- [ ] Integration works in deployed Cloud Function environment

---

## Requirements

### Functional Requirements

**FR1:** Create CNF API client module (`cnf_client.py`) with search and nutrition retrieval methods

**FR2:** CNF client must normalize Canadian nutrient data to match existing schema:
```python
{
    "calories": float,
    "protein_g": float,
    "carbs_g": float,
    "fat_g": float,
    "fiber_g": float,
    "sodium_mg": float,
    "vitamin_c_mg": float,
    "calcium_mg": float,
    "iron_mg": float,
    "category": str  # inferred from nutritional profile
}
```

**FR3:** Implement 3-tier fallback logic in `nutrition_calculator.py`:
1. Check local `nutrition_db.json`
2. If not found and CNF enabled → query CNF API
3. If CNF not found/disabled → query USDA API
4. If all fail → return error with unknown_foods list

**FR4:** Add in-memory caching for CNF API responses to reduce redundant calls

**FR5:** CNF feature must be controllable via environment variable `ENABLE_CNF_API` (true/false)

**FR6:** CNF client must handle API errors gracefully and log failures without breaking the fallback chain

**FR7:** Infer food category from nutritional profile (same logic as USDA client)

### Technical Requirements

**TR1:** CNF API client must use the Health Canada API endpoint: `https://food-nutrition.canada.ca/api/canadian-nutrient-file`

**TR2:** CNF API requires API key authentication (header: `X-API-Key`)

**TR3:** API key must be configurable via environment variable `CNF_API_KEY`

**TR4:** HTTP request timeout must be 5 seconds (same as USDA)

**TR5:** Use `requests` library for HTTP calls (consistent with USDA client)

**TR6:** Cache must be in-memory dictionary (no external cache dependencies)

**TR7:** All modules must work in Cloud Functions Python 3.12 runtime

**TR8:** Must include requirements.txt entry if new dependencies added (none expected)

### Non-Functional Requirements

**NFR1:** CNF API calls must not slow down overall response time beyond 1 second for first call, <100ms for cached

**NFR2:** Code must follow existing project style (black, isort, flake8)

**NFR3:** Error messages must be clear and actionable for debugging

**NFR4:** Cache must not grow unbounded (consider LRU eviction or size limits)

**NFR5:** Documentation must include troubleshooting section for API errors

---

## User Stories

### As a Demo Presenter
- I want the nutrition lookup to work reliably during demos
- So that I can confidently showcase the system to stakeholders
- Even if one external API is experiencing issues

### As a Developer
- I want clear documentation on obtaining CNF API credentials
- So that I can set up my local development environment
- Without trial-and-error or external research

### As a System Administrator
- I want to control which APIs are enabled via environment variables
- So that I can adjust configuration without code changes
- Based on API availability, rate limits, or costs

---

## Technical Specifications

### CNF API Integration

**Endpoint:** `https://food-nutrition.canada.ca/api/canadian-nutrient-file`

**Search Request:**
```http
GET /search?q={food_name}&lang=en
Headers:
  X-API-Key: {api_key}
```

**Response Format:**
```json
{
  "foods": [
    {
      "food_code": "123",
      "food_description": "Chicken, broilers or fryers, breast",
      "nutrients": {
        "energy_kcal": 165,
        "protein_g": 31,
        "carbohydrate_g": 0,
        "total_fat_g": 3.6,
        "fibre_g": 0,
        "sodium_mg": 74,
        "vitamin_c_mg": 0,
        "calcium_mg": 15,
        "iron_mg": 1
      }
    }
  ]
}
```

### Code Structure

**New File:** `cloud-functions/nutrition-analyzer/cnf_client.py`

```python
"""
Canadian Nutrient File (CNF) API client.
Provides food lookup and nutrition data from Health Canada database.
"""

import os
from typing import Dict, Optional
import requests


class CNFClient:
    """Client for Canadian Nutrient File API."""

    BASE_URL = "https://food-nutrition.canada.ca/api/canadian-nutrient-file"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize CNF API client."""
        self.api_key = api_key or os.environ.get("CNF_API_KEY")
        self._cache = {}  # In-memory cache

    def search_food(self, query: str, lang: str = "en") -> list:
        """Search for foods in CNF database."""
        # Implementation details

    def get_nutrition_per_100g(self, food_name: str) -> Optional[Dict]:
        """Get nutrition data normalized to our schema."""
        # Check cache first
        # Call API if not cached
        # Normalize response
        # Cache result
        # Return normalized dict

    def _normalize_nutrient_data(self, cnf_data: Dict) -> Dict:
        """Map CNF nutrient fields to our schema."""
        # Field mapping logic

    def _infer_category(self, nutrition: Dict) -> str:
        """Infer food category (same as USDA)."""
        # Category inference logic


# Singleton instance
_cnf_client = None


def get_cnf_client() -> CNFClient:
    """Get or create CNF API client singleton."""
    global _cnf_client
    if _cnf_client is None:
        _cnf_client = CNFClient()
    return _cnf_client
```

**Modified File:** `cloud-functions/nutrition-analyzer/nutrition_calculator.py`

Add CNF fallback between local and USDA:

```python
# Existing imports
from cnf_client import get_cnf_client

# In calculate_nutrition function
ENABLE_CNF_API = os.environ.get("ENABLE_CNF_API", "false").lower() == "true"
ENABLE_USDA_API = os.environ.get("ENABLE_USDA_API", "false").lower() == "true"

for item in food_items:
    food_name = item["name"].lower()

    # Tier 1: Local database
    if food_name in NUTRITION_DB:
        # existing logic
        continue

    # Tier 2: CNF API (if enabled)
    if ENABLE_CNF_API:
        cnf_client = get_cnf_client()
        cnf_data = cnf_client.get_nutrition_per_100g(food_name)
        if cnf_data:
            # use CNF data
            continue

    # Tier 3: USDA API (if enabled)
    if ENABLE_USDA_API:
        # existing USDA logic
        continue

    # All tiers failed
    unknown_foods.append(item["name"])
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENABLE_CNF_API` | No | `false` | Enable Canadian Nutrient File API fallback |
| `CNF_API_KEY` | Yes (if enabled) | None | API key for Health Canada CNF API |
| `ENABLE_USDA_API` | No | `false` | Enable USDA FoodData Central API fallback |
| `USDA_API_KEY` | Yes (if enabled) | `DEMO_KEY` | API key for USDA API |

### Obtaining CNF API Credentials

1. Visit: https://food-nutrition.canada.ca/api/documentation
2. Click "Request API Access"
3. Fill out application form with:
   - Organization: Personal/Demo Project
   - Use case: Nutrition tracking demo application
   - Expected volume: <100 requests/day
4. Receive API key via email (typically 1-2 business days)
5. Set environment variable: `export CNF_API_KEY="your-key-here"`

**For Cloud Function deployment:**
```bash
gcloud functions deploy nutrition-analyzer \
  --set-env-vars ENABLE_CNF_API=true,CNF_API_KEY=your-key-here
```

---

## Dependencies

### External Dependencies
- **Health Canada CNF API** - Requires API key, free tier available
- **USDA FoodData Central API** - Existing dependency
- No new Python packages required

### Internal Dependencies
- `nutrition_calculator.py` - Modified to add CNF tier
- `usda_client.py` - Reference implementation for structure
- Environment configuration in Cloud Function deployment

---

## Timeline

### Phase 1: Implementation (3-4 hours)
- Create `cnf_client.py` module (1.5 hours)
- Update `nutrition_calculator.py` with 3-tier fallback (1 hour)
- Add environment variable handling (30 min)
- Manual testing with sample foods (1 hour)

### Phase 2: Testing & Documentation (2-3 hours)
- Write unit tests for CNF client (1.5 hours)
- Update deployment documentation (30 min)
- Test in Cloud Function environment (1 hour)

### Phase 3: Validation (1 hour)
- End-to-end testing with Agent Builder
- Performance validation
- Demo scenario testing

**Total Estimated Time:** 6-8 hours

---

## Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| CNF API credential approval delayed | High | Medium | Start with local testing using mock responses; use USDA as primary fallback |
| CNF API has different data structure than documented | Medium | Low | Implement robust error handling; log actual responses for debugging |
| Cache grows too large in Cloud Function | Low | Low | Implement LRU cache with max 1000 entries |
| CNF API has lower coverage than expected | Low | Medium | Document coverage comparison; USDA remains final fallback |
| API response times slow down demos | Medium | Low | Use aggressive caching; set 5-second timeout; fail fast to USDA |

---

## Out of Scope

The following are explicitly **not** included in this feature:

- ❌ Storing CNF results in `nutrition_db.json` (same as USDA - not persisted)
- ❌ Multi-language support (English only for CNF queries)
- ❌ Advanced caching strategies (Redis, memcached, persistent storage)
- ❌ CNF-specific food categories beyond standard inference
- ❌ Webhooks or notifications for API failures
- ❌ Cost tracking or rate limit monitoring
- ❌ A/B testing between CNF and USDA results
- ❌ UI for selecting preferred data source
- ❌ Historical tracking of which API was used per query

---

## Acceptance Criteria

### API Integration
- [ ] CNF client can search for common foods (chicken, apple, rice, milk)
- [ ] CNF client returns normalized nutrition data matching schema
- [ ] CNF client handles API errors without crashing
- [ ] CNF client respects 5-second timeout

### Fallback Logic
- [ ] Local DB checked first
- [ ] CNF checked second (when enabled)
- [ ] USDA checked third (when enabled)
- [ ] Error returned only when all tiers fail
- [ ] Feature flag `ENABLE_CNF_API` works correctly

### Caching
- [ ] Identical queries return cached results
- [ ] Cache survives multiple requests in same Cloud Function instance
- [ ] Cache doesn't cause memory issues

### Testing
- [ ] Unit tests for CNF client (>80% coverage)
- [ ] Integration test for 3-tier fallback
- [ ] Manual testing with 10+ food items
- [ ] Deployed Cloud Function works with CNF enabled

### Documentation
- [ ] README updated with CNF setup instructions
- [ ] Environment variable documentation complete
- [ ] Troubleshooting guide for common API errors
- [ ] Code comments explain CNF-specific logic

---

## Open Questions

1. **Cache eviction policy:** Should we implement LRU eviction or just cap at N entries?
   - **Decision needed:** Simple cap at 1000 entries or LRU implementation?

2. **API key rotation:** How should we handle CNF API key rotation in production?
   - **Decision needed:** Document manual process or implement auto-reload?

3. **Metrics/Logging:** Should we log which tier (local/CNF/USDA) was used for each query?
   - **Decision needed:** Add logging for debugging or keep simple?

4. **Priority override:** Should there be a way to prefer USDA over CNF for specific foods?
   - **Decision needed:** Keep simple priority (CNF first) or add override mechanism?

---

## Related Work

- **Issue #7:** USDA client needs test coverage (44.8% → 90%+)
- **Existing:** USDA API integration (`usda_client.py`)
- **Existing:** 2-tier fallback logic in `nutrition_calculator.py`
- **Reference:** https://produits-sante.canada.ca/api/documentation/cnf-documentation-en.html

---

## Success Metrics

For a demo application with no user base:

1. **Functional Success:**
   - API calls return valid nutrition data 95%+ of the time
   - Response times stay under 1 second (first call) / 100ms (cached)

2. **Demo Success:**
   - System remains operational during stakeholder presentations
   - Can demonstrate fallback behavior (disable CNF, shows USDA working)

3. **Code Quality:**
   - CNF client module has >80% test coverage
   - No SonarCloud code quality issues introduced
   - Follows existing code style (black, isort, flake8)

4. **Documentation Quality:**
   - Junior developer can set up CNF API with docs alone
   - Troubleshooting guide resolves 80%+ of common issues

---

**PRD Approved By:** _Pending_
**Implementation Started:** _Not yet started_
**Implementation Completed:** _Not yet completed_
