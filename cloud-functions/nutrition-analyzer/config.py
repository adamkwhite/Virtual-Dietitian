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
    NUTRITION_DB_PATH = os.getenv("NUTRITION_DB_PATH", "../../data/nutrition_db.json")

    @classmethod
    def is_cloud(cls):
        """Check if running in cloud environment."""
        return cls.ENVIRONMENT == "cloud"

    @classmethod
    def is_local(cls):
        """Check if running in local development."""
        return cls.ENVIRONMENT == "local"
