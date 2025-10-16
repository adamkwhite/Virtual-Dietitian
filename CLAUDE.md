# CLAUDE.md

## Project Overview
Virtual Dietitian AI Agent - Interview take-home exercise demonstrating rapid prototyping with Google Cloud Agent Builder.

## Purpose
Build a conversational AI agent that analyzes meal descriptions and provides nutritional feedback with actionable health insights.

## Key Context
- **Timeline:** 2-3 hour implementation target
- **Stakeholders:** Demo for CEO and Chief Data Officer
- **Focus:** Technical depth, clean architecture, data flow design
- **Platform:** Google Cloud (Vertex AI Agent Builder, Cloud Functions, Vertex AI Search)
- **Deliverables:** Live demo link, video walkthrough, architecture documentation

## Technical Approach
- **Phase 1 (MVP):** 50-food static JSON database, tiered rule engine, single-turn conversations
- **Phase 2:** USDA API integration for 500+ foods
- **Phase 3:** Multi-turn conversations, meal history, dietary goals

## Architecture Highlights
- **Separation of Concerns:** LLM for NLU/NLG, Cloud Function for deterministic business logic
- **Tiered Rule Engine:** Category detection, threshold warnings, macro ratio recommendations
- **State Management:** Progression from stateless → session → persistent
- **Scalability:** Serverless-first design (1 to 1M users without architectural changes)

## Current Status
**Implementation Status:** Phase 2 COMPLETE + Image Processing Feature (Experimental) (Sessions 1-11 done)
**Current Branch:** main (experimental: feature/image-food-logging)
**Last Updated:** October 15, 2025

### Completed Sessions
- ✅ Session 1: GCP Setup & Environment Configuration
- ✅ Session 2: Nutrition Database Creation (47 foods)
- ✅ Session 3: Cloud Function Webhook Development
- ✅ Session 4: Vertex AI Agent Builder Configuration
- ✅ Session 5: End-to-End Testing & Demo Preparation
- ✅ Session 6: Agent Builder Integration & Live Deployment
- ✅ Session 7: Code Quality & SonarCloud Integration
- ✅ Session 8: Multi-Language Support & Agent Configuration Fixes
- ✅ Session 9: CNF API Integration & Code Quality Refactoring
- ✅ Session 10: Parser Enhancement for CNF Natural Language Queries
- ✅ Session 11: Image-Based Food Logging PRD & Infrastructure Setup

### Key Deliverables
- ✅ Cloud Function deployed: `nutrition-analyzer` (us-central1)
- ✅ Nutrition database: 47 foods + CNF API (5,690 foods) + USDA API (500,000+ foods)
- ✅ 3-tier fallback system: Local DB → CNF API → USDA API
- ✅ Natural language support for CNF foods via enhanced parser
- ✅ Tiered rule engine with 3 rule types
- ✅ Unit tests: 93 tests, 100% coverage on CNF client (94% overall)
- ✅ Agent Builder configuration complete
- ✅ Demo script and test cases documented
- ✅ SonarCloud integration with CI/CD pipeline
- ✅ Demo page deployed to GCS
- ✅ Observability features enabled (Cloud Logging, Conversation History)

### Recent Changes (Session 11 - October 15, 2025)
- **Image Processing PRD:** Created comprehensive PRD for image-based food logging (32-hour estimate)
- **Task Breakdown:** Generated 72 sub-tasks across 8 parent tasks (detailed implementation plan)
- **GCP Infrastructure:** Completed full Vision API setup (Task 1.0 - 9/9 sub-tasks)
- **Vision API Enabled:** Activated Cloud Vision API in virtualdietitian project
- **Service Account:** Created vision-api-sa with Vision + Storage permissions
- **Cloud Storage:** Created gs://virtualdietitian-food-images bucket (us-central1)
- **Lifecycle Policy:** Configured 90-day auto-deletion for uploaded images
- **Security:** Enforced public access prevention (private bucket)
- **CORS Configuration:** Enabled for demo webpage uploads (wildcard for development)
- **Automation Script:** Created scripts/setup-image-processing.sh (5KB, executable)
- **Feature Branch:** Created feature/image-food-logging experimental branch
- **Progress:** 1/8 parent tasks complete (12.5%), 9/72 sub-tasks complete

