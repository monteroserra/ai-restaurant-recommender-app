"""
Configuration file for the AI-powered restaurant recommender app
Contains API keys and application settings
"""

# =============================================================================
# API KEYS - REPLACE WITH YOUR ACTUAL KEYS
# =============================================================================

# Google Maps API Key
# Required APIs: Places API, Distance Matrix API, Geocoding API
# Get from: https://console.cloud.google.com/
GOOGLE_MAP_API_KEY = "AIzaSyCRwDRASI5kMkmmZ07Gbzf1y5k_ED6jBZM"

# Gemini AI API Key (NEW)
# Required for AI-powered review analysis
# Get from: https://aistudio.google.com/
GEMINI_API_KEY = "AIzaSyCx2fzv7x4HQbDhRzoCdgxikKXX8AVfWPk"

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# Default search parameters
DEFAULT_RADIUS = 1000  # meters
DEFAULT_MIN_REVIEWS = 100
DEFAULT_MAX_RESULTS = 5

# Default coordinates (New York City)
# Change these to your preferred default location
DEFAULT_LATITUDE = 40.7128
DEFAULT_LONGITUDE = -74.0060

# =============================================================================
# AI ANALYSIS SETTINGS (NEW)
# =============================================================================

# Enable/disable AI features
GEMINI_ENABLED = True  # Set to False to disable AI analysis

# AI analysis parameters
MAX_REVIEWS_FOR_ANALYSIS = 30  # Maximum reviews to analyze per restaurant
GEMINI_RATE_LIMIT = 1.0  # Minimum seconds between Gemini API calls
AI_ANALYSIS_TIMEOUT = 30  # Seconds to wait for AI analysis

# Only analyze restaurants with minimum reviews to ensure quality insights
MIN_REVIEWS_FOR_AI_ANALYSIS = 10

# Maximum restaurants to analyze with AI (to save API quotas)
MAX_RESTAURANTS_FOR_AI_ANALYSIS = 3

# =============================================================================
# UI SETTINGS
# =============================================================================

# Window settings
WINDOW_TITLE = "AI-Powered Restaurant Recommender"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700

# Color scheme
PRIMARY_COLOR = "#2c3e50"
SECONDARY_COLOR = "#3498db"
SUCCESS_COLOR = "#27ae60"
WARNING_COLOR = "#f39c12"
ERROR_COLOR = "#e74c3c"
BACKGROUND_COLOR = "#ecf0f1"

# =============================================================================
# API RATE LIMITING
# =============================================================================

# Google Maps API rate limiting
GOOGLE_API_RATE_LIMIT = 0.1  # Seconds between calls
GOOGLE_API_TIMEOUT = 10  # Request timeout in seconds

# =============================================================================
# SEARCH CONSTRAINTS
# =============================================================================

# Search radius limits (meters)
MIN_SEARCH_RADIUS = 100
MAX_SEARCH_RADIUS = 5000

# Review count limits
MIN_REVIEW_COUNT = 10
MAX_REVIEW_COUNT = 1000

# Result limits
MIN_RESULTS = 1
MAX_RESULTS = 20

# =============================================================================
# ERROR HANDLING
# =============================================================================

# Retry settings
MAX_API_RETRIES = 3
RETRY_DELAY = 1.0  # Seconds

# Timeout settings
DEFAULT_TIMEOUT = 10  # Seconds

# =============================================================================
# FEATURE FLAGS
# =============================================================================

# Feature toggles for easy enabling/disabling
ENABLE_DISTANCE_CALCULATION = True
ENABLE_AI_ANALYSIS = True  # Master switch for all AI features
ENABLE_REVIEW_SENTIMENT = True
ENABLE_PRICE_ANALYSIS = True
ENABLE_CUISINE_DETECTION = False  # Future feature

# Debug settings
DEBUG_MODE = False
VERBOSE_LOGGING = True

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_config():
    """
    Validate configuration settings
    """
    errors = []
    
    # Check API keys
    if GOOGLE_MAP_API_KEY == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
        errors.append("Google Maps API key not configured")
    
    if GEMINI_ENABLED and GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        errors.append("Gemini API key not configured but AI features are enabled")
    
    # Check ranges
    if not (MIN_SEARCH_RADIUS <= DEFAULT_RADIUS <= MAX_SEARCH_RADIUS):
        errors.append(f"DEFAULT_RADIUS must be between {MIN_SEARCH_RADIUS} and {MAX_SEARCH_RADIUS}")
    
    if not (MIN_RESULTS <= DEFAULT_MAX_RESULTS <= MAX_RESULTS):
        errors.append(f"DEFAULT_MAX_RESULTS must be between {MIN_RESULTS} and {MAX_RESULTS}")
    
    return errors

def print_config_status():
    """
    Print current configuration status
    """
    print("🔧 Configuration Status:")
    print(f"   Google Maps API: {'✅ Configured' if GOOGLE_MAP_API_KEY != 'YOUR_GOOGLE_MAPS_API_KEY_HERE' else '❌ Not configured'}")
    print(f"   Gemini AI API: {'✅ Configured' if GEMINI_API_KEY != 'YOUR_GEMINI_API_KEY_HERE' else '❌ Not configured'}")
    print(f"   AI Features: {'✅ Enabled' if GEMINI_ENABLED else '❌ Disabled'}")
    print(f"   Default Location: {DEFAULT_LATITUDE}, {DEFAULT_LONGITUDE}")
    print(f"   Default Radius: {DEFAULT_RADIUS}m")
    
    errors = validate_config()
    if errors:
        print("\n⚠️ Configuration Issues:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("\n✅ Configuration is valid!")

# =============================================================================
# QUICK SETUP GUIDE
# =============================================================================

"""
QUICK SETUP GUIDE:

1. Google Maps API Setup:
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing
   - Enable: Places API, Distance Matrix API, Geocoding API
   - Create an API key and replace GOOGLE_MAP_API_KEY above

2. Gemini AI Setup:
   - Go to https://aistudio.google.com/
   - Create an API key
   - Replace GEMINI_API_KEY above

3. Install Dependencies:
   pip install requests google-generativeai

4. Test Configuration:
   python config.py

5. Run the App:
   python main.py
"""

if __name__ == "__main__":
    print_config_status()
