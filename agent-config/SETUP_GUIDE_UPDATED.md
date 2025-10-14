# Vertex AI Agent Builder Setup Guide (Updated 2025)

## Important: Interface Changes

The Vertex AI Agent Builder UI has changed. **Webhooks are now added as "Tools"** (specifically OpenAPI tools), not in a separate "Webhooks" or "Fulfillment" section.

## Step-by-Step Configuration

### Step 1: Access Agent Builder
1. Go to GCP Console: https://console.cloud.google.com
2. Navigate to **Vertex AI** → **Agent Builder**
3. Or direct link: https://console.cloud.google.com/gen-app-builder/engines

### Step 2: Create New Agent
1. Click **"Create Agent"** or **"Create App"**
2. Choose **"Agent"** as the type (not Search or Chat app)
3. Agent Settings:
   - **Name:** Virtual Dietitian MVP
   - **Region:** us-central1 (same as Cloud Function)
   - **Language:** English

### Step 3: Configure Agent Instructions
1. In the agent settings, find **"Agent Instructions"** or **"Instructions"** tab
2. Copy the entire content from `agent-config/agent-instructions.txt`
3. Paste into the instructions field
4. Click **Save**

### Step 4: Add OpenAPI Tool (Webhook)

**NEW APPROACH - Use OpenAPI Tool instead of webhook:**

1. Look for **"Tools"** section in the left sidebar or agent settings
2. Click **"+ Create Tool"** or **"Add Tool"**
3. Select **"OpenAPI"** as tool type
4. Configure the OpenAPI tool:

   **Option A: Use OpenAPI Specification (Recommended)**
   - **Tool Name:** nutrition-analyzer
   - **OpenAPI Spec:** Upload or paste this OpenAPI schema:

```yaml
openapi: 3.0.0
info:
  title: Nutrition Analyzer API
  version: 1.0.0
  description: Analyzes food items and returns nutritional information
servers:
  - url: https://nutrition-analyzer-epp4v6loga-uc.a.run.app
paths:
  /:
    post:
      summary: Analyze nutrition for food items
      operationId: analyzeNutrition
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                food_items:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                        description: Name of the food item
                      quantity:
                        type: number
                        description: Quantity/serving size
                    required:
                      - name
                      - quantity
              required:
                - food_items
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  total_nutrition:
                    type: object
                    properties:
                      calories:
                        type: number
                      protein_g:
                        type: number
                      carbs_g:
                        type: number
                      fat_g:
                        type: number
                      fiber_g:
                        type: number
                      sodium_mg:
                        type: number
                  macro_percentages:
                    type: object
                    properties:
                      protein_pct:
                        type: integer
                      carbs_pct:
                        type: integer
                      fat_pct:
                        type: integer
                  insights:
                    type: array
                    items:
                      type: object
                      properties:
                        type:
                          type: string
                        message:
                          type: string
                  follow_up:
                    type: string
```

   - **Authentication:** None (function is public with --allow-unauthenticated)
   - **Description:** "Analyzes food items and returns detailed nutritional information including calories, macros, and health insights"

   **Option B: Manual Configuration (if OpenAPI not available)**
   - **Tool Type:** Function/Extension
   - **Endpoint URL:** https://nutrition-analyzer-epp4v6loga-uc.a.run.app
   - **Method:** POST
   - **Headers:** Content-Type: application/json
   - **Request format:** See webhook-config.json for schema

5. Click **"Test Tool"** to verify it works
   - Use test payload: `{"food_items": [{"name": "chicken", "quantity": 1}]}`
   - Should return nutrition data

6. Click **"Save"** or **"Create"**

### Step 5: Enable Tool for Agent

After creating the tool, you need to enable it for use:

1. Go back to your agent's main configuration
2. Look for **"Tools"** or **"Available Tools"** section
3. Find **"nutrition-analyzer"** in the list
4. Toggle it **ON** or check the box to enable it
5. Configure when the agent should use this tool:
   - **Trigger:** When user describes a meal or food items
   - **Examples:** "I had chicken and rice", "I ate an apple"

### Step 6: Configure Training Phrases (Optional but Recommended)

While Vertex AI Agent Builder can understand meal logging naturally, adding training phrases improves accuracy:

1. If there's an **"Examples"** or **"Training Phrases"** section:
   - Add phrases from `agent-config/training-phrases.txt`
   - Focus on variations like:
     - "I had oatmeal with blueberries for breakfast"
     - "I ate chicken and rice for lunch"
     - "Just had an apple and banana"

2. If using **"Intents"** (older UI):
   - Create intent named: `log_meal`
   - Add training phrases from the file
   - Enable tool calling for this intent

### Step 7: Test in Simulator

