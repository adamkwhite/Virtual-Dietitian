#!/bin/bash
# Setup script for Google Cloud Vision API image processing infrastructure
# Automates: API enablement, service account creation, Cloud Storage bucket setup

set -e  # Exit on error

PROJECT_ID="virtualdietitian"
SERVICE_ACCOUNT_NAME="vision-api-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
BUCKET_NAME="virtualdietitian-food-images"
REGION="us-central1"
KEY_FILE="$HOME/.gcp/virtualdietitian-vision-sa.json"

echo "========================================="
echo "Virtual Dietitian - Image Processing Setup"
echo "========================================="
echo ""
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Bucket: gs://$BUCKET_NAME"
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""

# Step 1: Enable Vision API
echo "[1/9] Enabling Vision API..."
gcloud services enable vision.googleapis.com --project=$PROJECT_ID
echo "✓ Vision API enabled"
echo ""

# Step 2: Create service account
echo "[2/9] Creating service account: $SERVICE_ACCOUNT_NAME..."
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL --project=$PROJECT_ID &>/dev/null; then
    echo "✓ Service account already exists"
else
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="Vision API Service Account" \
        --project=$PROJECT_ID
    echo "✓ Service account created"
fi
echo ""

# Step 3: Grant Vision API permissions
echo "[3/9] Granting Vision API permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/serviceusage.serviceUsageConsumer" \
    --quiet
echo "✓ Vision API permissions granted"
echo ""

# Step 4: Grant Cloud Storage permissions
echo "[4/9] Granting Cloud Storage permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/storage.objectAdmin" \
    --quiet
echo "✓ Cloud Storage permissions granted"
echo ""

# Step 5: Download service account key
echo "[5/9] Downloading service account key..."
mkdir -p "$(dirname $KEY_FILE)"
if [ -f "$KEY_FILE" ]; then
    echo "⚠ Key file already exists at $KEY_FILE"
    read -p "Overwrite? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✓ Skipping key download"
    else
        rm "$KEY_FILE"
        gcloud iam service-accounts keys create "$KEY_FILE" \
            --iam-account=$SERVICE_ACCOUNT_EMAIL \
            --project=$PROJECT_ID
        echo "✓ Service account key downloaded to $KEY_FILE"
    fi
else
    gcloud iam service-accounts keys create "$KEY_FILE" \
        --iam-account=$SERVICE_ACCOUNT_EMAIL \
        --project=$PROJECT_ID
    echo "✓ Service account key downloaded to $KEY_FILE"
fi
echo ""

# Step 6: Create Cloud Storage bucket
echo "[6/9] Creating Cloud Storage bucket: gs://$BUCKET_NAME..."
if gcloud storage buckets describe gs://$BUCKET_NAME &>/dev/null; then
    echo "✓ Bucket already exists"
else
    gcloud storage buckets create gs://$BUCKET_NAME \
        --location=$REGION \
        --project=$PROJECT_ID
    echo "✓ Bucket created"
fi
echo ""

# Step 7: Configure lifecycle policy (delete after 90 days)
echo "[7/9] Configuring bucket lifecycle policy..."
cat > /tmp/lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {
          "type": "Delete"
        },
        "condition": {
          "age": 90
        }
      }
    ]
  }
}
EOF
gcloud storage buckets update gs://$BUCKET_NAME --lifecycle-file=/tmp/lifecycle.json
rm /tmp/lifecycle.json
echo "✓ Lifecycle policy configured (delete after 90 days)"
echo ""

# Step 8: Set bucket to private
echo "[8/9] Setting bucket to private (enforcing public access prevention)..."
gcloud storage buckets update gs://$BUCKET_NAME --public-access-prevention
echo "✓ Public access prevention enforced"
echo ""

# Step 9: Enable CORS for demo webpage uploads
echo "[9/9] Enabling CORS for demo webpage uploads..."
cat > /tmp/cors.json << 'EOF'
[
  {
    "origin": ["*"],
    "method": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
    "maxAgeSeconds": 3600
  }
]
EOF
gcloud storage buckets update gs://$BUCKET_NAME --cors-file=/tmp/cors.json
rm /tmp/cors.json
echo "✓ CORS enabled"
echo ""

echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✓ Vision API enabled"
echo "  ✓ Service account: $SERVICE_ACCOUNT_EMAIL"
echo "  ✓ Service account key: $KEY_FILE"
echo "  ✓ Cloud Storage bucket: gs://$BUCKET_NAME"
echo "  ✓ Lifecycle policy: Delete after 90 days"
echo "  ✓ Public access: Prevented"
echo "  ✓ CORS: Enabled for demo webpage"
echo ""
echo "Next steps:"
echo "  1. Export service account key:"
echo "     export GOOGLE_APPLICATION_CREDENTIALS=$KEY_FILE"
echo "  2. Deploy image-food-analyzer Cloud Function"
echo "  3. Update demo webpage with upload UI"
echo ""
