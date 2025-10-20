"""
Configuration for Pokemon TCG Database Sync
"""
import os

# API Configuration
API_KEY = '0af3890a-ef8f-4a46-8cb6-f5e111be72f1'
BASE_URL = 'https://api.pokemontcg.io/v2'

# Database Configuration
# For local development (SQLite)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///pokemon_tcg.db')

# For Railway/Production (PostgreSQL)
# DATABASE_URL = os.getenv('DATABASE_URL')  # Railway provides this automatically

# Sync Configuration
BATCH_SIZE = 100  # Reduced batch size for slow connections
RATE_LIMIT_DELAY = 0  # No delay between requests
MAX_RETRIES = 5  # More retries
RETRY_DELAY = 5  # Longer retry delay for slow VPN

# Features
INCLUDE_PRICING = True  # Include TCGPlayer and Cardmarket pricing
INCLUDE_IMAGES = True  # Store image URLs
INCLUDE_LEGALITIES = True  # Store format legalities

# Update Settings
UPDATE_EXISTING = False  # Update existing cards or skip them
UPDATE_PRICES_ONLY = False  # Only update pricing data

# Logging
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = 'logs/sync.log'
