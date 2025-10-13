# Product Requirements Document: Virtual Dietitian AI Agent MVP

**Status:** PLANNED
**Target Implementation Time:** 2-3 hours
**Last Updated:** October 12, 2025
**Owner:** Adam White

---

## 1. Introduction/Overview

The Virtual Dietitian is a conversational AI agent built on Google Cloud Agent Builder that analyzes meal descriptions and provides nutritional feedback. Users input free-text meal descriptions (e.g., "I had oatmeal with blueberries and almond butter for breakfast"), and the agent responds with:

- Brief nutritional assessment (calories, macros, key micronutrients)
- Health insights based on meal composition
- Follow-up questions or personalized recommendations

**Problem Statement:** Users need quick, accessible nutritional guidance without manual food logging or calorie counting apps. Traditional nutrition apps require tedious data entry; this agent makes logging conversational and provides instant, actionable feedback.

**Primary Goal:** Demonstrate rapid prototyping with GCP AI tools while showcasing clean architecture, thoughtful system design, and separation of concerns between NLU and business logic.

---

## 2. Goals

### Primary Goals
1. **Functional MVP:** Working end-to-end conversational agent that can analyze meal descriptions and provide nutritional feedback
2. **Technical Depth:** Demonstrate separation between LLM capabilities (NLU) and deterministic business logic (nutrient calculation, rule engine)
3. **Clean Architecture:** Clear data flow, testable components, well-structured codebase suitable for extension
4. **Demo-Ready:** Both live agent link and recorded video walkthrough

### Secondary Goals
1. **Extensibility:** Architecture that supports easy addition of new rules, data sources, and features
2. **Documentation:** Clear explanation of design choices, data flow, and state management approaches
3. **Scalability Considerations:** Document how the system would scale from 1 to 1M users

---

## 3. User Stories

**US1: Meal Logging**
As a health-conscious user, I want to describe what I ate in natural language, so that I can quickly log meals without tedious data entry.

**US2: Nutritional Feedback**
As a user, I want to receive immediate nutritional information about my meal (calories, protein, carbs, fat), so that I can understand what I'm consuming.

**US3: Health Insights**
As a user, I want to receive contextual health insights (e.g., "Great source of Vitamin C" for fruit), so that I can make informed dietary choices.

**US4: Recommendations**
As a user, I want to receive actionable recommendations (e.g., "Add more protein"), so that I can improve the nutritional balance of my meals.

**US5: Follow-up Questions**
As a user, I want the agent to ask relevant follow-up questions, so that I can get more detailed information if needed.

---

## 4. Functional Requirements

### Phase 1: MVP (Must Have - 2-3 hours)

**FR1: Natural Language Meal Input**
The system must accept free-text meal descriptions and extract food items using Vertex AI Agent Builder's NLU capabilities.

**FR2: Nutrition Database Lookup**
The system must maintain a JSON database of 50 common foods with the following data fields:
- Food name
- Serving size (grams)
- Calories
- Macronutrients (protein, carbs, fat in grams)
- Key micronutrients (Vitamin C, Iron, Calcium, Fiber)

**FR3: Nutrient Aggregation**
The system must aggregate nutritional values across all identified food items in a meal using a Cloud Function webhook.

**FR4: Tiered Rule Engine**
The system must implement three types of business logic rules:

- **Rule Type 1: Category Detection**
  If meal contains fruit → Add insight about vitamin benefits

- **Rule Type 2: Threshold Warnings**
  If sodium > 800mg → Warn about high sodium content

- **Rule Type 3: Macro Ratio Recommendations**
  If protein ratio < 15% of total calories → Recommend adding protein source

**FR5: Natural Language Response**
The system must generate conversational responses that include:
- Total calories
- Macro breakdown (protein/carbs/fat grams and percentages)
- Applied rule insights/warnings/recommendations
- One follow-up question

**FR6: Single-Turn Conversation**
The system must support stateless, single-turn interactions (no session memory required for MVP).

### Phase 2: USDA API Integration (Should Have - Documented)

