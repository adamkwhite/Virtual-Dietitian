# Agent Test Cases (from PRD)

## Test Case 1: Balanced Breakfast ✅
**Input:** "I had oatmeal with blueberries and almond butter for breakfast"

**Expected Webhook Request:**
```json
{
  "food_items": [
    {"name": "oatmeal", "quantity": 1},
    {"name": "blueberries", "quantity": 1},
    {"name": "almond butter", "quantity": 1}
  ]
}
```

**Expected Response Elements:**
- Total: 332 calories
- Macros: 11% protein, 58% carbs, 31% fat
- ✅ Vitamin insight (fruit category)
- ✅ Fiber insight (grain category)
- ✅ Protein recommendation (11% < 15%)

---

## Test Case 2: High Sodium Meal ⚠️
**Input:** "I ate bacon, sausage, and cheese for breakfast"

**Expected Webhook Request:**
```json
{
  "food_items": [
    {"name": "bacon", "quantity": 1},
    {"name": "sausage", "quantity": 1},
    {"name": "cheese", "quantity": 1}
  ]
}
```

**Expected Response Elements:**
- ⚠️ High sodium warning (> 800mg)
- Recommendation to reduce salt or choose lower-sodium options
- May suggest adding vegetables

**Note:** Bacon and sausage not in current 47-food database. May need to add or will get "unknown food" response.

---

## Test Case 3: Protein-Rich Meal 💪
**Input:** "I had grilled chicken, quinoa, and broccoli for lunch"

**Expected Webhook Request:**
```json
{
  "food_items": [
    {"name": "chicken", "quantity": 1},
    {"name": "quinoa", "quantity": 1},
    {"name": "broccoli", "quantity": 1}
  ]
}
```

**Expected Response Elements:**
- Well-balanced macros (protein likely 25-35%)
- ✅ Positive feedback about meal balance
- ✅ Vitamin C insight (vegetable)
- No warnings or major recommendations

---

## Test Case 4: Fruit Snack 🍎
**Input:** "I just had an apple and banana"

**Expected Webhook Request:**
```json
{
  "food_items": [
    {"name": "apple", "quantity": 1},
    {"name": "banana", "quantity": 1}
  ]
}
```

**Expected Response Elements:**
- Low calories (~160 total)
- ✅ Vitamin C insight (fruit category)
- ✅ Recommendation to add protein for satiety
- Low protein percentage (< 5%)

---

## Test Case 5: Unknown Food (Error Handling) ❓
**Input:** "I had Martian space food for lunch"

**Expected Behavior:**
- Webhook returns unknown_foods: ["Martian space food"]
- Agent acknowledges unknown food gracefully
- Agent suggests user describe it differently or provides clarification request
- No nutritional data displayed (since no recognized foods)

**Expected Agent Response:**
"I don't have nutritional data for 'Martian space food'. Could you describe it differently, or let me know what ingredients it contains? For example, is it similar to any common foods?"

---

## Additional Test Cases

### Test Case 6: Quantity Specification
**Input:** "I had half a banana and two eggs"

**Expected:**
- Banana: quantity 0.5
- Eggs: quantity 2
- Correct calorie calculation with quantities

### Test Case 7: Multiple Meal Logging
**Input 1:** "I had oatmeal for breakfast"
**Input 2:** "And for lunch I had chicken and rice"

**Expected:**
- Each treated as separate meal analysis
- No aggregation across conversations (stateless MVP)

### Test Case 8: Vague Input
**Input:** "I ate food"

**Expected:**
- Agent asks clarifying questions
- "What specific foods did you eat? For example, did you have protein like chicken, grains like rice, or fruits and vegetables?"

---

## Success Criteria for Each Test

For agent to pass testing:
1. ✅ Correctly extracts food items from natural language
2. ✅ Calls webhook with proper JSON format
3. ✅ Displays nutritional summary clearly
4. ✅ Shows all relevant insights from rule engine
5. ✅ Asks follow-up question from webhook
6. ✅ Handles unknown foods gracefully
7. ✅ Maintains friendly, supportive tone
8. ✅ Response time < 3 seconds