### Recent Changes (Session 10 - October 15, 2025)
- **Parser Enhancement:** Natural language support for CNF API foods (5,690 foods)
- **Stopword Filtering:** Added 50+ stopwords in English, French, Spanish
- **Passthrough Logic:** Unknown foods now pass to 3-tier fallback (Local → CNF → USDA)
- **Test Updates:** Added 4 new tests, updated 2 existing tests (93 tests total)
- **SonarCloud Fixes:** Resolved 7 code smells (duplicate keys, type hints, string concatenation)
- **USDA Coverage Exclusion:** Excluded usda_client.py from coverage (feature flag off)
- **Claude Settings Cleanup:** Fixed invalid settings.local.json (31 entries → 20 patterns)
- **Slash Commands Fixed:** Added frontmatter to enable autocomplete discovery
- **PRs Merged:** #17 (SonarCloud fixes), #18 (USDA exclusion), #19 (Parser enhancement - pending)

### Recent Changes (Session 9 - October 15, 2025)
- **CNF API Integration:** Added Canadian Nutrient File API client (5,690 foods)
- **3-Tier Fallback:** Implemented Local DB → CNF API → USDA API architecture
- **In-Memory Caching:** Food list and nutrition data cached for performance
- **Fuzzy Search:** Exact → contains → reverse contains matching algorithm
- **Code Refactoring:** Extracted `nutrition_utils.py` to eliminate 21.9% code duplication
- **100% Test Coverage:** 33 unit tests for CNF client, all passing
- **Observability Setup:** Enabled Cloud Logging, Conversation History, User Feedback
- **Production Deployment:** Deployed refactored code (revision 00006-xud)
- **PR #16 Merged:** All SonarCloud quality gates passed

### Recent Changes (Session 8 - October 15, 2025)
- **Multi-Language Support:** Added French/Spanish food name translation (32 translations)
- **Agent Configuration Fix:** Removed all examples from Agent Builder (were causing silent responses)
- **Simplified Instructions:** Created minimal agent instructions that work reliably
- **CNF API Planning:** Created comprehensive PRD and tasks for Canadian Nutrient File integration (72 sub-tasks, deferred)
- **Demo Page Updates:** Attempted clickable examples (browser caching issues), deployed clean version
- **Cache Management:** Learned GCS cache-busting techniques (setmeta headers, URL versioning)

## Technology Stack
- **Backend:** Python 3.12, Google Cloud Functions Framework (not Flask - see notes below)
- **Testing:** pytest, pytest-cov
- **Code Quality:** SonarCloud, black, isort, flake8, pre-commit hooks
- **CI/CD:** GitHub Actions (linting → testing → code analysis)
- **Cloud Platform:** Google Cloud Platform
  - Cloud Functions Gen2 (serverless compute)
  - Vertex AI Agent Builder (conversational AI)
  - Cloud Storage (static website hosting)
- **APIs:** CNF API (5,690 foods), USDA FoodData Central API (500,000+ foods)
- **Data:** Static JSON (47 foods) + 3-tier API fallback (CNF → USDA)
- **Deployment:** gcloud CLI, bash scripts