1. Look for **"Test"**, **"Simulator"**, or **"Try it out"** button
2. Open the test interface
3. Test with sample inputs from `agent-config/test-cases.md`:

   **Test 1:**
   ```
   I had oatmeal with blueberries and almond butter for breakfast
   ```
   Expected: Nutrition summary with 332 calories, insights about Vitamin C, fiber, and protein recommendation

   **Test 2:**
   ```
   I just had an apple and banana
   ```
   Expected: ~160 calories, Vitamin C benefit, protein recommendation

4. Verify:
   - ✅ Agent extracts food items correctly
   - ✅ Tool is called with proper JSON format
   - ✅ Response includes nutrition data
   - ✅ Insights are displayed
   - ✅ Follow-up question is asked
   - ✅ Response time < 3 seconds

### Step 8: Debug Tool Integration

**If tool isn't being called:**

1. Check **Tool Logs** or **Execution Logs**:
   - Look for tool invocation attempts
   - Check for authentication errors
   - Verify request format

2. **Test the Cloud Function directly:**
   ```bash
   curl -X POST https://nutrition-analyzer-epp4v6loga-uc.a.run.app \
     -H "Content-Type: application/json" \
     -d '{"food_items": [{"name": "chicken", "quantity": 1}]}'
   ```
   Should return JSON with nutrition data

3. **Common issues:**
   - Tool not enabled for agent → Enable in Tools section
   - Wrong URL → Verify Cloud Function URL
   - Authentication blocking → Confirm --allow-unauthenticated
   - Schema mismatch → Verify OpenAPI spec matches actual API

### Step 9: Improve Agent Instructions (if needed)

If the agent doesn't use the tool correctly, update instructions:

1. Go back to **Agent Instructions**
2. Add explicit tool usage guidance:
   ```
   When a user describes what they ate, always:
   1. Extract the food items and quantities
   2. Call the nutrition-analyzer tool with the food_items parameter
   3. Format the response with the nutrition data provided
   4. Include all insights from the tool response
   5. Ask the follow-up question provided by the tool
   ```

### Step 10: Publish Agent

1. Once testing is successful, click **"Publish"** or **"Deploy"**
2. Choose deployment target:
   - **Web integration** (shareable link)
   - **Embed code** (for website)
   - **API endpoint** (for custom integration)
3. Copy the shareable link
4. Add to `docs/demo/implementation-log.md`:
   ```
   - Agent URL: [your-shareable-link]
   ```

## Alternative: Using Dialogflow CX Directly

If Vertex AI Agent Builder doesn't expose tool configuration clearly, you can use Dialogflow CX (which powers Agent Builder):

1. Go to **Dialogflow CX Console**: https://dialogflow.cloud.google.com/cx/
2. Find your agent (created by Agent Builder)
3. Navigate to **Manage → Webhooks**
4. Add webhook with:
   - Name: nutrition-analyzer
   - URL: https://nutrition-analyzer-epp4v6loga-uc.a.run.app
   - Method: POST
5. Create fulfillment in your flow to call this webhook

## Troubleshooting

### Issue: Can't find "Tools" section
**Solution:** UI varies by region and rollout. Try:
- Look for **"Extensions"**, **"Functions"**, or **"Integrations"**
- Check the **"Manage"** section in left sidebar
- Use Dialogflow CX console instead (link above)

### Issue: OpenAPI schema validation errors
**Solution:**
- Ensure you're using OpenAPI 3.0.0 format
- Validate schema at https://editor.swagger.io
- Simplify schema to just the required fields first

### Issue: Tool not being invoked
**Solution:**
- Add explicit instructions: "Always call nutrition-analyzer when user describes food"
- Check tool is enabled/toggled ON for the agent
- Verify agent instructions mention the tool

### Issue: Authentication errors
**Solution:**
- Confirm Cloud Function is deployed with `--allow-unauthenticated`
- If using service account auth, add Agent Builder service account to Cloud Function invokers
- Test function URL directly in browser or curl

## Quick Test Command

To verify your Cloud Function is accessible:

```bash
# Should return 200 OK with nutrition JSON
curl -v -X POST https://nutrition-analyzer-epp4v6loga-uc.a.run.app \
  -H "Content-Type: application/json" \
  -d '{
    "food_items": [
      {"name": "oatmeal", "quantity": 1},
      {"name": "blueberries", "quantity": 0.5}
    ]
  }'
```

## Next Steps After Setup

1. Run all test cases from `agent-config/test-cases.md`
2. Record demo using `docs/demo/demo-script.md`
3. Share agent link with stakeholders
4. Document any UI differences you encountered (helps future users)

## Need Help?

- **Vertex AI Agent Builder Docs:** https://cloud.google.com/dialogflow/vertex/docs
- **OpenAPI Tools Guide:** https://cloud.google.com/dialogflow/vertex/docs/concept/tools
- **Dialogflow CX Console:** https://dialogflow.cloud.google.com/cx/
- **Cloud Function Logs:** https://console.cloud.google.com/functions (check for errors)
