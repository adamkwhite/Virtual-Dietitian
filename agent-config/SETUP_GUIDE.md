# Vertex AI Agent Builder Setup Guide

## Step-by-Step Configuration

### Step 1: Access Agent Builder
1. Go to GCP Console: https://console.cloud.google.com
2. Navigate to **Vertex AI** → **Agent Builder**
3. Or direct link: https://console.cloud.google.com/gen-app-builder/engines

### Step 2: Create New Agent
1. Click **"Create Agent"** or **"Create App"**
2. Choose **"Chat"** as the agent type
3. Agent Settings:
   - **Name:** Virtual Dietitian MVP
   - **Region:** us-central1 (same as Cloud Function)
   - **Language:** English
   - **Company name:** (Your name or company)

### Step 3: Configure Agent Instructions
1. In the agent settings, find **"Agent Instructions"** or **"System Instructions"**
2. Copy the entire content from `agent-config/agent-instructions.txt`
3. Paste into the instructions field
4. Save

### Step 4: Create Webhook Integration
1. Go to **"Webhooks"** or **"Fulfillment"** section
2. Click **"Add Webhook"**
3. Configure:
   - **Webhook Name:** nutrition-analyzer
   - **URL:** https://nutrition-analyzer-epp4v6loga-uc.a.run.app
   - **Method:** POST
   - **Headers:** Content-Type: application/json
   - **Authentication:** None (function is public)

### Step 5: Configure Intent & Training Phrases
1. Create a new **Intent** named `log_meal`
2. Add training phrases (examples of user input):
   ```
   I had oatmeal with blueberries for breakfast
   I ate chicken and rice for lunch
   Just had an apple and banana
   I had salmon, quinoa, and broccoli
   Scrambled eggs with whole wheat toast
   Greek yogurt with strawberries
   Grilled chicken salad
   Oatmeal and almond butter
   I ate a bagel with cream cheese
   Just finished eating tuna and carrots
   ```

3. Link this intent to the webhook:
   - In the intent configuration, enable **"Use webhook"**
   - Select the `nutrition-analyzer` webhook

### Step 6: Configure Webhook Parameters
In the webhook call configuration:

**Request Parameters:**
```json
{
  "food_items": "$extracted_foods"
}
```

The agent should extract food items from the user's message and populate the `food_items` array with `name` and `quantity` fields.

**Response Usage:**
Configure the agent to use these fields from the webhook response:
- `total_nutrition.*` - Display nutritional totals
- `macro_percentages.*` - Show macro breakdown
- `insights[]` - List health insights
- `follow_up` - Ask this question to the user

### Step 7: Test in Simulator
1. Click **"Test Agent"** or **"Simulate"** in the Agent Builder
2. Test with sample inputs:
   - "I had oatmeal with blueberries and almond butter for breakfast"
   - "I ate grilled chicken, quinoa, and broccoli for lunch"
   - "Just had an apple and banana"

3. Verify:
   - ✅ Agent extracts food items correctly
   - ✅ Webhook is called with correct format
   - ✅ Response is formatted properly
   - ✅ Insights are displayed
   - ✅ Follow-up question is asked

### Step 8: Debug Common Issues

**Issue: Webhook not being called**
- Check that intent is linked to webhook
- Verify webhook URL is correct
- Test webhook directly with curl (see below)

**Issue: Foods not extracted**
- Add more training phrases
- Check agent instructions for food extraction protocol
- Verify parameter mapping is correct

**Issue: Response formatting incorrect**
- Review agent instructions for response template
- Check that all webhook response fields are being used

**Test Webhook Directly:**
```bash
curl -X POST https://nutrition-analyzer-epp4v6loga-uc.a.run.app \
  -H "Content-Type: application/json" \
  -d '{
    "food_items": [
      {"name": "chicken", "quantity": 1},
      {"name": "rice", "quantity": 1}
    ]
  }'
```

### Step 9: Publish Agent
1. Once testing is complete, click **"Publish"** or **"Deploy"**
2. Get the agent URL/link
3. Share link will be in format: `https://dialogflow.cloud.google.com/cx/...`

### Step 10: Update Implementation Log
Add agent URL to `docs/demo/implementation-log.md`:
```
- Agent URL: [your-agent-url]
```

## Alternative: Using gcloud CLI (Advanced)

If you prefer CLI configuration, you can use:

```bash
# Create agent
gcloud alpha agent-builder agents create \
  --display-name="Virtual Dietitian MVP" \
  --location=us-central1

# This is more complex and requires Dialogflow CX configuration
# Recommend using the UI for faster setup
```

## Next Steps After Setup
1. Test with all 5 test cases from PRD
2. Record demo video (2-3 minutes)
3. Document architecture and design decisions
4. Complete Session 5 tasks
