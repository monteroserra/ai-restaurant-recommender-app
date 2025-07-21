# config.py
"""
Configuration file for the AI Restaurant Recommender App
"""

# Google Maps API Key - Get yours from: https://console.cloud.google.com/
GOOGLE_MAP_API_KEY = "AIzaSyCRwDRASI5kMkmmZ07Gbzf1y5k_ED6jBZM"

# Default coordinates (optional - these are now set in the UI)
# You can change these to your preferred default location
latitude = 41.38  # New York City latitude
longitude = 2.17  # New York City longitude

# API Configuration
DEFAULT_RADIUS = 1000  # meters
DEFAULT_MIN_REVIEWS = 100
DEFAULT_MAX_RESULTS = 5

# You can add more configuration options here as needed
# For example:
# - Different default locations for different users
# - API rate limiting settings
# - Logging configuration
# - etc.

