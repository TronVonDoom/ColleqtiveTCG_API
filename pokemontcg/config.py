"""
Configuration for Pokemon TCG Database Sync
"""
import os

# API Configuration
API_KEY = '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
BASE_URL = 'https://api.pokemontcg.io/v2'

# Database Configuration
# For local development (SQLite)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///pokemontcg/pokemontcg.db')

# For Railway/Production (PostgreSQL)
# DATABASE_URL = os.getenv('DATABASE_URL')  # Railway provides this automatically

# Sync Configuration
BATCH_SIZE = 50  # Reduced batch size for more reliable requests
RATE_LIMIT_DELAY = 0.5  # Small delay to avoid overwhelming API
MAX_RETRIES = 3  # Fewer retries with shorter timeout
RETRY_DELAY = 3  # Shorter retry delay
REQUEST_TIMEOUT = 30  # Shorter timeout (30 seconds instead of 180)

# Features
INCLUDE_PRICING = True  # Include TCGPlayer and Cardmarket pricing
INCLUDE_IMAGES = True  # Store image URLs
INCLUDE_LEGALITIES = True  # Store format legalities

# Update Settings
UPDATE_EXISTING = False  # Update existing cards or skip them
UPDATE_PRICES_ONLY = False  # Only update pricing data

# Logging
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = 'pokemontcg/logs/sync.log'
