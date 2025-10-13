# Google Cloud Agent Builder Setup Guide

**Last Updated:** October 12, 2025
**Target Time:** 45-60 minutes
**Prerequisites:** GCP project with billing enabled, nutrition_db.json prepared, Cloud Function deployed

---

## Overview

This guide walks through setting up a Vertex AI Conversational Agent with OpenAPI tool integration. It covers the complete configuration process including data stores, tools, and playbooks.

**Key Learnings:**
- Agent Builder and Vertex AI Studio are separate interfaces with separate configurations
- System instructions are configured in Playbooks, not in a single global prompt field
- Tools are configured via OpenAPI specifications (not simple webhook URLs)
- The UI can be confusing - this guide provides the exact navigation paths

---

## Part 1: Initial Agent Setup (15 min)

### 1.1 Navigate to Agent Builder

```
https://console.cloud.google.com/gen-app-builder/apps
```

Or: Navigation menu (☰) → Vertex AI → Agent Builder → Apps

### 1.2 Create New Agent

1. Click **"Create App"** or **"New Agent"**
2. **App Type:** Choose "Agent" (conversational agent)
3. **Agent Name:** `Virtual Dietitian`
4. **Company Name:** Enter your company name (appears in default responses)
5. **Region:** `global` (recommended) or specific region
6. **Language:** English (en)
7. Click **"Continue"**

### 1.3 Configure Data Store (Optional but Required by Setup Wizard)

**Note:** For webhook-based architectures, the data store is optional. However, the setup wizard requires it.

#### Option A: Cloud Storage (Recommended for Static Data)

1. **Data Source Type:** Select **"Cloud Storage"**
2. **Data Type:** Select **"Structured data"**
3. **File Type:**
   - For JSON: Select "Unstructured data with metadata"
   - For CSV: Select "CSV (for FAQ data)"

4. **Upload Data First:**
   ```bash
   # Create bucket if needed
   gcloud storage buckets create gs://your-project-nutrition-data --location=us-central1

   # Upload nutrition database
   gcloud storage cp data/nutrition_db.json gs://your-project-nutrition-data/nutrition_db.json
   ```

5. **Select Storage Location:**
   - Click on your bucket (e.g., `run-sources-virtualdietitian-us-central1`)
   - Click the **"File"** tab
   - Enter path: `gs://your-bucket-name/nutrition_db.json`
   - Click **"Continue"**

#### Option B: Skip Data Store (Use API Option)

1. Select **"API"**
2. Skip the import step
3. You can add data later if needed

### 1.4 Complete Initial Setup

1. Review settings
2. Click **"Create"**
3. Wait for agent provisioning (30-60 seconds)

---

## Part 2: Configure OpenAPI Tool (20 min)

### 2.1 Navigate to Tools Section

In the left sidebar under **BUILD**, click **"Tools"**

### 2.2 Create New Tool

1. Click **"+ Create Tool"** or **"Add Tool"**
2. **Tool Name:** `nutrition-analyzer`
3. **Type:** Select **"OpenAPI"**
4. **Description:**
   ```
   Analyzes meal descriptions and returns nutritional information including calories, protein, carbs, fats, and health insights
   ```

### 2.3 Get Cloud Function URL

```bash
# Get the deployed Cloud Function URL
gcloud functions describe nutrition-analyzer \
  --region=us-central1 \
  --format="value(serviceConfig.uri)"
```

Example output: `https://nutrition-analyzer-epp4v6loga-uc.a.run.app`

### 2.4 Create OpenAPI Schema

Paste the following YAML in the **Schema** field:

```yaml
openapi: 3.0.0
info:
  title: Nutrition Analyzer
  version: 1.0.0
  description: Analyzes nutritional content of meals
servers:
  - url: https://YOUR-FUNCTION-URL-HERE.run.app
paths:
  /:
    post:
      operationId: analyzeNutrition
      summary: Analyze nutritional content of a meal description
      description: Takes a meal description and returns detailed nutritional information
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                meal_description:
                  type: string
                  description: Description of the meal
              required:
                - meal_description
      responses:
        '200':
          description: Successful nutritional analysis
          content:
            application/json:
              schema:
                type: object
                properties:
                  nutritional_data:
                    type: object
                  insights:
                    type: array
                    items:
                      type: string
```

**Important:** Replace `YOUR-FUNCTION-URL-HERE.run.app` with your actual Cloud Function URL

### 2.5 Configure Authentication

1. **Authentication Type:** Select **"Service agent token"**
2. **Service Agent Auth Type:** Select **"ID token"**
3. Leave **Custom TLS certificate authorities** empty (unless using private CA)
4. Leave **Service Directory** unconfigured (unless using VPC)

### 2.6 Additional Settings

