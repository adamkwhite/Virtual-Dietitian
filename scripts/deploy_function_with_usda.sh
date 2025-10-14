#!/bin/bash
# Deploy nutrition-analyzer Cloud Function with USDA API support
# Usage: ./scripts/deploy_function_with_usda.sh <YOUR_USDA_API_KEY>

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if API key provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: USDA API key required${NC}"
    echo "Usage: $0 <YOUR_USDA_API_KEY>"
    echo ""
    echo "Get your API key at: https://fdc.nal.usda.gov/api-key-signup.html"
    exit 1
fi

USDA_API_KEY=$1

echo -e "${GREEN}=== Virtual Dietitian - USDA API Deployment ===${NC}"
echo "API Key: ${USDA_API_KEY:0:10}..."
echo ""

# Navigate to function directory
cd "$(dirname "$0")/../cloud-functions/nutrition-analyzer"

echo -e "${YELLOW}Step 1: Deploying Cloud Function with USDA API enabled...${NC}"
gcloud functions deploy nutrition-analyzer \
  --gen2 \
  --runtime=python312 \
  --region=us-central1 \
  --source=. \
  --entry-point=analyze_nutrition \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars="ENABLE_USDA_API=true,USDA_API_KEY=${USDA_API_KEY},ENVIRONMENT=cloud,LOG_EXECUTION_ID=true,NUTRITION_DB_PATH=./nutrition_db.json" \
  --timeout=60s \
  --memory=256MB

echo ""
echo -e "${GREEN}=== Deployment Complete! ===${NC}"
echo ""
echo "Function URL: https://nutrition-analyzer-epp4v6loga-uc.a.run.app"
echo ""
echo -e "${YELLOW}Environment Variables Set:${NC}"
echo "  ✓ ENABLE_USDA_API=true"
echo "  ✓ USDA_API_KEY=${USDA_API_KEY:0:10}..."
echo "  ✓ ENVIRONMENT=cloud"
echo ""
echo -e "${YELLOW}Testing the function:${NC}"
echo ""
echo "Test with static DB food (fast):"
echo "curl -X POST https://nutrition-analyzer-epp4v6loga-uc.a.run.app \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"food_items\":[{\"name\":\"chicken\",\"quantity\":1}]}'"
echo ""
echo "Test with new food (USDA API):"
echo "curl -X POST https://nutrition-analyzer-epp4v6loga-uc.a.run.app \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"food_items\":[{\"name\":\"pizza\",\"quantity\":1}]}'"
echo ""
echo -e "${GREEN}Ready to analyze 500,000+ foods!${NC}"
