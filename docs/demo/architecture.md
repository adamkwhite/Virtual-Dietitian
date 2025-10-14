# Virtual Dietitian MVP - Architecture Documentation

## System Overview

The Virtual Dietitian MVP is a conversational AI system that analyzes meal descriptions and provides personalized nutritional feedback. The architecture separates concerns between natural language processing (handled by LLM) and deterministic business logic (handled by Cloud Function webhook).

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│                  (Vertex AI Agent Builder UI)                │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Natural language input
                             │ "I had oatmeal with blueberries"
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Vertex AI Agent (LLM Component)                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Natural Language Understanding (NLU)                │   │
│  │  - Extract food items from user message              │   │
│  │  - Parse quantities and meal context                 │   │
│  │  - Map to structured data format                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Natural Language Generation (NLG)                   │   │
│  │  - Format webhook response into friendly message     │   │
│  │  - Apply conversational tone and empathy             │   │
│  │  - Ask follow-up questions from webhook              │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Structured request
                             │ {"food_items": [...]}
                             ▼
┌─────────────────────────────────────────────────────────────┐
│         Cloud Function: nutrition-analyzer (Webhook)         │
│                    (Deterministic Logic)                     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Nutrition Calculator                                │   │
│  │  - Load nutrition database (47 foods)                │   │
│  │  - Look up foods by name/alias                       │   │
│  │  - Aggregate nutrients with quantity multipliers     │   │
│  │  - Calculate macro percentages (4/4/9 cal/g)         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Rule Engine (3 Rule Types)                          │   │
│  │  - Category Rules: fruit → Vitamin C benefit         │   │
│  │  - Threshold Rules: sodium > 800mg → warning         │   │
│  │  - Macro Ratio Rules: protein < 15% → add protein    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Response Generator                                   │   │
│  │  - Compile total nutrition                           │   │
│  │  - Package insights from rule engine                 │   │
│  │  - Generate contextual follow-up question            │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Structured response
                             │ {nutrition, insights, follow_up}
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nutrition Database                        │
│                  (USDA FoodData Central)                     │
│                                                              │
│  47 foods across 6 categories:                              │
│  - Protein (chicken, salmon, tofu, eggs...)                 │
│  - Grain (oatmeal, quinoa, rice, bread...)                  │
│  - Fruit (apple, banana, strawberries...)                   │
│  - Vegetable (broccoli, spinach, carrots...)                │
│  - Dairy (milk, yogurt, cheese...)                          │
│  - Fat (avocado, olive oil, almonds...)                     │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### 1. Vertex AI Agent (LLM Component)
**Purpose:** Natural language understanding and generation
**Responsibilities:**
- Parse user's meal descriptions into structured food items
- Extract quantities and handle variations ("half a banana", "two eggs")
- Format webhook responses into conversational, empathetic messages
- Ask clarifying questions when input is ambiguous
- Maintain friendly, supportive tone throughout conversation

**Why LLM:** Natural language is inherently variable - same food can be described many ways. LLM handles this ambiguity gracefully.

### 2. Cloud Function Webhook
**Purpose:** Deterministic business logic and nutrition analysis
**Responsibilities:**
- Calculate precise nutritional values (no randomness)
- Apply consistent business rules (same input → same output)
- Generate data-driven insights based on meal composition
- Provide follow-up questions tailored to nutritional context

**Why Deterministic:** Nutrition calculations must be exact and reproducible. Business rules must apply consistently.

### 3. Separation of Concerns Benefits
- **Testability:** Cloud Function logic has 100% test coverage (32/32 tests passing)
- **Reliability:** Nutrition calculations are always accurate, never hallucinated
- **Maintainability:** Business rules can be updated without retraining LLM
- **Auditability:** Every insight can be traced to specific rule or calculation
- **Performance:** Lightweight webhook responds in <500ms

## Data Flow

### Request Flow (User Input → Response)

