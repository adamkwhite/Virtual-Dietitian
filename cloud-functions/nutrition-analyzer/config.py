"""
Configuration management for nutrition analyzer.
Handles local development vs cloud deployment settings.
"""

import os

from dotenv import load_dotenv

# Load .env file if it exists (for local development)
load_dotenv()


class Config:
    """Configuration class for environment-specific settings."""

    # Environment: 'local' or 'cloud'
    ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

    # Nutrition database path
    # Default points to local copy (used in deployment)
    # Master copy maintained at ../../data/nutrition_db.json for reference
    NUTRITION_DB_PATH = os.getenv("NUTRITION_DB_PATH", "./nutrition_db.json")

    @classmethod
    def is_cloud(cls):
        """Check if running in cloud environment."""
        return cls.ENVIRONMENT == "cloud"

    @classmethod
    def is_local(cls):
        """Check if running in local development."""
        return cls.ENVIRONMENT == "local"
