#!/bin/bash
# Deploy nutrition-analyzer Cloud Function to GCP

set -e  # Exit on error

PROJECT_ID="virtualdietitian"
FUNCTION_NAME="nutrition-analyzer"
REGION="us-central1"
RUNTIME="python312"
ENTRY_POINT="analyze_nutrition"
SOURCE_DIR="cloud-functions/nutrition-analyzer"

echo "🚀 Deploying Cloud Function: $FUNCTION_NAME"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Runtime: $RUNTIME"
echo ""

# Deploy the function
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=$RUNTIME \
  --region=$REGION \
  --source=$SOURCE_DIR \
  --entry-point=$ENTRY_POINT \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=cloud,NUTRITION_DB_PATH=./nutrition_db.json \
  --memory=256MB \
  --timeout=60s

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Function URL:"
gcloud functions describe $FUNCTION_NAME --region=$REGION --gen2 --format="value(serviceConfig.uri)"
