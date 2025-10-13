# Virtual Dietitian MVP - Demo Script & Presentation Guide

## Demo Overview
**Duration:** 2-3 minutes
**Audience:** CEO and Chief Data Officer
**Goal:** Demonstrate AI-powered nutrition analysis with clear separation of LLM and deterministic logic

## Pre-Demo Checklist

### Technical Setup
- [ ] Cloud Function deployed and responding (test with curl)
- [ ] Vertex AI Agent published with shareable link
- [ ] Browser tabs ready:
  - Agent chat interface
  - GCP Cloud Functions console (for metrics)
  - Architecture diagram
- [ ] Screen recording software ready
- [ ] Test all 5 scenarios once before recording

### Test Cloud Function
```bash
curl -X POST https://nutrition-analyzer-epp4v6loga-uc.a.run.app \
  -H "Content-Type: application/json" \
  -d '{"food_items": [{"name": "chicken", "quantity": 1}]}'
```

Expected: JSON response with nutrition data and insights

## Demo Script (2-3 minutes)

### Opening (15 seconds)
**Visual:** Architecture diagram
**Script:**
> "I've built a Virtual Dietitian AI that demonstrates how we can combine LLMs with deterministic business logic for reliable, auditable nutrition analysis. Let me show you how it works."

### Architecture Overview (30 seconds)
**Visual:** Point to architecture diagram components
**Script:**
> "The system has two main components:
>
> First, a Vertex AI Agent handles natural language - it understands meal descriptions and generates friendly responses.
>
> Second, a Cloud Function webhook contains all the deterministic logic - nutrition calculations and business rules. This ensures we get accurate, reproducible results every time.
>
> The key insight is: LLMs handle language, not math or business logic. Let's see it in action."

### Live Demo - Test Case 1: Balanced Breakfast (45 seconds)
**Visual:** Switch to agent chat interface
**Input:**
```
I had oatmeal with blueberries and almond butter for breakfast
```

**Script while typing:**
> "I'll describe a balanced breakfast - oatmeal with blueberries and almond butter."

**Wait for response, then highlight:**
> "Notice three things:
>
> 1. **Accurate nutrition:** 332 calories, precise macro breakdown - this comes from the Cloud Function's calculations, not the LLM guessing.
>
> 2. **Intelligent insights:** It detected fruit and highlighted Vitamin C benefits. It also noticed the protein is a bit low and made a recommendation. These insights come from our rule engine - seven deterministic rules that fire based on meal composition.
>
> 3. **Conversational follow-up:** The LLM formats this data into a friendly response and asks a contextual question."

### Live Demo - Test Case 2: Edge Case (30 seconds)
**Visual:** Continue in agent chat
**Input:**
```
I just had an apple and banana
```

**Script:**
> "Let's try something simpler - just fruit."

**Wait for response, then highlight:**
> "The system correctly identifies this as very low protein - only about 5% of calories. It provides the Vitamin C benefit from fruit, but also recommends adding protein for satiety. Same deterministic rules, different meal composition."

### Technical Highlight (20 seconds)
**Visual:** Switch to Cloud Functions console (optional) or stay on chat
**Script:**
> "Behind the scenes, the Cloud Function has 100% test coverage - 32 unit tests all passing. The nutrition database uses USDA FoodData Central values, so every calorie count is accurate and traceable.
>
> This architecture means we can audit every insight, update business rules without retraining, and guarantee consistent results."

### Closing & Next Steps (10 seconds)
**Visual:** Return to architecture diagram or agent chat
**Script:**
> "This MVP demonstrates reliable AI for healthcare - combining LLM flexibility with deterministic accuracy. The architecture scales easily to thousands of foods, personalized recommendations, and multi-day tracking.
>
> Ready for your questions."

## Alternative Demo Flow (If Time Constrained: 90 seconds)

### Speed Demo Script
> "I've built a Virtual Dietitian AI that shows how to combine LLMs with business logic reliably. [Open agent]
>
> Watch this: [Type 'I had oatmeal with blueberries and almond butter for breakfast']
>
> See how it extracts the foods, calculates exact nutrition from our USDA database, applies business rules for insights, and formats a friendly response. The LLM handles language, the Cloud Function handles math and rules - 100% test coverage, zero hallucination risk.
>
> [Type 'I just had an apple and banana']
>
> Different meal, different insights - same deterministic logic. This architecture scales and audits cleanly. Questions?"