**FR7: USDA FoodData Central Integration**
The system should integrate with USDA FoodData Central API to expand food database from 50 to 500+ items.

**FR8: Fallback Handling**
The system should gracefully handle unknown foods by prompting user for clarification or suggesting similar known foods.

### Phase 3: Enhanced Conversation (Nice to Have - Documented)

**FR9: Multi-Turn Conversation**
The system should support follow-up questions and context retention within a single session using Agent Builder session parameters.

**FR10: Meal History**
The system should store meal history in Firestore and calculate daily nutritional totals.

**FR11: Dietary Goals**
The system should allow users to set dietary goals (e.g., "low sodium", "high protein") and tailor recommendations accordingly.

---

## 5. Non-Goals (Out of Scope)

1. **User Authentication:** No login or user accounts in MVP
2. **Mobile App:** Web-based agent interface only
3. **Image Recognition:** Text input only; no photo-based meal logging
4. **Recipe Database:** Individual foods only; no complex recipes
5. **Medical Advice:** General nutrition info only; no personalized medical guidance
6. **Portion Size Estimation:** Assumes standard serving sizes unless user specifies
7. **Integration with Fitness Trackers:** Standalone system only
8. **Multi-Language Support:** English only for MVP

---

## 6. Design Considerations

### System Architecture

```
User Input (Text)
    ↓
[Vertex AI Agent Builder]
  - NLU: Extract food items & quantities
  - Intent recognition: log_meal
    ↓
[Vertex AI Search Datastore] ← nutrition_db.json
  - Lookup nutrition data for each food item
    ↓
[Cloud Function Webhook - Nutrition Analyzer]
  - Aggregate nutrients (sum calories, macros, micros)
  - Apply tiered rule engine:
    ✓ Category Detection (fruit → vitamin insight)
    ✓ Threshold Warnings (sodium > 800mg)
    ✓ Macro Ratio Check (protein < 15%)
  - Return structured JSON response
    ↓
[Vertex AI Agent Builder]
  - Natural language generation
  - Format response with insights & follow-up
    ↓
User Response (Text)
```

### Data Model

**Nutrition Database Entry (JSON):**
```json
{
  "id": "oatmeal_001",
  "name": "Oatmeal",
  "category": "grain",
  "serving_size_g": 40,
  "nutrition": {
    "calories": 150,
    "protein_g": 5,
    "carbs_g": 27,
    "fat_g": 3,
    "fiber_g": 4,
    "sodium_mg": 0,
    "vitamin_c_mg": 0,
    "iron_mg": 1.7,
    "calcium_mg": 20
  }
}
```

**Webhook Response Structure:**
```json
{
  "total_nutrition": {
    "calories": 430,
    "protein_g": 13,
    "carbs_g": 52,
    "fat_g": 18,
    "fiber_g": 8,
    "sodium_mg": 150
  },
  "macro_percentages": {
    "protein_pct": 12,
    "carbs_pct": 48,
    "fat_pct": 40
  },
  "insights": [
    {
      "type": "vitamin",
      "message": "Excellent source of Vitamin C and antioxidants from blueberries"
    },
    {
      "type": "recommendation",
      "message": "Consider adding protein (chicken, eggs, tofu) to reach 15-35% protein target"
    }
  ],
  "follow_up": "Would you like to know more about the fiber content in this meal?"
}
```

### UI/UX Flow

1. **User:** "I had oatmeal with blueberries and almond butter for breakfast"
2. **Agent:** "Thanks for logging your breakfast! Here's the nutritional breakdown:
   - **Total:** 430 calories
   - **Protein:** 13g (12%)
   - **Carbs:** 52g (48%)
   - **Fat:** 18g (40%)

   🍇 Excellent source of Vitamin C and antioxidants from blueberries

   💡 Consider adding protein (chicken, eggs, Greek yogurt) to reach the 15-35% protein target for a balanced meal.

   Would you like to know the fiber content?"

---

## 7. Technical Considerations

