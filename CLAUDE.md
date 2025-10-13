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
**Implementation Status:** MVP COMPLETE (Sessions 1-5 done)
**Current Branch:** main
**Last Updated:** October 13, 2025

### Completed Sessions
- ✅ Session 1: GCP Setup & Environment Configuration
- ✅ Session 2: Nutrition Database Creation (47 foods)
- ✅ Session 3: Cloud Function Webhook Development
- ✅ Session 4: Vertex AI Agent Builder Configuration
- ✅ Session 5: End-to-End Testing & Demo Preparation

### Key Deliverables
- ✅ Cloud Function deployed: `nutrition-analyzer` (us-central1)
- ✅ Nutrition database: 47 foods across 6 categories
- ✅ Tiered rule engine with 3 rule types
- ✅ Unit tests: 100% coverage, all passing
- ✅ Agent Builder configuration complete
- ✅ Demo script and test cases documented

## Technology Stack
- **Backend:** Python 3.12, Flask (Cloud Functions Gen2)
- **Testing:** pytest, pytest-cov (100% coverage)
- **Cloud Platform:** Google Cloud Platform
  - Cloud Functions Gen2 (HTTP trigger)
  - Vertex AI Agent Builder
  - Vertex AI Search
- **Data:** Static JSON (47 foods, USDA-based values)
- **Deployment:** gcloud CLI, bash scripts

## Key Files
- **PRD:** `docs/features/virtual-dietitian-mvp-PLANNED/prd.md`
- **Todo List:** `docs/todo.md`
- **Nutrition Data:** `data/nutrition_db.json`
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

## Maintainer
adamkwhite