## Test Cases Reference

### Test Case 1: Balanced Breakfast ✅
**Input:** "I had oatmeal with blueberries and almond butter for breakfast"
**Expected:**
- 332 calories total
- Vitamin C benefit (fruit category)
- Fiber benefit (grain category)
- Protein recommendation (11% < 15%)

### Test Case 2: Fruit Snack 🍎
**Input:** "I just had an apple and banana"
**Expected:**
- ~160 calories total
- Vitamin C benefit (fruit category)
- Protein recommendation (very low protein)

### Test Case 3: Protein-Rich Meal 💪
**Input:** "I had grilled chicken, quinoa, and broccoli for lunch"
**Expected:**
- Well-balanced macros (25-35% protein)
- Positive feedback about balance
- Vitamin C benefit (vegetable)
- No warnings

### Test Case 4: High Sodium (Optional - if bacon/sausage added to DB) ⚠️
**Input:** "I ate bacon, sausage, and cheese for breakfast"
**Expected:**
- High sodium warning (>800mg)
- Recommendation to reduce salt
- Suggestion to add vegetables

### Test Case 5: Unknown Food (Error Handling) ❓
**Input:** "I had Martian space food for lunch"
**Expected:**
- Graceful handling of unknown food
- Agent asks for clarification or different description
- No fabricated nutrition data

## Key Talking Points

### Technical Excellence
- **100% test coverage:** 32 unit tests, all passing
- **USDA data:** All nutrition values are real, not fabricated
- **Sub-3 second response:** Meets performance requirements
- **Deterministic rules:** Same input always produces same output
- **Serverless scalability:** Cloud Functions auto-scale on demand

### Architecture Benefits
- **Auditability:** Every insight traces to specific rule or calculation
- **Maintainability:** Business rules update without model retraining
- **Testability:** Deterministic logic has full unit test coverage
- **Reliability:** No hallucination risk for nutrition data
- **Separation of concerns:** LLM for language, Cloud Function for logic

### Business Value
- **Fast implementation:** Built in ~2 hours (5 sessions x 25 min)
- **Production-ready patterns:** Can scale to full healthcare applications
- **Cost-efficient:** Pay-per-request serverless model
- **Extensible:** Easy to add foods, rules, or integrations

## Q&A Preparation

### Expected Questions & Answers

**Q: "How accurate is the nutrition data?"**
A: "All values come from USDA FoodData Central - the same database used by professional dietitians. The Cloud Function performs exact calculations using 4/4/9 calories per gram for macros. We have 47 foods now, but can easily scale to the full USDA database of 200,000+ foods."

**Q: "Can users track meals over time?"**
A: "The MVP is stateless by design for simplicity. Adding persistence is straightforward - we'd store meal logs in Cloud Firestore or BigQuery, then add trend analysis and historical insights. The architecture supports this without changes to core logic."

**Q: "What if the LLM misunderstands a food item?"**
A: "Great question. The webhook returns 'unknown_foods' in the response when it can't find something. The LLM is instructed to ask clarifying questions - you saw this with the 'Martian space food' test case. We handle ambiguity gracefully without fabricating data."

**Q: "How do you prevent hallucination?"**
A: "By architectural design. The LLM never generates nutrition numbers - it only extracts food names and formats responses. All calculations happen in the Cloud Function with 100% deterministic logic. The LLM is a language interface, not a data source."

**Q: "What's the cost to run this?"**
A: "Cloud Functions are ~$0.40 per million requests. For a user making 10 meal logs per day, that's ~$0.001 per month. Vertex AI Agent has free tier for development, then charges per session. Very cost-effective for healthcare applications."

**Q: "Can this integrate with existing systems?"**
A: "Absolutely. The Cloud Function is a standard REST API - it can be called from any application. We could integrate with meal planning apps, fitness trackers, or EHR systems. The agent itself can be embedded in websites, mobile apps, or Slack/Teams."

**Q: "How do you handle dietary restrictions or allergies?"**
A: "In the MVP, we don't persist user preferences. For production, we'd add a user profile system - store allergies, dietary restrictions (vegan, keto, etc.), and health goals. The rule engine would then apply personalized rules. The architecture already supports this - we'd just add more rule types."

