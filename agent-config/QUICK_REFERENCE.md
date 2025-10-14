# Agent Builder Quick Reference

## 📋 Configuration Checklist

### ✅ Files You Need
- [ ] `agent-instructions.txt` - Copy/paste into Agent Instructions
- [ ] `training-phrases.txt` - Add to log_meal intent
- [ ] `webhook-config.json` - Reference for webhook setup
- [ ] `test-cases.md` - Use for testing

### ✅ GCP Console Steps

1. **Create Agent** (5 min)
   - Go to: https://console.cloud.google.com/gen-app-builder/engines
   - Name: Virtual Dietitian MVP
   - Type: Chat
   - Region: us-central1

2. **Add Instructions** (2 min)
   - Copy all text from `agent-instructions.txt`
   - Paste into "Agent Instructions" or "System Instructions"

3. **Create Webhook** (3 min)
   - Name: nutrition-analyzer
   - URL: `https://nutrition-analyzer-epp4v6loga-uc.a.run.app`
   - Method: POST
   - Auth: None

4. **Create Intent** (5 min)
   - Intent name: log_meal
   - Add training phrases from `training-phrases.txt`
   - Enable webhook fulfillment
   - Link to nutrition-analyzer webhook

5. **Test** (10 min)
   - Open agent simulator
   - Test each case from `test-cases.md`
   - Verify all insights appear correctly

6. **Publish** (2 min)
   - Click Publish/Deploy
   - Copy shareable link
   - Add to implementation log

## 🔗 Important URLs

**GCP Console:**
- Agent Builder: https://console.cloud.google.com/gen-app-builder
- Cloud Functions: https://console.cloud.google.com/functions

**Your Services:**
- Cloud Function: https://nutrition-analyzer-epp4v6loga-uc.a.run.app
- Project: virtualdietitian (us-central1)

## 🧪 Quick Test

Paste this into agent chat to test:
```
I had oatmeal with blueberries and almond butter for breakfast
```

Expected: Should show 332 cal, 11% protein, vitamin C benefit, fiber benefit, protein recommendation

## 🐛 Troubleshooting

**Webhook not calling?**
- Check URL is correct
- Verify intent has webhook enabled
- Test webhook directly with curl

**Wrong food extraction?**
- Add more training phrases
- Check agent instructions are loaded
- Verify parameter mapping

**Response formatting off?**
- Review agent instructions template
- Check all webhook fields are used
- Test webhook response directly

## 📝 After Setup

Update `docs/demo/implementation-log.md` with:
- Agent URL
- Screenshots of successful tests
- Any issues encountered
