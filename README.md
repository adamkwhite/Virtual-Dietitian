# Virtual Dietitian

AI-powered nutrition analysis agent built with Google Cloud Agent Builder. Analyzes meal descriptions and provides personalized nutritional feedback with actionable health insights.

**Live Demo:** https://storage.googleapis.com/virtual-dietitian-demo/index.html

## Overview

Virtual Dietitian is a conversational AI agent that:
- Analyzes natural language meal descriptions
- Calculates total nutritional values (calories, protein, carbs, fat, fiber, vitamins, minerals)
- Provides evidence-based health recommendations
- Detects nutritional imbalances and suggests improvements
- Supports 500,000+ foods via USDA FoodData Central API integration

Built as a demonstration of rapid prototyping with serverless architecture and AI agents.

## Architecture

### Components

**Cloud Function Webhook** (`cloud-functions/nutrition-analyzer/`)
- Python 3.12 serverless function
- Parses meal descriptions and calculates nutrition
- Implements tiered rule engine for health insights
- 100% test coverage with pytest

**Vertex AI Agent Builder**
- Natural language understanding (NLU)
- Conversational flow management
- Natural language generation (NLG)
- Integrates with webhook for deterministic business logic

**Data Sources**
1. **Static Database** (47 foods) - Fast lookup for common foods
2. **USDA API** (500,000+ foods) - Fallback for comprehensive coverage

### Design Philosophy

**Separation of Concerns:**
- LLM handles conversation and language understanding
- Cloud Function handles deterministic nutrition calculations
- Rule engine provides consistent health recommendations

**Scalability:**
- Serverless-first architecture (Cloud Functions Gen2)
- Scales from 1 to 1M users without code changes
- Stateless design for MVP (session state planned for Phase 2)

## Quick Start

### Prerequisites
- Python 3.12+
- Google Cloud SDK (`gcloud`)
- Active GCP project

### Local Development

1. **Setup environment:**
   ```bash
   cd cloud-functions/nutrition-analyzer
   python3 -m venv virtual-dietitian-venv
   source virtual-dietitian-venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your USDA API key (optional)
   ```

3. **Run tests:**
   ```bash
   pytest --cov=. --cov-report=html
   ```

4. **Test locally:**
   ```bash
   python3 test_usda_local.py
   ```

### Deployment

**Deploy Cloud Function:**
```bash
# Without USDA API (static DB only)
gcloud functions deploy nutrition-analyzer \
  --gen2 \
  --runtime=python312 \
  --region=us-central1 \
  --source=. \
  --entry-point=analyze_nutrition \
  --trigger-http \
  --allow-unauthenticated

# With USDA API integration
./scripts/deploy_function_with_usda.sh YOUR_USDA_API_KEY
```

**Deploy Demo Page:**
```bash
# Create GCS bucket (one-time)
gsutil mb -l us-central1 gs://virtual-dietitian-demo

# Upload demo page
gsutil cp docs/demo/virtual-dietitian-demo.html gs://virtual-dietitian-demo/index.html

# Make public
gsutil iam ch allUsers:objectViewer gs://virtual-dietitian-demo
```

## Project Structure

```
Virtual-Dietitian/
├── cloud-functions/
│   └── nutrition-analyzer/          # Cloud Function webhook
│       ├── main.py                   # Entry point (HTTP handler)
│       ├── nutrition_calculator.py   # Nutrition aggregation logic
│       ├── rule_engine.py            # Health insight rules
│       ├── usda_client.py            # USDA API integration
│       ├── nutrition_db.json         # Static food database (47 foods)
│       ├── requirements.txt          # Python dependencies
│       ├── test_*.py                 # Unit tests (100% coverage)
│       └── .env.example              # Environment variable template
│
├── agent-config/                     # Vertex AI Agent Builder config
│   ├── agent-instructions.txt        # Agent prompt and behavior
│   ├── webhook-config.json           # Webhook integration settings
│   └── test-cases.md                 # Manual test scenarios
│
├── docs/
│   ├── demo/
│   │   ├── virtual-dietitian-demo.html  # Live demo page
│   │   └── demo-script.md               # Demo walkthrough
│   ├── deployment/                      # Deployment guides
│   └── features/                        # PRDs and planning docs
│
├── scripts/
│   └── deploy_function_with_usda.sh  # Automated deployment
│
├── CLAUDE.md                         # Project context for Claude AI
└── README.md                         # This file
```

