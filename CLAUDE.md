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
**Implementation Status:** Phase 2 COMPLETE (Sessions 1-7 done)
**Current Branch:** main
**Last Updated:** October 14, 2025

### Completed Sessions
- ✅ Session 1: GCP Setup & Environment Configuration
- ✅ Session 2: Nutrition Database Creation (47 foods)
- ✅ Session 3: Cloud Function Webhook Development
- ✅ Session 4: Vertex AI Agent Builder Configuration
- ✅ Session 5: End-to-End Testing & Demo Preparation
- ✅ Session 6: Agent Builder Integration & Live Deployment
- ✅ Session 7: Code Quality & SonarCloud Integration

### Key Deliverables
- ✅ Cloud Function deployed: `nutrition-analyzer` (us-central1)
- ✅ Nutrition database: 47 foods + USDA API (500,000+ foods)
- ✅ Tiered rule engine with 3 rule types
- ✅ Unit tests: 32 tests, 100% coverage on core modules (44.8% overall)
- ✅ Agent Builder configuration complete
- ✅ Demo script and test cases documented
- ✅ SonarCloud integration with CI/CD pipeline
- ✅ Demo page deployed to GCS

### Recent Changes (Session 7 - October 14, 2025)
- Added SonarCloud integration for code quality analysis
- Set up GitHub Actions two-stage CI/CD pipeline
- Fixed all code formatting violations (black, isort, flake8)
- Added comprehensive code quality badges to README
- Fixed documentation discrepancies (test coverage, tech stack, API docs)
- Created PROJECT_STATUS.md for accurate project tracking
- Identified technical debt: USDA client needs test coverage (Issue #7)

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
  - `main.py` - Entry point (202 lines)
  - `nutrition_calculator.py` - Aggregation (237 lines)
  - `rule_engine.py` - Rules engine (349 lines)
  - `test_*.py` - Unit tests
- **Agent Config:** `agent-config/`
  - `agent-instructions.txt`
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
**Session 7 Key Learnings:**
1. **Workflow Discipline:** Always use feature branches, even for documentation changes
2. **Quality Gates:** SonarCloud "Previous version" needs 2+ analyses to establish baseline
3. **Documentation Accuracy:** Regular deep reviews prevent documentation drift
4. **Technology Clarity:** Be precise about frameworks (Functions Framework vs Flask)
5. **Test Coverage Reality:** Distinguish between "core module coverage" and "overall coverage"
6. **Pre-commit Hooks:** Never bypass with environment variables (PRE_COMMIT_ALLOW_NO_CONFIG=1)

## Maintainer
adamkwhite
