# Data Directory

This directory contains master reference data for the Virtual Dietitian project.

## Files

### nutrition_db.json (Master Copy)
The authoritative source for the 47-food nutrition database. This is a reference copy maintained for version control and documentation.

**Active Copy:** The Cloud Function uses a working copy at `cloud-functions/nutrition-analyzer/nutrition_db.json` which is bundled with the function deployment.

**Keeping in Sync:** When updating nutrition data:
1. Edit this master copy first
2. Copy changes to `cloud-functions/nutrition-analyzer/nutrition_db.json`
3. Redeploy Cloud Function if needed

**Contents:**
- 47 common foods across 6 categories
- Complete nutritional data (9 nutrients per food)
- Food aliases for flexible matching
- USDA-based values

## Why Two Copies?

- **This copy (`data/`)**: Master reference, version controlled, documented
- **Cloud Function copy**: Required for function deployment (bundled with code)

The Cloud Function is deployed from its directory, so it needs a local copy of the database file.
