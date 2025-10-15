# Virtual Dietitian - Observability Setup

**Date Enabled:** October 15, 2025
**Status:** Active
**Project:** virtualdietitian

---

## Enabled Features

All observability features are now **ENABLED** in Agent Builder:

### 1. ✅ Cloud Logging
**What:** Exports detailed logs to Google Cloud Logging
**Where to view:** https://console.cloud.google.com/logs/query?project=virtualdietitian

**Filter for Dialogflow CX logs:**
```
resource.type="dialogflow.googleapis.com/Agent"
```

**What you'll see:**
- User messages
- Agent responses
- Intent matches
- Webhook calls (nutrition-analyzer function)
- Parameter extractions
- Errors and warnings
- Performance metrics

**Use cases:**
- Debug why agent didn't understand a query
- See webhook request/response payloads
- Track errors in production
- Monitor response times

---

### 2. ✅ Conversation History
**What:** Browse and analyze actual user conversations
**Where to view:** Agent Builder → Test & Evaluate → Conversations

**What you'll see:**
- Session ID
- Start time
- Duration
- Number of turns
- Full conversation transcript
- Intent matches per turn
- Parameters extracted

**Features:**
- Filter by conversation ID, display name, or turn ID
- Export to CSV (max 50 conversations)
- Analyze conversation flows

**Use cases:**
- See what real users are asking
- Identify common conversation patterns
- Find where users get stuck
- Review test user sessions

---

### 3. ✅ Intent Suggestions
**What:** AI-powered suggestions to improve intents
**Where to view:** Agent Builder → Manage → Intents → [Intent] → Suggestions tab

**What you'll see:**
- Suggested training phrases based on real queries
- Recommendations to create new intents
- Queries that didn't match well

**Use cases:**
- Improve intent matching accuracy
- Discover new use cases from real usage
- Add training phrases you didn't think of
- Identify gaps in agent understanding

**How it works:**
- Analyzes conversation history
- Identifies patterns in unmatched/low-confidence queries
- Suggests improvements automatically

---

### 4. ✅ User Feedback
**What:** Thumbs up/down buttons on agent responses
**Where to view:** Agent Builder → Test & Evaluate → Conversations (feedback shown in transcripts)

**What users see:**
After each agent response:
```
👍 Was this helpful? 👎
```

**What you'll see:**
- Feedback ratings in conversation history
- Aggregate feedback metrics
- Which responses users liked/disliked

**Use cases:**
- Identify problematic responses
- Measure user satisfaction
- Prioritize which responses to improve
- A/B test different response styles

---

## Quick Access Links

| Feature | Direct Link |
|---------|-------------|
| Cloud Logging | https://console.cloud.google.com/logs/query?project=virtualdietitian |
| Conversation History | Agent Builder → Test & Evaluate → Conversations |
| Intent Suggestions | Agent Builder → Manage → Intents → [Select Intent] → Suggestions |
| Agent Settings | Agent Builder → Manage → Settings |

---

## Testing the Setup

### 1. Send a Test Conversation

**Go to demo page:**
https://storage.googleapis.com/virtual-dietitian-demo/index.html

**Send test messages:**
```
User: I had oatmeal with blueberries for breakfast
User: What about chicken and rice?
User: 👍 or 👎 (test feedback buttons)
```

### 2. Verify Cloud Logging (1-2 minutes delay)

**Go to:** https://console.cloud.google.com/logs/query?project=virtualdietitian

**Run query:**
```
resource.type="dialogflow.googleapis.com/Agent"
timestamp>="2025-10-15T00:00:00Z"
```

**Look for:**
- `DetectIntent` requests
- Webhook calls
- Response logs

### 3. Verify Conversation History (1-2 minutes delay)

**Go to:** Agent Builder → Test & Evaluate → Conversations

**Look for:**
- New session appears
- Conversation transcript visible
- Turn count shows correctly
- Feedback icons present

### 4. Check Intent Suggestions (24-48 hours delay)

**Go to:** Agent Builder → Manage → Intents → [log_meal or other intent] → Suggestions