### Technology Notes
**Why Functions Framework (not Flask)?**
- We use `@functions_framework.http` decorator (Google's official framework)
- Flask is a transitive dependency, only import `jsonify()` utility
- Functions Framework handles GCP Cloud Functions integration automatically
- Simpler deployment, no WSGI/routing configuration needed
- Perfect fit for serverless webhook endpoints

## Key Files
- **Status:** `docs/PROJECT_STATUS.md` (current project state)
- **PRD:** `docs/features/virtual-dietitian-mvp-PLANNED/prd.md`
- **Nutrition Data:**
  - `data/nutrition_db.json` (master copy)
  - `cloud-functions/nutrition-analyzer/nutrition_db.json` (deployed copy)
- **Webhook:** `cloud-functions/nutrition-analyzer/`
  - `main.py` - Entry point (241 lines, includes multi-language support)
  - `nutrition_calculator.py` - Aggregation with 3-tier fallback (288 lines)
  - `rule_engine.py` - Rules engine (349 lines)
  - `cnf_client.py` - CNF API client (218 lines)
  - `usda_client.py` - USDA API client (176 lines)
  - `nutrition_utils.py` - Shared utilities (64 lines)
  - `test_*.py` - Unit tests (89 tests total)
- **Agent Config:** `agent-config/`
  - `agent-instructions-simple.txt` - Working minimal instructions
  - `agent-instructions.txt` - Original detailed version
  - `webhook-config.json`
  - `test-cases.md`
  - `SETUP_GUIDE_UPDATED.md`
- **Demo:** `docs/demo/demo-script.md`
- **Documentation:** `docs/deployment/`, `docs/demo/`
- **Image Processing (Experimental):** `docs/features/image-food-logging-PLANNED/`
  - `prd.md` - Comprehensive PRD (32-hour estimate, detailed specs)
  - `tasks.md` - Task breakdown (72 sub-tasks across 8 parent tasks)
  - `status.md` - Progress tracker (1/8 tasks complete, 9/72 sub-tasks complete)
- **Infrastructure:** `scripts/setup-image-processing.sh` - GCP Vision API setup automation

## Known Issues
- **Issue #6:** SonarCloud GitHub Action is deprecated (needs migration to sonarqube-scan-action)
- **Issue #7:** USDA client module has 0% test coverage (only affects overall coverage metric)
- USDA API feature flag requires API key configuration
- User feedback buttons not appearing on demo page (deferred troubleshooting)

## Next Steps
**Immediate (Experimental Feature):**
- Continue image-food-logging feature (Branch: feature/image-food-logging)
  - Build Vision API client for food detection (Task 2.0 - 11 sub-tasks)
  - Create food label mapping and serving size logic (Task 3.0 - 11 sub-tasks)
  - Implement Cloud Function endpoint for image analysis (Task 4.0 - 16 sub-tasks)
  - Add image upload UI to demo webpage (Task 5.0 - 17 sub-tasks)
  - Testing, monitoring, and deployment (Tasks 6.0-8.0 - 29 sub-tasks)
  - Progress: 1/8 parent tasks (12.5%), 9/72 sub-tasks (12.5%)

**Immediate (Technical Debt):**
- Add comprehensive unit tests for `usda_client.py` to reach ~90%+ coverage
- Migrate to non-deprecated SonarCloud action

**Phase 3 (Planned Features):**
- Multi-turn conversations with context tracking
- Meal history persistence (database integration)
- Dietary goal setting and progress monitoring
- Personalized recommendations based on user patterns
- Export nutrition reports (PDF, CSV)

## Dependencies
**External Services:**
- GCP Cloud Functions (Python 3.12 runtime)
- Vertex AI Agent Builder
- Google Cloud Vision API (experimental, image food detection)
- Google Cloud Storage (experimental, image storage)
- USDA FoodData Central API (optional, feature-flagged)
- SonarCloud (code quality analysis)

**Python Libraries:**
- functions-framework==3.* (Cloud Functions integration)
- requests==2.* (HTTP client for USDA API)
- python-dotenv==1.* (environment variables)
- pytest==8.*, pytest-cov==6.* (testing)
- google-cloud-vision==3.* (experimental, Vision API client)
- google-cloud-storage==2.* (experimental, image storage)
- Pillow==10.* (experimental, image preprocessing)

## Live Demo
**Demo URL:** https://storage.googleapis.com/virtual-dietitian-demo/index.html
**Cloud Function:** https://nutrition-analyzer-epp4v6loga-uc.a.run.app
**GCP Project:** virtualdietitian
**Region:** us-central1
**SonarCloud:** https://sonarcloud.io/summary/new_code?id=adamkwhite_Virtual-Dietitian

## Lessons Learned
**Session 11 Key Learnings:**
1. **PRD Structure Decision:** Use Option 2 (Comprehensive Engineering PRD) for complex technical features with infrastructure changes - provides detailed specs, code examples, and risk mitigation
2. **ML Service Cost Comparison:** Always research pricing before committing - Google Vision API free tier (1,000 images/month, $1.50/1k after) vs LogMeal ($100-500/month) vs Clarifai ($30-300/month plans)
3. **GCP Infrastructure Automation:** Create reusable bash scripts for setup tasks - enables quick recreation on new projects or disaster recovery (scripts/setup-image-processing.sh saved 30+ minutes of manual setup)
4. **Service Account Security:** Store keys in ~/.gcp/ directory with restrictive permissions (600) - keeps credentials out of project repos and version control
5. **Cloud Storage Lifecycle Policies:** Configure auto-deletion policies upfront (90-day lifecycle) - prevents unexpected storage costs and manual cleanup
6. **CORS Wildcard for Development:** Use `"origin": ["*"]` during development, restrict to specific domains in production - balances flexibility with security
7. **Task Breakdown Value:** Breaking 32-hour project into 72 sub-tasks provides clear stopping points and progress tracking - enables pause/resume without losing context
8. **Experimental Branch Strategy:** Use feature branches for experimental work (feature/image-food-logging) - keeps main branch stable while exploring new capabilities
9. **Infrastructure Validation:** Always test infrastructure with real operations (upload/read/delete) before proceeding - catches permission or configuration issues early
10. **Documentation-First Approach:** Creating PRD + tasks before coding clarifies scope, identifies dependencies, and prevents scope creep - 2 hours planning saves 10 hours rework

**Session 10 Key Learnings:**
1. **Claude Code Settings Validation:** Invalid permission patterns cause "Found 1 invalid file settings" warnings - use wildcards (`"Bash(git commit:*)"`) instead of specific command strings with heredocs
2. **SonarCloud Type Hints:** Methods that return `None` sometimes need `Optional[Dict]` return type hints, not just `Dict` (Python type checker strictness)
3. **Coverage Exclusion Strategy:** Use `pyproject.toml` `[tool.coverage.run]` omit config to exclude feature-flagged modules from coverage reports
4. **Parser Passthrough Logic:** Unknown foods can pass to API fallback if they're "food-like" (not stopwords, >=3 chars, not numeric) - enables CNF natural language queries
5. **Multi-language Stopwords:** Need language-specific stopword lists (English, French, Spanish) to filter non-food words before API fallback
6. **Test Consolidation Best Practice:** Always add new tests to existing test files, don't create temporary test files that need to be merged later
7. **Separate PR per Concern:** Even closely related changes need separate PRs for clean change tracking (CLAUDE.md workflow enforcement prevents commit history pollution)
8. **Test Updates for New Behavior:** When adding features that change expected behavior, update existing tests to match new behavior (e.g., `test_unknown_food` → `test_unknown_food_passes_through`)

**Session 9 Key Learnings:**
1. **Always Deploy After Merging:** PR merged code isn't live until deployed via gcloud CLI
2. **SonarCloud Duplication Detection:** 21.9% duplication threshold triggers quality gate failures
3. **DRY Principle in Practice:** Extract shared functions to utility modules (50 lines → 1 import)
4. **Test Coverage Doesn't Auto-Update:** CNF client 100% coverage, but must run pytest to measure
5. **In-Memory Caching Strategy:** Download 5,690 foods once on cold start (tradeoff: startup time vs API calls)
6. **Fuzzy Search Algorithms:** Layered matching (exact → contains → reverse) catches more user queries
7. **API Validation Before Implementation:** Always test API endpoints before designing architecture
8. **Observability Is Essential:** Enabled Cloud Logging/Conversation History before real users test

**Session 8 Key Learnings:**
1. **Agent Builder Examples Are Training Data:** Examples in Agent Builder teach behavior patterns - 11 examples showing "meal → tool call → response" inadvertently taught agent "tool call = end conversation"
2. **Less Is More for Instructions:** Minimal agent instructions (3 lines) work better than complex detailed versions
3. **GCS Browser Caching Is Aggressive:** Regular refreshes don't clear cache; requires hard refresh (`Ctrl+F5`), incognito mode, or `Cache-Control` headers
4. **Cache-Control Headers:** Use `gsutil setmeta -h "Cache-Control:no-cache"` for development, versioned URLs (`?v=N`) for production
5. **Multi-Language NLU Pattern:** Agent Builder handles language detection automatically; webhook only needs translation dictionary for database lookups
6. **Feature Planning Value:** Creating comprehensive PRDs upfront (72 tasks for CNF API) enables quick "go/no-go" decisions

**Session 7 Key Learnings:**
1. **Workflow Discipline:** Always use feature branches, even for documentation changes
2. **Quality Gates:** SonarCloud "Previous version" needs 2+ analyses to establish baseline
3. **Documentation Accuracy:** Regular deep reviews prevent documentation drift
4. **Technology Clarity:** Be precise about frameworks (Functions Framework vs Flask)
5. **Test Coverage Reality:** Distinguish between "core module coverage" and "overall coverage"
6. **Pre-commit Hooks:** Never bypass with environment variables (PRE_COMMIT_ALLOW_NO_CONFIG=1)

## Maintainer
adamkwhite
