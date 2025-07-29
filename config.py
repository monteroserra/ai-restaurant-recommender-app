# config.py
"""
Configuration file for the AI Restaurant Recommender App
"""

# Configuration file for Restaurant Recommender App
import os
from typing import Dict, Any

# API Keys
GOOGLE_MAPS_API_KEY = "AIzaSyCRwDRASI5kMkmmZ07Gbzf1y5k_ED6jBZM"
GEMINI_API_KEY = "AIzaSyCx2fzv7x4HQbDhRzoCdgxikKXX8AVfWPk"

# API Endpoints
GOOGLE_PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place"
GOOGLE_GEOCODING_BASE_URL = "https://maps.googleapis.com/maps/api/geocode"
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Default search parameters
DEFAULT_RADIUS = 1000  # meters
DEFAULT_MIN_REVIEWS = 100
DEFAULT_MAX_RESULTS = 5

# Review and analysis settings
DEFAULT_REVIEW_COUNT = 200
MAX_REVIEW_COUNT = 500
REVIEW_CACHE_DURATION = 3600  # 1 hour in seconds
ANALYSIS_CACHE_DURATION = 86400  # 24 hours in seconds

# Analysis settings
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30

# Cache settings
CACHE_DIR = "cache"
REVIEW_CACHE_FILE = "reviews_cache.json"
ANALYSIS_CACHE_FILE = "analysis_cache.json"

# UI Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
DETAIL_WINDOW_WIDTH = 900
DETAIL_WINDOW_HEIGHT = 700

# Web app settings
WEB_HOST = "127.0.0.1"
WEB_PORT = 5000
WEB_DEBUG = True

# Gemini Analysis Prompt Template
GEMINI_ANALYSIS_PROMPT = """
Analyze the following restaurant reviews and provide a structured analysis in JSON format.

Reviews to analyze:
{reviews_text}

Please provide the analysis in this exact JSON structure:
{{
    "cuisine_type": "Primary cuisine type and style",
    "ambience": "Description of the restaurant's atmosphere and setting",
    "highlights": [
        "Top positive aspect 1",
        "Top positive aspect 2", 
        "Top positive aspect 3",
        "Top positive aspect 4",
        "Top positive aspect 5"
    ],
    "complaints": [
        "Main complaint 1",
        "Main complaint 2",
        "Main complaint 3",
        "Main complaint 4"
    ],
    "overall_sentiment": "Brief overall sentiment summary",
    "price_range": "Estimated price range based on reviews",
    "best_dishes": [
        "Most mentioned dish 1",
        "Most mentioned dish 2",
        "Most mentioned dish 3"
    ],
    "service_quality": "Summary of service quality mentions"
}}

Focus on the most frequently mentioned aspects. Be concise but informative. Extract only factual information from the reviews.
"""

def validate_config() -> Dict[str, Any]:
    """Validate configuration settings and return status."""
    import sys
    current_module = sys.modules[__name__]
    
    issues = []
    
    google_key = getattr(current_module, 'GOOGLE_MAPS_API_KEY', 'YOUR_GOOGLE_MAPS_API_KEY_HERE')
    if google_key == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
        issues.append("Google Maps API key not configured")
    
    gemini_key = getattr(current_module, 'GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY_HERE')
    if gemini_key == "YOUR_GEMINI_API_KEY_HERE":
        issues.append("Gemini API key not configured")
    
    cache_dir = getattr(current_module, 'CACHE_DIR', 'cache')
    if not os.path.exists(cache_dir):
        try:
            os.makedirs(cache_dir)
        except Exception as e:
            issues.append(f"Cannot create cache directory: {e}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }

# Environment variable overrides
_env_google_key = os.getenv("GOOGLE_MAPS_API_KEY")
if _env_google_key:
    GOOGLE_MAPS_API_KEY = _env_google_key

_env_gemini_key = os.getenv("GEMINI_API_KEY")
if _env_gemini_key:
    GEMINI_API_KEY = _env_gemini_key