### Technology Stack
- **Agent Platform:** Google Cloud Vertex AI Agent Builder
- **LLM:** Gemini Pro (via Agent Builder)
- **Data Storage:** Vertex AI Search Datastore (Phase 1), Firestore (Phase 3)
- **Webhook Logic:** Cloud Functions (Python 3.11)
- **External API:** USDA FoodData Central API (Phase 2)

### Separation of Concerns

**LLM Responsibilities (Agent Builder):**
- Natural language understanding (extract foods from free text)
- Intent classification
- Natural language generation (conversational responses)
- Follow-up question generation

**Deterministic Logic (Cloud Function):**
- Nutrient aggregation (math operations)
- Rule engine evaluation
- Threshold comparisons
- Data validation

**Why This Separation Matters:**
- **Consistency:** Business rules produce identical outputs for identical inputs
- **Testability:** Unit tests validate rule logic without LLM dependency
- **Auditability:** Can explain exactly why a recommendation was made
- **Cost Efficiency:** LLM only used for NLU/NLG, not calculations
- **Reliability:** Core logic not subject to LLM variability

### State Management Progression

**Phase 1: Stateless (MVP)**
- Each request is independent
- No memory between interactions
- Simplest implementation, lowest complexity

**Phase 2: Session State (Multi-Turn)**
- Agent Builder session parameters
- Store: `current_meal_items[]`, `conversation_context`
- Enables follow-up questions within single session
- State expires after 20 minutes of inactivity

**Phase 3: Persistent State (Meal History)**
- Firestore collections: `users/{user_id}/meals/{meal_id}`
- Store: `meals_today[]`, `daily_totals`, `dietary_goals`
- Enables daily tracking and personalized recommendations
- Requires user identification mechanism

### Scalability Considerations

**Current Scale (Demo):**
- 1 user, 10 requests/day
- Agent Builder: Auto-scales
- Cloud Function: Cold starts acceptable (<1s)
- Datastore: In-memory JSON, <10ms lookup

**10,000 Users:**
- Agent Builder: No changes (auto-scales)
- Cloud Function: Set min instances = 5 (eliminate cold starts)
- Data: Migrate to Firestore with composite indexes
- Caching: Add Redis for top 100 most-queried foods

**1,000,000 Users:**
- Multi-region deployment (us-east1, europe-west1, asia-northeast1)
- CDN for static nutrition database
- Rate limiting: 100 requests/user/day
- Batch analytics: BigQuery for usage patterns
- Cost optimization: Smaller LLM for NLU, larger for generation

**Bottleneck:** LLM API costs, not infrastructure capacity

### Error Handling

1. **Unknown Food:** "I don't have nutritional data for [food]. Can you describe it differently, or would you like to continue with the foods I recognized?"
2. **API Timeout:** "Taking longer than expected. Please try again."
3. **Malformed Input:** Agent Builder prompt engineering to request clarification
4. **Webhook Failure:** Graceful degradation to LLM-only response without rule insights

---

## 8. Success Metrics

### Demo Success Criteria (Interview Context)
- ✅ Working end-to-end demo (live agent link functional)
- ✅ Video walkthrough (2-3 minutes) showing key capabilities
- ✅ Architecture documentation explaining design choices
- ✅ Clean codebase with separation of concerns
- ✅ Tested webhook logic with multiple meal scenarios

### Technical Metrics (If Deployed)
- **Response Time:** <2 seconds for meal analysis
- **Accuracy:** >90% correct food extraction from meal descriptions
- **Rule Application:** 100% consistent rule execution for same inputs
- **User Engagement:** Average 2+ meals logged per user per day

### Business Metrics (Future State)
- **Adoption:** 1,000 active users in first month
- **Retention:** 40% weekly active users return
- **Satisfaction:** >4.0/5.0 user rating

---

## 9. Implementation Plan (2-3 Hour Breakdown)

### Session 1: GCP Setup & Data Prep (30 min)
- Enable Vertex AI Agent Builder API
- Create Agent Builder agent
- Prepare 50-food nutrition JSON dataset
- Test basic agent greeting