- **Ignore unknown fields:** Check this box (recommended for flexibility)
- **Hide unspecified tool output fields:** Optional, leave unchecked for MVP

### 2.7 Save Tool

1. Click **"Create"** or **"Save"**
2. Verify tool appears in the Tools list

---

## Part 3: Configure Playbook (System Instructions) (15 min)

### 3.1 Navigate to Agent Settings

**Navigation Path:**
1. Click **"Agent Overview"** in left sidebar (first item under BUILD)
2. Look for the **gear icon (⚙️)** in the top toolbar and click it
3. Scroll to **"Conversation start"** section

**Alternative Path:**
1. In left sidebar, find the menu icon (☰) next to your agent name at top
2. Select **"Agent settings"** or **"Configuration"**

### 3.2 Choose Conversation Start Method

Under **"Conversation start"**, you'll see two options:

1. **Playbook** - Use generative AI (select this)
2. **Flow** - Set up pre-defined pages and rules

Click **"Playbook"**

### 3.3 Create Playbook

1. **Type Selection:** Choose **"Routine"**
   - Routine: Manages main conversation (choose this)
   - Task: Returns to caller when complete (not needed for MVP)

2. **Playbook Name:**
   ```
   Virtual Dietitian Main
   ```

3. **Goal:**
   ```
   Help users log meals and provide nutritional feedback with actionable health insights
   ```

4. **Instructions:**
   ```
   - When the user describes a meal or food they ate, use ${TOOL: nutrition-analyzer} to analyze the nutritional content
   - Pass the complete meal description to the nutrition-analyzer tool
   - Present the nutritional results in a friendly, conversational way
   - Highlight positive aspects of their meal choices
   - Provide specific, actionable suggestions for improvement when appropriate
   - Be encouraging and supportive in your responses
   - If the user asks general nutrition questions, answer based on your knowledge without calling the tool
   ```

5. **Available Tools:**
   - Check the box next to **"nutrition-analyzer"**
   - Do NOT connect the data store (unless you want RAG-based lookups in addition to tool calls)

6. **Session Parameters:** Leave empty for MVP (no session state needed)

7. **Conditional Actions:** Leave empty for MVP

8. **Python Code:** Leave empty for MVP

### 3.4 Save Playbook

1. Click **"Save"** or **"Create"**
2. Verify playbook appears in the Playbooks list

### 3.5 Set as Default Conversation Start

**Note:** The Agent Settings interface may not persist the Playbook selection properly. Use this method instead:

1. Go to **"Flows"** in the left sidebar
2. Click on **"Default Start Flow"**
3. Click on the **"Start Page"** node
4. In the Start Page configuration panel, look for **"Routes"** section
5. Click on **"Default Welcome Intent"**
6. In the route configuration, find the **"Fulfillment"** section
7. Set the fulfillment to call your playbook: **"Virtual Dietitian Main"**
8. Click **"Save"**
9. Verify the playbook is now connected to the Default Welcome Intent

---

## Part 4: Testing (10 min)

### 4.1 Access Test Interface

**In Agent Builder Console:**
1. Click **"Test Cases"** in left sidebar under TEST & EVALUATE
2. Or click the **Preview** button in the flow editor

**Test Dialog Interface:**
- Shows flow execution steps
- Displays which tools were called
- Shows input/output parameters

### 4.2 Test Meal Logging

Try these test cases:

**Test 1: Simple Meal**
```
I had oatmeal with blueberries and almond butter for breakfast
```

Expected behavior:
- Agent calls `nutrition-analyzer` tool
- Returns nutritional breakdown
- Provides insights and recommendations

**Test 2: Short Input**
```
oatmeal
```

Expected behavior:
- Agent calls `nutrition-analyzer` tool
- Returns nutritional data for oatmeal

**Test 3: General Question**
```
What are good sources of protein?
```

Expected behavior:
- Agent answers without calling tool (general knowledge)

### 4.3 Debugging Failed Tests

**Issue: Agent says "I'm sorry, as an AI Assistant at [Company Name]..."**
- **Cause:** Playbook not set as default conversation start
- **Fix:** Go to Agent Settings → Conversation start → Select Playbook

**Issue: Tool not being called**
- **Cause:** Instructions don't explicitly reference the tool
- **Fix:** Verify playbook instructions include `${TOOL: nutrition-analyzer}`

**Issue: "data_store_no_match" tool is called instead**
- **Cause:** Data store is connected and taking precedence
- **Fix:** In playbook configuration, uncheck the data store tool

**Issue: Authentication error calling Cloud Function**
- **Cause:** Cloud Function doesn't allow service agent
- **Fix:** Grant IAM permission:
  ```bash
  PROJECT_ID=$(gcloud config get-value project)
  SERVICE_AGENT="${PROJECT_ID}@gcp-sa-dialogflow.iam.gserviceaccount.com"

  gcloud functions add-iam-policy-binding nutrition-analyzer \
    --region=us-central1 \
    --member="serviceAccount:${SERVICE_AGENT}" \
    --role="roles/cloudfunctions.invoker"
  ```