```
1. User Input
   "I had oatmeal with blueberries and almond butter for breakfast"

2. LLM Processing (NLU)
   Extracts: [
     {"name": "oatmeal", "quantity": 1},
     {"name": "blueberries", "quantity": 1},
     {"name": "almond butter", "quantity": 1}
   ]

3. Webhook Request (HTTP POST)
   POST https://nutrition-analyzer-epp4v6loga-uc.a.run.app
   {
     "food_items": [
       {"name": "oatmeal", "quantity": 1},
       {"name": "blueberries", "quantity": 1},
       {"name": "almond butter", "quantity": 1}
     ]
   }

4. Cloud Function Processing
   a. Nutrition Calculation:
      - Lookup foods in database (O(1) hash lookup)
      - Aggregate nutrients with quantities
      - Calculate macro percentages

   b. Rule Engine Evaluation:
      - CategoryRule: fruit → Vitamin C benefit ✅
      - CategoryRule: grain → Fiber benefit ✅
      - MacroRatioRule: 11% protein → Add protein recommendation ✅
      - ThresholdRule: 95mg sodium → No warning (< 800mg) ❌

   c. Response Compilation:
      {
        "total_nutrition": {
          "calories": 332,
          "protein_g": 9,
          "carbs_g": 48,
          "fat_g": 12,
          ...
        },
        "macro_percentages": {
          "protein_pct": 11,
          "carbs_pct": 58,
          "fat_pct": 31
        },
        "insights": [
          {"type": "benefit", "message": "Excellent source of Vitamin C..."},
          {"type": "benefit", "message": "Great source of fiber..."},
          {"type": "recommendation", "message": "Consider adding protein..."}
        ],
        "follow_up": "Would you like suggestions for protein additions?"
      }

5. LLM Processing (NLG)
   Formats webhook data into natural response:

   "Great choice! Here's your nutritional breakdown:

   📊 Total: 332 calories
   - Protein: 9g (11%)
   - Carbs: 48g (58%)
   - Fat: 12g (31%)

   ✨ Health Insights:
   • Excellent source of Vitamin C from your fruit - supports immune health!
   • Great source of fiber from whole grains - promotes digestive health
   • Consider adding a protein source to make this meal more balanced

   Would you like suggestions for protein additions?"

6. User sees final formatted response
```

## Rule Engine Architecture

### Three-Tier Rule System

**Tier 1: Category Rules**
- **Trigger:** Presence of food from specific category
- **Example:** fruit → "Excellent source of Vitamin C"
- **Implementation:** Check if category in `food_categories` set
- **Test coverage:** 4 tests (trigger/non-trigger for 2 categories)

**Tier 2: Threshold Rules**
- **Trigger:** Nutrient exceeds/falls below threshold
- **Example:** sodium > 800mg → "High sodium warning"
- **Implementation:** Compare `total_nutrition[nutrient]` to threshold with operator
- **Test coverage:** 6 tests (>, <, >=, <= operators)

**Tier 3: Macro Ratio Rules**
- **Trigger:** Macro percentage outside healthy range
- **Example:** protein < 15% → "Consider adding protein"
- **Implementation:** Check `macro_percentages[macro]` against min/max bounds
- **Test coverage:** 5 tests (below min, above max, within range)

### Rule Extensibility

Adding new rules requires zero code changes to core logic:

```python
# Add to RULES list in rule_engine.py
RULES = [
    # Existing rules...

    # New rule - just add to list!
    ThresholdRule(
        nutrient='sugar_g',
        threshold=25,
        operator='>',
        insight_type='warning',
        message='High sugar content. Consider reducing added sugars.'
    ),
]
```

## Technology Stack

### Google Cloud Platform
- **Vertex AI Agent Builder:** Conversational AI interface with built-in LLM
- **Cloud Functions Gen2:** Serverless webhook for business logic
- **Cloud Run:** Underlying infrastructure for Cloud Functions
- **Vertex AI Search:** (Future) Enhanced data retrieval capabilities

### Python Stack
- **Python 3.12:** Latest stable version
- **functions-framework 3.x:** Cloud Functions HTTP handler
- **python-dotenv 1.x:** Environment configuration
- **pytest 8.x + pytest-cov 6.x:** Testing framework

### Development Tools
- **Pre-commit hooks:** Black, isort, flake8 for code quality
- **Virtual environment:** Isolated dependency management
- **Git workflow:** Feature branches, PR-based deployment

## Environment Configuration

### Local Development
```bash
# .env (project root)
ENVIRONMENT=local
NUTRITION_DB_PATH=../../data/nutrition_db.json
```

