# GCP Cloud Storage Deployment

**Deployed:** October 13, 2025
**Demo URL:** https://storage.googleapis.com/virtual-dietitian-demo/index.html

## Deployment Details

### Infrastructure
- **Platform:** Google Cloud Storage (Static Website Hosting)
- **Project:** virtualdietitian
- **Bucket:** virtual-dietitian-demo
- **Region:** us-central1
- **Access:** Public (allUsers:objectViewer)

### Components
- **Frontend:** Single HTML file with embedded Dialogflow Messenger
- **Backend:** Cloud Function (`nutrition-analyzer`)
- **Agent:** Vertex AI Agent Builder (agent-id: 70e21911-92e8-418f-9a11-aa98868ba1fe)

## Deployment Commands

### Initial Deployment
```bash
# 1. Create bucket
gsutil mb -p virtualdietitian gs://virtual-dietitian-demo

# 2. Upload HTML file
gsutil cp docs/demo/virtual-dietitian-demo.html gs://virtual-dietitian-demo/index.html

# 3. Make publicly accessible
gsutil iam ch allUsers:objectViewer gs://virtual-dietitian-demo

# 4. Set as website
gsutil web set -m index.html gs://virtual-dietitian-demo
```

### Update Demo
To update the demo page after making changes:

```bash
# From project root
gsutil cp docs/demo/virtual-dietitian-demo.html gs://virtual-dietitian-demo/index.html

# Verify
curl -I https://storage.googleapis.com/virtual-dietitian-demo/index.html
```

### Remove Deployment
```bash
# Delete all files in bucket
gsutil rm -r gs://virtual-dietitian-demo/*

# Delete bucket
gsutil rb gs://virtual-dietitian-demo
```

## Architecture

```
User Browser
    ↓
GCS Static Website (index.html)
    ↓
Dialogflow Messenger Widget
    ↓
Vertex AI Agent Builder
    ↓
Cloud Function (nutrition-analyzer)
    ↓
Nutrition Database (JSON in function)
    ↓
Rule Engine (business logic)
```

## URLs

- **Live Demo:** https://storage.googleapis.com/virtual-dietitian-demo/index.html
- **Cloud Function:** https://nutrition-analyzer-epp4v6loga-uc.a.run.app
- **GCP Console:** https://console.cloud.google.com/storage/browser/virtual-dietitian-demo?project=virtualdietitian

## Cost Analysis

### Monthly Cost Estimate (Low Traffic)
- **Cloud Storage:** ~$0.02/month (storage) + $0.12/GB (egress)
- **Cloud Function:** ~$0.40/month (1M invocations in free tier)
- **Dialogflow CX:** Included in free tier (up to 1,000 sessions/month)

**Total for MVP demo:** < $5/month for moderate traffic

### Scalability
- **Current limits:** None (public bucket)
- **Bandwidth:** Google Cloud CDN-backed
- **Global availability:** Yes
- **HTTPS:** Included by default

## Monitoring

### Check Deployment Status
```bash
# Test the demo page
curl https://storage.googleapis.com/virtual-dietitian-demo/index.html | grep "Virtual Dietitian"

# Check Cloud Function health
curl https://nutrition-analyzer-epp4v6loga-uc.a.run.app/health

# View bucket details
gsutil ls -L gs://virtual-dietitian-demo
```

### View Logs
```bash
# Cloud Function logs
gcloud functions logs read nutrition-analyzer --region=us-central1 --limit=50

# Storage access logs (requires configuration)
gsutil logging get gs://virtual-dietitian-demo
```

## Troubleshooting

### Issue: 403 Forbidden
**Cause:** Bucket or object not public
**Fix:**
```bash
gsutil iam ch allUsers:objectViewer gs://virtual-dietitian-demo
```

### Issue: 404 Not Found
**Cause:** File not uploaded correctly
**Fix:**
```bash
gsutil ls gs://virtual-dietitian-demo
gsutil cp docs/demo/virtual-dietitian-demo.html gs://virtual-dietitian-demo/index.html
```

### Issue: CORS Errors
**Cause:** Attempting to open `file://` directly instead of HTTP
**Fix:** Always access via `https://storage.googleapis.com/...` URL

### Issue: Agent Not Responding
**Cause:** Agent not published or webhook misconfigured
**Fix:**
1. Verify agent is published in Vertex AI Agent Builder
2. Test webhook directly: `curl -X POST https://nutrition-analyzer-epp4v6loga-uc.a.run.app -H "Content-Type: application/json" -d '{"food_items":[{"name":"chicken","quantity":1}]}'`
3. Check agent logs in GCP Console

## Security Considerations

### Current Setup (Public Demo)
- ✅ Public read access enabled
- ✅ HTTPS enforced by default
- ✅ No authentication required (demo purpose)
- ⚠️ Bucket writeable only by project members

### Production Recommendations
- [ ] Set up Cloud CDN for better performance
- [ ] Configure custom domain with SSL
- [ ] Enable Cloud Armor for DDoS protection
- [ ] Add rate limiting to Cloud Function
- [ ] Implement analytics (Google Analytics or Cloud Monitoring)
- [ ] Set up alerting for function errors

## Future Enhancements

### Custom Domain (Optional)
1. **Register domain** or use existing
2. **Create CNAME record:**
   ```
   demo.yourdomain.com → c.storage.googleapis.com
   ```
3. **Verify domain ownership** in GCP Console
4. **Update bucket for custom domain:**
   ```bash
   gsutil web set -m index.html -e 404.html gs://demo.yourdomain.com
   ```

### HTTPS with Custom Domain
- Use Cloud Load Balancer with managed SSL certificate
- Or use Firebase Hosting for automatic SSL

### CDN Configuration
```bash
# Enable Cloud CDN (requires Load Balancer)
gcloud compute backend-buckets create virtual-dietitian-backend \
    --gcs-bucket-name=virtual-dietitian-demo \
    --enable-cdn
```

## Related Documentation
- [Agent Builder Setup Guide](agent-builder-setup-guide.md)
- [Cloud Function Deployment](../cloud-functions/nutrition-analyzer/README.md)
- [Demo Script](../demo/demo-script.md)
- [Test Cases](../../agent-config/test-cases.md)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