**Issue: OpenAPI schema validation error**
- **Cause:** YAML formatting issue (line breaks in strings)
- **Fix:** Ensure all multi-line strings are on single lines or properly escaped

---

## Part 5: Deploy to Production (5 min)

### 5.1 Create Environment

1. In left sidebar under **DEPLOY**, click **"Environments"**
2. Click **"Create Environment"**
3. **Environment Name:** `production` or `demo`
4. **Display Name:** `Production` or `Demo`
5. Click **"Create"**

### 5.2 Deploy Agent Version

1. Go to **"Versions"** in left sidebar
2. Click **"Create Version"**
3. **Version Name:** `v1.0-mvp`
4. **Description:** `Initial MVP with nutrition analyzer tool`
5. Click **"Create"**
6. Wait for version to be created
7. Click **"Deploy to environment"**
8. Select your environment
9. Click **"Deploy"**

### 5.3 Get Agent URL

1. Go to **"Integrations"** in left sidebar
2. Click **"Dialogflow Messenger"** or **"Web Chat"**
3. Copy the embed code or agent URL
4. Share this URL for demo purposes

---

## Part 6: Accessing Different Interfaces

### Agent Builder Console (Configuration)
```
https://console.cloud.google.com/gen-app-builder/apps
```
**Use for:**
- Creating agents
- Configuring tools and data stores
- Setting up playbooks
- Managing flows
- Deploying versions

### Vertex AI Studio (Testing/API)
```
https://console.cloud.google.com/vertex-ai/studio
```
**Use for:**
- Quick testing with conversational UI
- Viewing API integration code
- Getting API keys
- Testing different models

**Important:** Changes in Vertex AI Studio do NOT sync to Agent Builder. You must configure the agent in Agent Builder.

### API Access
```bash
# Get API key
gcloud auth print-access-token

# Or create service account key
gcloud iam service-accounts keys create key.json \
  --iam-account=your-service-account@project.iam.gserviceaccount.com
```

---

## Troubleshooting Guide

### Can't Find System Instructions

**The system instructions are NOT in a single global field.** They're in the Playbook configuration.

**Path:** Agent Overview → Settings (⚙️) → Conversation start → Playbook → Instructions field

### OpenAPI Tool Not Working

**Checklist:**
- [ ] Cloud Function URL is correct in OpenAPI schema
- [ ] Authentication is set to "Service agent token" with "ID token"
- [ ] Service agent has `cloudfunctions.invoker` permission
- [ ] OpenAPI schema is valid YAML (no formatting errors)
- [ ] Tool is checked in Playbook "Available tools"

### Agent Using Wrong Identity

**Issue:** Agent says it's from a different company or has wrong persona

**Fix:** Update the Playbook instructions to define the agent's identity explicitly:
```
You are a Virtual Dietitian AI assistant that helps users log meals and provides nutritional feedback.
```

### Data Store vs Tool Confusion

**Data Store (Vertex AI Search):**
- Static reference data
- RAG-based retrieval
- Good for: FAQs, documentation, knowledge base

**Tool (OpenAPI/Cloud Function):**
- Dynamic function execution
- Business logic processing
- Good for: Calculations, rules, external API calls

**For nutrition analysis, use TOOL not DATA STORE** (Cloud Function has the rule engine logic)

---

## Quick Reference: Navigation Paths

| Task | Path |
|------|------|
| Create agent | `gen-app-builder/apps` → Create App |
| Configure tools | Agent Builder → Tools → Create Tool |
| Set system instructions | Agent Overview → ⚙️ → Conversation start → Playbook |
| Test agent | Agent Builder → Test Cases → Enter message |
| Deploy agent | Agent Builder → Versions → Create → Deploy |
| View API code | Vertex AI Studio → Code button |
| Configure data store | Agent Builder → Start Page → Data stores |

---

## Next Steps

After completing this setup:

1. **Test thoroughly** with various meal descriptions
2. **Record demo video** showing the agent in action
3. **Document architecture** (see `architecture.md`)
4. **Monitor usage** in Cloud Logging
5. **Iterate on playbook instructions** based on test results

---

## Additional Resources

- [Agent Builder Documentation](https://cloud.google.com/agent-builder/docs)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Cloud Functions IAM](https://cloud.google.com/functions/docs/securing/managing-access-iam)
- [Vertex AI Agent Builder Best Practices](https://cloud.google.com/agent-builder/docs/best-practices)

---

**Document Version:** 1.0
**Last Tested:** October 12, 2025
**Tested By:** Adam White
