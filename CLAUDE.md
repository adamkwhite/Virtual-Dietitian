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
**Implementation Status:** Phase 2 COMPLETE (Sessions 1-8 done)
**Current Branch:** feature/multi-language-support
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

### Key Deliverables
- ✅ Cloud Function deployed: `nutrition-analyzer` (us-central1)
- ✅ Nutrition database: 47 foods + USDA API (500,000+ foods)
- ✅ Tiered rule engine with 3 rule types
- ✅ Unit tests: 32 tests, 100% coverage on core modules (44.8% overall)
- ✅ Agent Builder configuration complete
- ✅ Demo script and test cases documented
- ✅ SonarCloud integration with CI/CD pipeline
- ✅ Demo page deployed to GCS

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
- **APIs:** USDA FoodData Central API (500,000+ foods)
- **Data:** Static JSON (47 foods) + USDA API fallback
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
  - `main.py` - Entry point (238 lines, includes multi-language support)
  - `nutrition_calculator.py` - Aggregation (237 lines)
  - `rule_engine.py` - Rules engine (349 lines)
  - `test_*.py` - Unit tests
- **Agent Config:** `agent-config/`
  - `agent-instructions-simple.txt` - Working minimal instructions
  - `agent-instructions.txt` - Original detailed version
  - `webhook-config.json`
  - `test-cases.md`
  - `SETUP_GUIDE_UPDATED.md`
- **Demo:** `docs/demo/demo-script.md`
- **Documentation:** `docs/deployment/`, `docs/demo/`

## Known Issues
- **Issue #6:** SonarCloud GitHub Action is deprecated (needs migration to sonarqube-scan-action)
- **Issue #7:** USDA client module has 0% test coverage (brings overall coverage to 44.8%)
- USDA API feature flag is enabled but requires API key configuration
- Manual test scripts (`manual_test_*.py`) require API keys and environment setup

## Next Steps
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
- USDA FoodData Central API (optional, feature-flagged)
- SonarCloud (code quality analysis)

**Python Libraries:**
- functions-framework==3.* (Cloud Functions integration)
- requests==2.* (HTTP client for USDA API)
- python-dotenv==1.* (environment variables)
- pytest==8.*, pytest-cov==6.* (testing)

## Live Demo
**Demo URL:** https://storage.googleapis.com/virtual-dietitian-demo/index.html
**Cloud Function:** https://nutrition-analyzer-epp4v6loga-uc.a.run.app
**GCP Project:** virtualdietitian
**Region:** us-central1
**SonarCloud:** https://sonarcloud.io/summary/new_code?id=adamkwhite_Virtual-Dietitian

## Lessons Learned
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