### Cloud Deployment
```bash
# Set via deployment flags
--set-env-vars ENVIRONMENT=cloud,NUTRITION_DB_PATH=./nutrition_db.json
```

### Config Class
```python
class Config:
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')
    NUTRITION_DB_PATH = os.getenv('NUTRITION_DB_PATH', '../../data/nutrition_db.json')

    @classmethod
    def is_cloud(cls):
        return cls.ENVIRONMENT == 'cloud'
```

## Testing Strategy

### Unit Tests (32 tests, 100% pass rate)

**Nutrition Calculator Tests (17 tests)**
- Food lookup by name, alias, case-insensitive
- Single and multiple food calculations
- Quantity multipliers (0.5x, 2x servings)
- Unknown food handling
- Macro percentage calculations
- Edge cases (empty input, zero values)

**Rule Engine Tests (15 tests)**
- Category rule triggering conditions
- Threshold rule operators (>, <, >=, <=)
- Macro ratio boundary conditions
- Multiple simultaneous rule triggers
- Rule priority and ordering

### Integration Testing (Manual - Session 5)
1. Balanced breakfast test (oatmeal + blueberries + almond butter)
2. High sodium test (bacon + sausage + cheese)
3. Protein-rich test (chicken + quinoa + broccoli)
4. Fruit snack test (apple + banana)
5. Unknown food test (graceful error handling)

## Deployment Architecture

### Cloud Function Deployment
```bash
gcloud functions deploy nutrition-analyzer \
  --gen2 \
  --runtime=python312 \
  --region=us-central1 \
  --source=cloud-functions/nutrition-analyzer \
  --entry-point=analyze_nutrition \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=cloud,NUTRITION_DB_PATH=./nutrition_db.json
```

**Deployed URL:** https://nutrition-analyzer-epp4v6loga-uc.a.run.app

### Vertex AI Agent Deployment
- **Manual configuration:** Vertex AI Agent Builder UI
- **Configuration files:** `agent-config/` directory
- **Webhook integration:** HTTP POST to Cloud Function
- **Publishing:** One-click deploy to shareable link

## Performance Characteristics

### Response Times
- **Cloud Function cold start:** ~1-2 seconds
- **Cloud Function warm:** <500ms
- **LLM processing:** 1-2 seconds
- **Total end-to-end:** <3 seconds (meets PRD requirement)

### Scalability Considerations
- **Current:** Handles single-user demo load
- **Database:** 47 foods sufficient for MVP, expandable to thousands
- **Webhook:** Serverless auto-scaling (Cloud Run)
- **Cost:** Pay-per-request, ~$0.40 per million requests

See `docs/demo/scalability-notes.md` for detailed scaling analysis.

## Security & Privacy

### Current Implementation (MVP)
- **Authentication:** Public webhook (--allow-unauthenticated)
- **Data storage:** None (stateless processing)
- **User tracking:** None (no persistence)

### Production Considerations
- Add OAuth 2.0 for webhook authentication
- Implement user sessions for multi-meal tracking
- Add data encryption for stored nutrition logs
- HIPAA compliance for health data (if required)

## Limitations & Future Enhancements

### Current Limitations
1. **Food database:** 47 foods (expandable to full USDA database)
2. **No persistence:** Stateless per-conversation (by design for MVP)
3. **No user profiles:** Can't track dietary preferences or restrictions
4. **No meal history:** Can't analyze trends over time

### Planned Enhancements (Post-MVP)
1. **Expanded database:** Integrate full USDA FoodData Central API
2. **User profiles:** Store dietary goals, allergies, preferences
3. **Meal history:** Track nutrition over days/weeks
4. **Advanced analytics:** Micronutrient tracking, trend analysis
5. **Recipe suggestions:** Proactive meal recommendations
6. **Integration:** Connect to fitness trackers, meal planning apps

## References

- **PRD:** `docs/features/virtual-dietitian-mvp-PLANNED/prd.md`
- **Implementation Log:** `docs/demo/implementation-log.md`
- **Agent Configuration:** `agent-config/SETUP_GUIDE.md`
- **Cloud Function Source:** `cloud-functions/nutrition-analyzer/`
- **Test Cases:** `agent-config/test-cases.md`