**Note:** Suggestions appear after sufficient traffic (usually 24-48 hours)

---

## Data Retention

| Feature | Retention Period | Notes |
|---------|------------------|-------|
| Cloud Logging | 30 days (default) | Can extend to 365 days in Logs Router |
| Conversation History | 365 days (default) | Configured in Agent settings |
| Intent Suggestions | N/A | Generated from conversation history |
| User Feedback | Same as conversations | Stored with conversation data |

---

## Common Queries

### Find Errors
```
resource.type="dialogflow.googleapis.com/Agent"
severity>=ERROR
```

### Find Webhook Calls
```
resource.type="dialogflow.googleapis.com/Agent"
jsonPayload.webhookStatuses
```

### Find Specific User Query
```
resource.type="dialogflow.googleapis.com/Agent"
jsonPayload.queryResult.text:"oatmeal"
```

### Find Unknown Foods
```
resource.type="dialogflow.googleapis.com/Agent"
jsonPayload.webhookStatuses.errorMessage:"unknown"
```

---

## Monitoring Best Practices

### Daily Checks (During Testing Phase)
- [ ] Review conversation history for new sessions
- [ ] Check Cloud Logging for errors
- [ ] Look at user feedback ratings
- [ ] Note common food queries that fail

### Weekly Reviews
- [ ] Review intent suggestions
- [ ] Analyze conversation patterns
- [ ] Identify most common user questions
- [ ] Update training phrases based on real queries

### Monthly Analysis
- [ ] Export conversation data for trends
- [ ] Review overall feedback scores
- [ ] Identify top improvement opportunities
- [ ] Update documentation based on learnings

---

## Troubleshooting

### "No conversations appearing in history"

**Possible causes:**
1. Interaction logging not fully enabled (check Agent → Manage → Settings)
2. Conversations too recent (<2 minutes old)
3. Browser cache (hard refresh the page)

**Solution:**
- Wait 2-5 minutes after test conversation
- Check Cloud Logging first (shows up faster)
- Verify "Enable conversation history" is checked

### "No logs in Cloud Logging"

**Possible causes:**
1. Cloud Logging not enabled
2. Viewing wrong project
3. Time filter too narrow

**Solution:**
- Verify project is "virtualdietitian"
- Expand time range to "Last 1 hour"
- Check Logs Explorer permissions

### "No intent suggestions"

**Expected behavior:**
- Suggestions require 24-48 hours of traffic
- Needs multiple conversations with similar patterns
- Won't suggest if intent already covers query well

**Solution:**
- Wait for more traffic data
- Check back in 1-2 days
- Ensure conversation history is enabled (required for suggestions)

---

## Privacy & Security Notes

**Data Storage:**
- All data stored in Google Cloud (US region: us-central1)
- Google does not use conversation data for other purposes
- Conversations stored with redaction if configured

**PII Considerations:**
- Users might mention personal health info
- Consider adding parameter redaction for sensitive fields
- Review DLP (Data Loss Prevention) integration if needed

**Access Control:**
- Only project owners/editors can view conversations
- Use IAM roles to restrict access
- Audit logs track who viewed what

---

## Cost Implications

### Cloud Logging
- **Free tier:** 50 GB/month
- **Expected usage:** <1 GB/month for demo/testing
- **Cost if exceeded:** $0.50/GB

### Conversation History
- **Cost:** Free (included in Dialogflow CX)
- **Storage:** Part of agent configuration

### Intent Suggestions
- **Cost:** Free (included in Dialogflow CX)

### User Feedback
- **Cost:** Free (included in Dialogflow CX)

**Total expected cost:** $0/month (within free tier)

---

## Related Documentation

- [Dialogflow CX Conversation History](https://cloud.google.com/dialogflow/cx/docs/concept/conversation-history)
- [Cloud Logging Docs](https://cloud.google.com/logging/docs)
- [Agent Settings Guide](agent-config/SETUP_GUIDE_UPDATED.md)
- [Demo Page](docs/demo/demo-script.md)

---

**Last Updated:** October 15, 2025
**Updated By:** Session 9 - Observability setup
