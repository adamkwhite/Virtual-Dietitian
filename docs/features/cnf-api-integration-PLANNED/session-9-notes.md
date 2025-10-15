# CNF API Integration - Session 9 Notes

**Date:** October 15, 2025
**Status:** PAUSED - Design complete, ready for implementation
**Branch:** main (clean, PR #14 merged)

---

## Session Summary

Began CNF API integration work. Validated API, corrected PRD assumptions, designed implementation approach. **PAUSED before implementation to address higher priority work.**

---

## Key Discoveries

### 1. CNF API Validation ✅

**Base URL:** `https://food-nutrition.canada.ca/api/canadian-nutrient-file/`

**Authentication:** NONE REQUIRED (PRD incorrectly assumed API key needed)

**Available Data:**
- 5,690 foods in CNF database
- 152 nutrients per food
- Bilingual (English/French)
- JSON/XML response formats

**API Structure (differs from PRD):**

```bash
# Get all foods (no search endpoint exists)
GET /food/?lang=en&type=json
→ [{"food_code": 571, "food_description": "Chicken, broiler, giblets, raw"}, ...]

# Get nutrition for specific food by code
GET /nutrientamount/?id=109&lang=en&type=json
→ [{"nutrient_web_name": "Energy (kcal)", "nutrient_value": 357.0}, ...]
```

**PRD Correction:** PRD assumed `/search?q=chicken` endpoint exists. Reality: must download all foods and search locally.

### 2. Implementation Approach Decision

**User confirmed: "Live design" (in-memory caching) approach**

**Rejected approach:** Pre-download 5,690 foods to `data/cnf_foods.json` in git repo

**Accepted approach:**
- Download on Cloud Function cold start
- Store in global `_cnf_foods_list` variable
- Cache persists across warm requests
- Fresh data on each cold start

**Rationale:**
- Keeps repo clean (~200KB smaller)
- Always fresh data (CNF may add foods)
- Still fast (in-memory search)
- Cold start penalty acceptable for demo use case

---

## Architecture Design

### Global State Variables

```python
# In cnf_client.py
_cnf_foods_list = None      # List of 5,690 {food_code, food_description}
_cnf_nutrition_cache = {}   # Dict of food_code → normalized nutrition data
```

### 3-Tier Fallback Logic

```python
# In nutrition_calculator.py
for item in food_items:
    food_name = item["name"].lower()

    # Tier 1: Local database (47 foods)
    if food_name in NUTRITION_DB:
        # existing logic
        continue

    # Tier 2: CNF API (5,690 foods) ← NEW
    if ENABLE_CNF_API:
        cnf_client = get_cnf_client()
        cnf_data = cnf_client.get_nutrition_per_100g(food_name)
        if cnf_data:
            # use CNF data
            continue

    # Tier 3: USDA API (500,000+ foods)
    if ENABLE_USDA_API:
        # existing USDA logic
        continue

    # All tiers failed
    unknown_foods.append(item["name"])
```

### CNF Client Class Structure

```python
class CNFClient:
    """Client for Canadian Nutrient File API."""

    BASE_URL = "https://food-nutrition.canada.ca/api/canadian-nutrient-file/"

    def __init__(self):
        self._foods_list = None
        self._nutrition_cache = {}

    def get_cnf_foods_list(self) -> List[Dict]:
        """Download all 5,690 foods (once on cold start)."""
        if self._foods_list is None:
            # Download from /food/?lang=en
        return self._foods_list

    def search_food(self, query: str) -> Optional[int]:
        """Fuzzy search for food, return food_code."""
        # 1. Exact match
        # 2. Contains match
        # 3. Return None if no match

    def get_nutrition_per_100g(self, food_name: str) -> Optional[Dict]:
        """Main entry point: search + fetch + normalize."""
        food_code = self.search_food(food_name)
        if food_code:
            return self._fetch_nutrition_data(food_code)
        return None

    def _fetch_nutrition_data(self, food_code: int) -> Dict:
        """Fetch from API, cache, and normalize."""
        # Check cache
        # If not cached: API call → normalize → cache
        # Return normalized data

    def _normalize_nutrient_data(self, cnf_data: List[Dict]) -> Dict:
        """Map CNF nutrient names to our schema."""
        # CNF: "Energy (kcal)" → Our: "calories"
        # CNF: "Protein" → Our: "protein_g"
        # etc.

    def _infer_category(self, nutrition: Dict) -> str:
        """Infer food category from nutrition profile."""
        # Copy logic from usda_client.py
```

### Nutrient Mapping

```python
CNF_NUTRIENT_MAP = {
    "Energy (kcal)": "calories",
    "Protein": "protein_g",
    "Carbohydrate": "carbs_g",
    "Total Fat": "fat_g",
    "Fibre, total dietary": "fiber_g",
    "Sodium, Na": "sodium_mg",
    "Vitamin C": "vitamin_c_mg",
    "Calcium, Ca": "calcium_mg",
    "Iron, Fe": "iron_mg"
}
```

---

## Performance Characteristics

| Scenario | Latency | Notes |
|----------|---------|-------|
| Cold start (first request) | +2-3 seconds | Download 5,690 foods once |
| Warm request (cached nutrition) | <10ms | In-memory dictionary lookup |
| Warm request (not cached) | ~500ms | API call + cache store |
| Memory footprint | ~500KB | Food list in memory |
| Per-food cache entry | ~10KB | Normalized nutrition data |

---

## Next Steps (When Resuming)

### Phase 1: Implementation (~2-3 hours)

1. **Create CNF Client Module**
   - [ ] Create `cloud-functions/nutrition-analyzer/cnf_client.py`
   - [ ] Implement `CNFClient` class with all methods
   - [ ] Add error handling and logging
   - [ ] Test locally with sample queries

2. **Update Nutrition Calculator**
   - [ ] Import `get_cnf_client` in `nutrition_calculator.py`
   - [ ] Add `ENABLE_CNF_API` environment variable check
   - [ ] Insert CNF tier between local and USDA
   - [ ] Test 3-tier fallback logic

3. **Environment Configuration**
   - [ ] Update `.env.example` with `ENABLE_CNF_API=false`
   - [ ] Update deployment scripts if needed
   - [ ] Document CNF configuration in README

### Phase 2: Testing (~1.5 hours)

4. **Unit Tests**
   - [ ] Create `test_cnf_client.py`
   - [ ] Test: `get_cnf_foods_list()` downloads and caches
   - [ ] Test: `search_food()` exact and fuzzy matching
   - [ ] Test: `get_nutrition_per_100g()` success path
   - [ ] Test: `_normalize_nutrient_data()` field mapping
   - [ ] Test: `_infer_category()` logic
   - [ ] Test: API error handling
   - [ ] Test: Caching behavior
   - [ ] Target: >80% coverage

5. **Integration Testing**
   - [ ] Test locally: chicken, rice, broccoli lookups
   - [ ] Test fallback: local → CNF → USDA
   - [ ] Test unknown food handling
   - [ ] Run full test suite: `pytest`

### Phase 3: Deployment (~1 hour)

6. **Deploy to Cloud Function**
   - [ ] Deploy with `ENABLE_CNF_API=true`
   - [ ] Test deployed function with curl
   - [ ] Test with Agent Builder
   - [ ] Monitor Cloud Function logs
   - [ ] Verify cold start time acceptable

7. **Documentation Updates**
   - [ ] Update README.md with CNF section
   - [ ] Update CLAUDE.md with CNF API details
   - [ ] Document 3-tier fallback architecture
   - [ ] Update deployment guides

---

## Files to Reference

- **PRD:** `docs/features/cnf-api-integration-PLANNED/prd.md` (NOTE: API assumptions incorrect)
- **Tasks:** `docs/features/cnf-api-integration-PLANNED/tasks.md` (72 sub-tasks, may need revision)
- **Status:** `docs/features/cnf-api-integration-PLANNED/status.md`
- **Reference Implementation:** `cloud-functions/nutrition-analyzer/usda_client.py`
- **Current Todo:** `docs/todo.md` (shows CNF as high priority)

---

## Important Context

### Why CNF Integration Is High Priority

1. **USDA API is down** - Our current fallback (Tier 3) is unavailable
2. **Only 47 foods in local DB** - Very limited coverage
3. **CNF provides 5,690 foods** - 120x increase in coverage
4. **No authentication** - Simpler than originally planned (no API key needed)
5. **Canadian + international coverage** - Good food variety

### Known Blockers/Risks

- None currently! API is accessible, no auth needed, design is solid

### Current Branch State

- **Branch:** `main` (clean, up to date)
- **Uncommitted changes:** `.claude/settings.local.json` (tool permissions)
- **Untracked files:** `docs/features/cnf-api-integration-PLANNED/` (this directory)
- **Ready to start:** Can create feature branch immediately

---

## Resuming This Work

**Quick start command:**
```bash
# Pull latest
git checkout main && git pull origin main

# Create feature branch
git checkout -b feature/cnf-api-integration

# Read this file for context
cat docs/features/cnf-api-integration-PLANNED/session-9-notes.md

# Start with creating cnf_client.py
# Reference: cloud-functions/nutrition-analyzer/usda_client.py
```

**Estimated time to complete:** 4-6 hours (implementation + tests + deployment)

---

**Session paused to address higher priority work. All design complete, ready for implementation.**
