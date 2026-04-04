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
**Implementation Status:** Phase 2 COMPLETE + VPS Migration COMPLETE (Sessions 1-15 done)
**Current Branch:** main
**Last Updated:** April 3, 2026

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
- ✅ Session 12: Code Quality Tooling Migration (Ruff, Security Scans, SonarCloud Fixes)
- ✅ Session 13: Image Feature Merge + UI/UX Bug Fixes (7 issues closed)
- ✅ Session 14: Repository Cleanup & Test Fixture Optimization (PR #44)
- ✅ Session 15: VPS Migration - FastAPI + OpenRouter Backend (PR #50)

### Key Deliverables
- ✅ Cloud Function deployed: `nutrition-analyzer` (us-central1)
- ✅ Nutrition database: 47 foods + CNF API (5,690 foods) + USDA API (500,000+ foods)
- ✅ 3-tier fallback system: Local DB → CNF API → USDA API
- ✅ Natural language support for CNF foods via enhanced parser
- ✅ Tiered rule engine with 3 rule types
- ✅ Unit tests: 93 tests, 100% coverage on CNF client (94% overall)
- ✅ Agent Builder configuration complete (replaced by FastAPI + OpenRouter in Session 15)
- ✅ Demo script and test cases documented
- ✅ SonarCloud integration with CI/CD pipeline
- ✅ Demo page deployed to VPS (dietitian.adamkwhite.com)
- ✅ Self-hosted FastAPI backend with OpenRouter (Gemini Flash 2.0)
- ✅ Custom chat widget replacing Dialogflow df-messenger

### Recent Changes (Session 15 - April 3, 2026)
- **VPS Migration (PR #50):** Migrated entire backend from GCP to self-hosted VPS
- **FastAPI Backend:** New `backend/app.py` with `/api/chat` endpoint using OpenRouter (Gemini Flash 2.0)
- **LLM Tool-Calling:** Gemini Flash decides when to call nutrition analyzer via OpenAI-compatible tool-calling API
- **Custom Chat Widget:** Replaced Dialogflow df-messenger with inline HTML/JS chat widget
- **DNS + SSL:** Set up dietitian.adamkwhite.com with nginx + Let's Encrypt on Hostinger VPS
- **Systemd Service:** `dietitian.service` running uvicorn on port 8001, auto-restart
- **sys.path Import Pattern:** Backend imports existing nutrition modules from `cloud-functions/nutrition-analyzer/` without copying
- **SonarCloud Token Issue:** SONAR_TOKEN returning HTTP 403 — needs investigation (pre-existing)
- **Issue #49 Closed:** Migration tracking issue completed

### Recent Changes (Session 14 - November 30, 2025)
- **Repository Cleanup (PR #44):** Cleaned up uncommitted files from previous sessions
- **Gitignore Update:** Added .playwright-mcp/ to .gitignore (local MCP server state)
- **Slash Commands:** Added 9 slash command files to .claude/commands/ directory
- **Settings Update:** Updated .claude/settings.local.json with git pull and gh issue close permissions
- **Test Fixture Optimization:** Optimized kiwi.jpg from 3.5MB to 1.5MB (57% reduction using ImageMagick quality=75)
- **Test Fixtures Added:** 5 test fixture images for image processing feature (total 3.6MB)
- **Pre-commit Config:** Increased large file check from 500KB to 2MB to accommodate test images
- **All CI/CD Checks Passed:** Quick Validation, Tests, SonarCloud, Security all green

### Recent Changes (Session 13 - November 22, 2025)
- **Image Feature Merged:** PR #20 merged image-food-logging feature branch to main
- **Issue #30 Fixed:** Visual indicators (green/red) for recognized vs unrecognized foods (PR #36)
- **Issue #27 Fixed:** Show detected foods in chat when sending to agent (PR #37)
- **Issue #28 Fixed:** Improved UX for non-food detection with dynamic headings (PR #38)
- **Issue #29 Fixed:** Checkboxes to select which foods to send to agent (PR #39)
- **Issue #26 Fixed:** Auto-clear results when selecting new image (PR #40)
- **Issue #32 Fixed:** Main page "Try It Now" section now clickable (PR #41)
- **Issue #25 Fixed:** Analyze button opens file picker when no file selected (PR #42)
- **Demo Pages Deployed:** Both index.html and test-multimodal.html updated in GCS
- **7 Issues Closed:** All UI/UX issues from user testing addressed

### Recent Changes (Session 12 - October 16-17, 2025)
- **Ruff Migration (PR #22):** Replaced flake8 + isort with ruff for 10-100x faster linting
- **SonarCloud Coverage Fix (PR #24):** Excluded feature-flagged usda_client.py from coverage
- **Simplified Pre-commit Hooks (PR #23):** Removed overkill checks from pre-commit
- **Security Workflow:** Created weekly CI/CD security scans (bandit + safety in GitHub Actions)

### Recent Changes (Session 11 - October 15, 2025)
- **Image Processing PRD:** Created comprehensive PRD for image-based food logging
- **GCP Infrastructure:** Vision API setup, service account, Cloud Storage bucket
- **Feature Implementation:** Vision API client, food label mapper, Cloud Function endpoint

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
**Backend Architecture (Session 15+):**
- FastAPI backend on VPS, OpenRouter API (Gemini Flash 2.0) for conversational AI
- OpenAI SDK with `base_url="https://openrouter.ai/api/v1"` (same pattern as job-agent project)
- LLM tool-calling pattern: Gemini Flash decides when to invoke nutrition analyzer
- Existing nutrition modules imported via `sys.path` — no code duplication
- Stateless backend: frontend sends conversation history with each request

**Why Functions Framework (not Flask) in nutrition-analyzer?**
- Original Cloud Function code uses `@functions_framework.http` decorator
- Flask is a transitive dependency, only import `jsonify()` utility
- Functions Framework installed in backend venv to allow importing `main.py` without modification

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
- **Backend (VPS):** `backend/`
  - `app.py` - FastAPI app with OpenRouter integration (165 lines)
  - `requirements.txt` - Backend dependencies
  - `systemd/dietitian.service` - Systemd unit file
- **Agent Config (legacy):** `agent-config/`
  - `agent-instructions-simple.txt` - System prompt source for OpenRouter
  - `agent-instructions.txt` - Original detailed version
  - `webhook-config.json`
  - `test-cases.md`
  - `SETUP_GUIDE_UPDATED.md`
- **Demo:** `docs/demo/demo-script.md`
- **Documentation:** `docs/deployment/`, `docs/demo/`
- **Image Processing (MERGED to main):** `cloud-functions/image-food-analyzer/`
  - `main.py` - Cloud Function for image analysis (595 lines)
  - `vision_client.py` - Vision API client (266 lines)
  - `food_label_mapper.py` - Maps Vision labels to foods (324 lines)
  - `test_*.py` - Unit tests for image processing
- **Demo Pages:** `docs/demo/`
  - `virtual-dietitian-demo.html` - Main landing page (deployed as index.html)
  - `test-multimodal.html` - Image upload + analysis page
- **Infrastructure:** `scripts/setup-image-processing.sh` - GCP Vision API setup automation

## Known Issues
- **Issue #7:** USDA client module has 0% test coverage (deferred - USDA API unavailable)
- **Issue #31:** Commercial packaged items not in database (feature request)
- **Issue #33:** Lack of Calendar (future feature)
- USDA API feature flag requires API key configuration
- **SonarCloud Token:** SONAR_TOKEN returning HTTP 403 in CI — needs token refresh

## Next Steps
**Immediate (Technical Debt):**
- Fix SonarCloud SONAR_TOKEN (HTTP 403 in CI)
- Migrate to non-deprecated SonarCloud action (Issue #6)
- Add comprehensive unit tests for `usda_client.py` when API available
- Add unit tests for `backend/app.py`

**Phase 3 (Planned Features):**
- Multi-turn conversations with context tracking
- Meal history persistence (database integration)
- Calendar integration for meal tracking (Issue #33)
- Commercial packaged food recognition (Issue #31)
- Dietary goal setting and progress monitoring
- Personalized recommendations based on user patterns
- Export nutrition reports (PDF, CSV)

## Dependencies
**External Services:**
- Hostinger VPS (Ubuntu, nginx, systemd)
- OpenRouter API (Gemini Flash 2.0 via OpenAI-compatible endpoint)
- CNF API (Canadian Nutrient File, 5,690 foods)
- USDA FoodData Central API (optional, feature-flagged)
- SonarCloud (code quality analysis)
- Let's Encrypt (SSL certificates)

**Python Libraries (Backend):**
- fastapi>=0.115 (web framework)
- uvicorn>=0.34 (ASGI server)
- openai>=1.60 (OpenRouter API client)
- python-dotenv>=1.0 (environment variables)
- requests>=2.31 (HTTP client for APIs)
- functions-framework>=3.0 (enables importing nutrition-analyzer modules)

**Python Libraries (Testing):**
- pytest==8.*, pytest-cov==6.*

## Live Demo
**Demo URL:** https://dietitian.adamkwhite.com
**Backend API:** https://dietitian.adamkwhite.com/api/chat
**Health Check:** https://dietitian.adamkwhite.com/api/health
**VPS:** Hostinger (srv1412298), systemd service `dietitian`
**Repo on VPS:** `/home/adam/Code/Virtual-Dietitian/` (branch: feature/fastapi-openrouter-backend)
**Legacy GCP (expired):** virtualdietitian project, us-central1
**SonarCloud:** https://sonarcloud.io/summary/new_code?id=adamkwhite_Virtual-Dietitian

## Lessons Learned
**Session 15 Key Learnings:**
1. **sys.path Import for Code Reuse:** Adding existing module directories to `sys.path` avoids duplicating code — but watch for top-level imports in the source module (e.g., `functions_framework`) that must be installed in the new venv
2. **OpenRouter Model IDs:** OpenRouter model names differ from provider names — `google/gemini-2.0-flash-001` not `google/gemini-flash-2.0`. Use env var override for easy fixing without redeployment
3. **Port Conflicts on systemd Restart:** Fast restart loops can leave zombie processes holding the port. Use `fuser -k <port>/tcp` before restarting to clear stale bindings
4. **LLM Tool-Calling over Heuristics:** Using the LLM's native tool-calling to decide "is this a meal?" is more robust than regex — handles ambiguity, multilingual input, and conversational context naturally
5. **Stateless Chat Backend:** Sending conversation history from the frontend eliminates server-side session management — simple, scalable, no state to lose on restart
6. **Let's Encrypt "No such authorization":** Can be transient — retry after a minute often succeeds, even when DNS is already resolving correctly
7. **GCP Free Trial Expiry:** All services stop immediately — no grace period. Self-hosted VPS eliminates this single point of failure for demo/portfolio projects

**Session 14 Key Learnings:**
1. **Pre-commit Large File Checks:** Default 500KB limit blocks legitimate test fixtures - adjust `--maxkb` parameter in `.pre-commit-config.yaml` to accommodate realistic test data
2. **ImageMagick Quality Settings:** quality=75 with 4:2:0 sampling provides excellent balance for test fixtures (3.5MB → 1.5MB = 57% reduction without visible quality loss)
3. **Test Fixture Validation:** Always verify test images work after optimization - compression can break Vision API recognition if too aggressive
4. **Repository Hygiene:** Periodic cleanup of uncommitted files prevents confusion and keeps git status clean
5. **Duplicate File Detection:** Check both `.claude/` and `.claude/commands/` for duplicates when adding slash commands
6. **MCP State Files:** Local MCP server directories (`.playwright-mcp/`, etc.) should be gitignored to avoid committing generated state

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