### Session 2: Webhook Development (45 min)
- Create Cloud Function with Python
- Implement nutrient aggregation logic
- Implement tiered rule engine (3 rule types)
- Write unit tests for rule logic
- Deploy function and test endpoint

### Session 3: Agent Configuration (45 min)
- Upload nutrition database to Vertex AI Search datastore
- Configure webhook integration in Agent Builder
- Write agent instructions/prompts
- Test end-to-end meal logging flow
- Debug and refine responses

### Session 4: Demo & Documentation (30 min)
- Record demo video (2-3 min)
- Create architecture diagram
- Write architecture documentation
- Document Phase 2 & 3 approach
- Commit to GitHub

### Buffer: Debugging (30 min)
- Resolve integration issues
- Fine-tune agent responses
- Handle edge cases

---

## 10. Open Questions

1. **Food Name Variations:** How should we handle synonyms (e.g., "oats" vs "oatmeal")?
   - **Approach:** Include common aliases in JSON; use fuzzy matching in webhook

2. **Quantity Extraction:** How precise do we need quantity extraction (e.g., "a bowl of oatmeal" vs "40g oatmeal")?
   - **Phase 1 Approach:** Assume standard serving sizes if quantity not specified
   - **Phase 2 Enhancement:** Train quantity extraction with examples

3. **Meal Type Context:** Should recommendations differ for breakfast vs dinner?
   - **Phase 1:** Generic recommendations
   - **Phase 3:** Meal-type-specific guidance

4. **Multi-Food Ambiguity:** How to handle "chicken salad" (is it a prepared dish or chicken + salad)?
   - **Phase 1:** Treat as individual components
   - **Phase 2:** Add common prepared foods to database

---

## 11. Appendix

### Food Selection Criteria (50 Foods)

**Categories to Cover:**
- Proteins: chicken, salmon, tofu, eggs, Greek yogurt, almonds
- Grains: oatmeal, rice, quinoa, whole wheat bread, pasta
- Fruits: apple, banana, blueberries, strawberries, orange
- Vegetables: broccoli, spinach, carrots, tomato, avocado
- Dairy: milk, cheese, butter
- Fats: olive oil, almond butter, peanut butter
- Common prepared items: pizza, burger, salad

**Prioritization:**
1. Most commonly logged foods in nutrition apps
2. Variety across food groups for balanced meal testing
3. Items with interesting rule engine test cases (high sodium, high protein, vitamin-rich)

### USDA API Integration Notes (Phase 2)

**API Endpoint:** https://api.nal.usda.gov/fdc/v1/foods/search
**Required:** API key (free registration)
**Rate Limit:** 3,600 requests/hour (1 request/second)

**Implementation Approach:**
1. Query USDA API during webhook processing
2. Cache results in Firestore (TTL: 30 days)
3. Fallback to static JSON if API unavailable
4. Pre-populate cache with top 500 foods during setup

### Testing Scenarios

**Test Case 1: Balanced Breakfast**
- Input: "oatmeal with blueberries and almond butter"
- Expected: Positive feedback, vitamin insight, minor protein recommendation

**Test Case 2: High Sodium Meal**
- Input: "bacon, sausage, and cheese"
- Expected: Sodium warning, recommend vegetables

**Test Case 3: Protein-Rich Meal**
- Input: "grilled chicken, quinoa, and broccoli"
- Expected: Positive feedback, well-balanced message

**Test Case 4: Fruit Snack**
- Input: "apple and banana"
- Expected: Vitamin insight, suggest adding protein for satiety

**Test Case 5: Unknown Food**
- Input: "Martian space food"
- Expected: Graceful fallback, request clarification

---

## 12. References

- USDA Dietary Guidelines: https://www.dietaryguidelines.gov/
- FoodData Central API: https://fdc.nal.usda.gov/api-guide.html
- Vertex AI Agent Builder Docs: https://cloud.google.com/agent-builder/docs
- Recommended Macro Ranges: Protein 15-35%, Carbs 45-65%, Fat 20-35%

---

**Document Version:** 1.0
**Next Steps:** Generate task breakdown using `generate-tasks.md`
**Status:** Ready for implementation