## Features

### Phase 1 (MVP) - ✅ Complete
- [x] 47-food static nutrition database
- [x] Natural language meal parsing
- [x] Nutritional analysis (9 nutrients tracked)
- [x] Tiered rule engine (3 rule types)
- [x] Cloud Function webhook deployment
- [x] Vertex AI Agent Builder integration
- [x] 100% test coverage
- [x] Demo page with Dialogflow Messenger widget

### Phase 2 (Current) - 🚧 In Progress
- [x] USDA FoodData Central API integration (500,000+ foods)
- [x] Feature flag for gradual rollout
- [ ] Enhanced error handling and logging
- [ ] Performance optimization (caching)

### Phase 3 (Planned)
- [ ] Multi-turn conversations with context
- [ ] Meal history tracking
- [ ] Dietary goal setting and monitoring
- [ ] Personalized recommendations
- [ ] Export nutrition reports

## Technology Stack

- **Backend:** Python 3.12, Flask
- **Cloud Platform:** Google Cloud Platform
  - Cloud Functions Gen2 (serverless compute)
  - Vertex AI Agent Builder (conversational AI)
  - Cloud Storage (static hosting)
- **APIs:** USDA FoodData Central API
- **Testing:** pytest, pytest-cov
- **Deployment:** gcloud CLI, bash scripts

## Testing

### Run Tests
```bash
cd cloud-functions/nutrition-analyzer
pytest --cov=. --cov-report=html
```

### Test Coverage
- **Overall:** 100% coverage
- **Core modules:**
  - `nutrition_calculator.py` - 100%
  - `rule_engine.py` - 100%
  - `main.py` - 100%

### Manual Testing
```bash
# Test deployed function
curl -X POST https://nutrition-analyzer-epp4v6loga-uc.a.run.app \
  -H "Content-Type: application/json" \
  -d '{"food_items":[{"name":"chicken","quantity":1},{"name":"rice","quantity":1}]}'
```

## Configuration

### Environment Variables

**Required for USDA API:**
- `ENABLE_USDA_API` - Enable USDA API fallback (default: false)
- `USDA_API_KEY` - API key from https://fdc.nal.usda.gov/api-key-signup.html

**Optional:**
- `ENVIRONMENT` - Environment name (local/cloud)
- `LOG_EXECUTION_ID` - Enable execution ID logging (default: false)
- `NUTRITION_DB_PATH` - Path to static database JSON

### Get USDA API Key
1. Visit https://fdc.nal.usda.gov/api-key-signup.html
2. Sign up for free API key
3. Add to `.env` or deployment script

## API Reference

### Webhook Endpoint

**POST** `/analyze_nutrition`

**Request Body:**
```json
{
  "food_items": [
    {"name": "chicken", "quantity": 1},
    {"name": "rice", "quantity": 1}
  ]
}
```

**Response:**
```json
{
  "total_nutrition": {
    "calories": 330.0,
    "protein_g": 35.0,
    "carbs_g": 28.0,
    "fat_g": 5.6,
    "fiber_g": 0.4,
    "sodium_mg": 149.0,
    "vitamin_c_mg": 0.0,
    "calcium_mg": 25.0,
    "iron_mg": 1.7
  },
  "macro_percentages": {
    "protein_pct": 42,
    "carbs_pct": 34,
    "fat_pct": 15
  },
  "insights": [
    {
      "type": "recommendation",
      "message": "This meal is low in fiber. Consider adding vegetables..."
    }
  ],
  "follow_up": "Would you like ideas for adding more vegetables?"
}
```

## Performance

- **Static DB lookup:** < 50ms
- **USDA API fallback:** 1-2 seconds
- **Cold start:** 2-3 seconds (Cloud Function)
- **Warm requests:** < 100ms

## Contributing

This is a demonstration project. For production use, consider:
- Adding authentication and user accounts
- Implementing rate limiting
- Adding meal history persistence
- Expanding rule engine with more health insights
- Supporting dietary restrictions (vegan, gluten-free, etc.)

## License

MIT License - See [LICENSE](LICENSE)

## Maintainer

**Adam White** ([@adamkwhite](https://github.com/adamkwhite))

Built as a technical demonstration for interview process.
