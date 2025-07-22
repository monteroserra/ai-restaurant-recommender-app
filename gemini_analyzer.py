"""
Gemini AI-powered restaurant review analyzer
Integrates with existing restaurant recommender app
"""

import requests
import google.generativeai as genai
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

# Import configuration
try:
    from config import (
        GOOGLE_MAP_API_KEY, 
        GEMINI_API_KEY, 
        GEMINI_ENABLED,
        MAX_REVIEWS_FOR_ANALYSIS,
        GEMINI_RATE_LIMIT
    )
except ImportError:
    print("⚠️ Configuration not found - using defaults")
    GOOGLE_MAP_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY_HERE"
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
    GEMINI_ENABLED = True
    MAX_REVIEWS_FOR_ANALYSIS = 30
    GEMINI_RATE_LIMIT = 1.0

@dataclass
class ReviewSummary:
    """Structure for AI-generated review summary"""
    summary: str
    highlights: List[str]
    criticisms: List[str]
    overall_sentiment: str
    confidence_score: float

class RestaurantAnalyzer:
    """
    Analyzes restaurant reviews using Gemini AI
    """
    
    def __init__(self):
        self.enabled = self._initialize_analyzer()
        
    def _initialize_analyzer(self) -> bool:
        """Initialize the Gemini analyzer"""
        try:
            # Check if enabled and API key is configured
            if not GEMINI_ENABLED:
                print("ℹ️ Gemini analyzer disabled in configuration")
                return False
                
            if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
                print("⚠️ Gemini API key not configured")
                return False
            
            # Initialize Gemini
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Rate limiting
            self.last_call = 0
            self.min_interval = GEMINI_RATE_LIMIT
            
            print("✅ Gemini analyzer initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
            return False
    
    def is_enabled(self) -> bool:
        """Check if analyzer is enabled and ready"""
        return self.enabled
    
    def _rate_limit(self):
        """Apply rate limiting between API calls"""
        if not self.enabled:
            return
            
        current_time = time.time()
        time_since_last = current_time - self.last_call
        
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        
        self.last_call = time.time()
    
    def get_restaurant_reviews(self, place_id: str) -> List[Dict]:
        """Get reviews for a restaurant using Google Places API"""
        if not self.enabled or not place_id:
            return []
            
        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                'place_id': place_id,
                'fields': 'reviews',
                'key': GOOGLE_MAP_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'OK':
                reviews = data.get('result', {}).get('reviews', [])
                print(f"📝 Retrieved {len(reviews)} reviews")
                return reviews
            else:
                print(f"⚠️ Places API error: {data.get('status')}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching reviews: {e}")
            return []
    
    def analyze_reviews(self, reviews: List[Dict], restaurant_name: str) -> Optional[ReviewSummary]:
        """Analyze reviews using Gemini AI"""
        if not self.enabled or not reviews:
            return None
            
        try:
            self._rate_limit()
            
            # Prepare reviews for analysis
            review_texts = []
            for review in reviews[:MAX_REVIEWS_FOR_ANALYSIS]:
                rating = review.get('rating', 0)
                text = review.get('text', '').strip()
                if text and len(text) > 10:
                    review_texts.append(f"Rating: {rating}/5 - {text}")
            
            if len(review_texts) < 3:
                print(f"⚠️ Not enough quality reviews for {restaurant_name}")
                return None
            
            # Create analysis prompt
            prompt = f"""Analyze these customer reviews for "{restaurant_name}" and provide insights in JSON format.

Reviews ({len(review_texts)} total):
{chr(10).join(review_texts[:20])}

Respond with ONLY valid JSON in this exact format:
{{
    "summary": "Brief 2-sentence summary of customer experience",
    "highlights": ["Top 3 positive points"],
    "criticisms": ["Top 2 negative points or improvements needed"],
    "overall_sentiment": "positive/negative/mixed",
    "confidence_score": 0.85
}}

Be concise and focus on the most important insights."""
            
            print(f"🤖 Analyzing {len(review_texts)} reviews for {restaurant_name}...")
            
            # Generate analysis
            response = self.model.generate_content(prompt)
            
            if not response.text:
                print("❌ Empty response from Gemini")
                return None
            
            # Parse JSON response
            response_text = response.text.strip()
            
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON if response contains extra text
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    try:
                        data = json.loads(response_text[start:end])
                    except json.JSONDecodeError:
                        print(f"❌ Could not parse JSON from response")
                        return None
                else:
                    print(f"❌ No valid JSON found in response")
                    return None
            
            # Validate response structure
            required_fields = ['summary', 'highlights', 'criticisms', 'overall_sentiment', 'confidence_score']
            if not all(field in data for field in required_fields):
                print(f"❌ Missing required fields in response")
                return None
            
            # Create summary object
            summary = ReviewSummary(
                summary=data.get('summary', ''),
                highlights=data.get('highlights', [])[:3],
                criticisms=data.get('criticisms', [])[:2],
                overall_sentiment=data.get('overall_sentiment', 'unknown'),
                confidence_score=min(float(data.get('confidence_score', 0.5)), 1.0)
            )
            
            print(f"✅ Analysis completed for {restaurant_name} (confidence: {summary.confidence_score:.1%})")
            return summary
            
        except Exception as e:
            print(f"❌ Error in Gemini analysis for {restaurant_name}: {e}")
            return None
    
    def get_analysis_for_restaurant(self, place_id: str, restaurant_name: str) -> Optional[ReviewSummary]:
        """Complete workflow: Get reviews and analyze them"""
        if not self.enabled:
            return None
            
        print(f"🔍 Starting analysis for {restaurant_name}")
        
        # Get reviews
        reviews = self.get_restaurant_reviews(place_id)
        
        if not reviews:
            print(f"⚠️ No reviews found for {restaurant_name}")
            return None
        
        # Analyze reviews
        return self.analyze_reviews(reviews, restaurant_name)


# Convenience functions for easy integration
def analyze_restaurant(place_id: str, restaurant_name: str) -> Optional[Dict]:
    """
    Simple function to analyze a restaurant and return dict
    """
    analyzer = RestaurantAnalyzer()
    
    if not analyzer.is_enabled():
        return None
    
    summary = analyzer.get_analysis_for_restaurant(place_id, restaurant_name)
    
    if summary:
        return {
            'summary': summary.summary,
            'highlights': summary.highlights,
            'criticisms': summary.criticisms,
            'sentiment': summary.overall_sentiment,
            'confidence': summary.confidence_score
        }
    
    return None

def test_analyzer():
    """Test the analyzer"""
    print("🧪 Testing Gemini Restaurant Analyzer...")
    
    analyzer = RestaurantAnalyzer()
    
    if not analyzer.is_enabled():
        print("❌ Analyzer not enabled - check configuration")
        return False
    
    print("✅ Analyzer is ready!")
    return True

if __name__ == "__main__":
    test_analyzer()