**Q: "What about recipe recommendations?"**
A: "That's a natural next step. Once we track user preferences and history, we can use the LLM to suggest meals that fit their goals. The deterministic logic would validate recommendations meet nutritional targets before the LLM presents them. Same architecture pattern - LLM for creativity, Cloud Function for validation."

**Q: "How long did this take to build?"**
A: "About 2 hours total, across 5 focused sessions:
- Session 1: GCP setup (20 min)
- Session 2: Nutrition database (25 min)
- Session 3: Cloud Function + tests (30 min)
- Session 4: Agent configuration (15 min)
- Session 5: Testing + docs (30 min)

The PRD and task breakdown took another hour. So ~3 hours from idea to working demo."

**Q: "What's the path to production?"**
A: "Three main areas:
1. **Scale the database:** Integrate full USDA API or user-uploaded recipes
2. **Add persistence:** User profiles, meal history, trend tracking
3. **Enhanced rules:** Personalized recommendations based on health goals

The core architecture is production-ready - we'd primarily be adding features, not restructuring."

## Recording Tips

### Before Recording
1. Close unnecessary tabs and applications
2. Clear browser cache and agent conversation history
3. Test each input once to ensure agent is warm
4. Set browser zoom to 100% for clarity
5. Enable Do Not Disturb (no notifications)

### During Recording
1. Speak clearly and at moderate pace
2. Pause briefly after each agent response to let viewer read
3. Use mouse to highlight key numbers or insights
4. Keep cursor visible when pointing at UI elements
5. If demo fails, stay calm and explain the retry

### After Recording
1. Trim any dead air at start/end
2. Add captions if presenting to non-native English speakers
3. Export at 1080p minimum resolution
4. Share via unlisted YouTube link or Google Drive

## Backup Plans

### If Agent Doesn't Respond
1. Refresh the page and retry
2. Test webhook directly with curl (show in terminal)
3. Explain the architecture works, just UI connection issue
4. Fall back to showing test results and architecture diagram

### If Webhook Returns Error
1. Check Cloud Function logs in GCP console
2. Show the unit test results (all passing)
3. Explain the deterministic logic works in isolation
4. Demonstrate local testing if possible

### If Unknown Food Not in Database
1. Explain the 47-food MVP database scope
2. Show how easy it is to add foods (point to JSON structure)
3. Demonstrate graceful error handling with "Martian space food" test
4. Highlight this is a feature, not a bug (no fabrication)

## Post-Demo Actions

### Immediate Follow-Up
- [ ] Share recording link with stakeholders
- [ ] Provide architecture diagram (PDF export)
- [ ] Send GitHub repository link
- [ ] Share implementation log for transparency

### Documentation to Provide
1. `docs/demo/architecture.md` - Full technical architecture
2. `docs/demo/implementation-log.md` - Build timeline and decisions
3. `docs/demo/scalability-notes.md` - Production scaling analysis
4. `agent-config/test-cases.md` - Test case documentation
5. `README.md` - Project overview and quick start

### Questions to Ask Stakeholders
1. "What use cases beyond nutrition analysis interest you?"
2. "Would you like to see user profile and history features?"
3. "Should we explore integration with existing healthcare systems?"
4. "What's your timeline for production deployment?"
5. "Any specific regulatory requirements (HIPAA, etc.) to address?"

## Success Criteria for Demo

### Must Demonstrate
- ✅ Natural language meal description → structured data
- ✅ Accurate nutrition calculation (show numbers match USDA)
- ✅ Intelligent insights from rule engine
- ✅ Friendly conversational response from LLM
- ✅ Sub-3 second response time
- ✅ Graceful handling of unknown foods or edge cases

### Nice to Have
- ✅ Show Cloud Function metrics/logs
- ✅ Mention 100% test coverage
- ✅ Point out separation of concerns benefits
- ✅ Explain scalability path
- ✅ Reference USDA data source

### Demo Success Markers
- Stakeholders understand LLM vs. deterministic logic split
- Questions focus on "what's next" vs. "does it work"
- Interest in production deployment timeline
- Discussion of additional use cases or integrations
- Positive feedback on architecture approach

Good luck with the demo! 🚀
