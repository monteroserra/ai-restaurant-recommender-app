"""
Enhanced restaurant service with AI-powered review analysis
Updated version of restaurant_service.py with Gemini integration
"""

import requests
import time
from typing import List, Dict, Optional

# Import configuration
from config import (
    GOOGLE_MAP_API_KEY,
    DEFAULT_RADIUS,
    GEMINI_ENABLED,
    MAX_RESTAURANTS_FOR_AI_ANALYSIS,
    MIN_REVIEWS_FOR_AI_ANALYSIS
)

# Import AI analyzer (NEW)
try:
    from gemini_analyzer import RestaurantAnalyzer
    AI_AVAILABLE = True
except ImportError:
    print("⚠️ Gemini analyzer not available - AI features disabled")
    AI_AVAILABLE = False
    RestaurantAnalyzer = None

class RestaurantService:
    """
    Restaurant service with AI-powered review analysis
    Handles restaurant search and data processing
    """
    
    def __init__(self):
        self.api_key = GOOGLE_MAP_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        
        # Initialize AI analyzer (NEW)
        self.ai_analyzer = None
        if GEMINI_ENABLED and AI_AVAILABLE:
            try:
                self.ai_analyzer = RestaurantAnalyzer()
                if not self.ai_analyzer.is_enabled():
                    self.ai_analyzer = None
                    print("⚠️ AI analyzer disabled - check API configuration")
                else:
                    print("✅ AI analysis enabled")
            except Exception as e:
                print(f"❌ Failed to initialize AI analyzer: {e}")
                self.ai_analyzer = None
        else:
            print("ℹ️ AI analysis disabled")
    
    def get_nearby_restaurants(self, lat: float, lng: float, radius: int = DEFAULT_RADIUS, 
                             min_reviews: int = 10, max_results: int = 5) -> List[Dict]:
        """
        Get nearby restaurants with optional AI analysis
        """
        try:
            print(f"🔍 Searching for restaurants near {lat}, {lng}")
            
            # Step 1: Get nearby restaurants
            restaurants = self._fetch_nearby_restaurants(lat, lng, radius, min_reviews, max_results)
            
            if not restaurants:
                print("⚠️ No restaurants found")
                return []
            
            # Step 2: Add distance information
            restaurants_with_distance = self._add_distance_info(restaurants, lat, lng)
            
            # Step 3: Add AI analysis (NEW)
            if self.ai_analyzer:
                restaurants_with_ai = self._add_ai_analysis(restaurants_with_distance)
                return restaurants_with_ai
            
            return restaurants_with_distance
            
        except Exception as e:
            print(f"❌ Error in restaurant service: {e}")
            return []
    
    def _fetch_nearby_restaurants(self, lat: float, lng: float, radius: int, 
                                min_reviews: int, max_results: int) -> List[Dict]:
        """
        Fetch restaurants using Google Places API
        """
        try:
            # Nearby search API call
            nearby_url = f"{self.base_url}/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': radius,
                'type': 'restaurant',
                'key': self.api_key
            }
            
            response = requests.get(nearby_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'OK':
                raise Exception(f"Places API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
            
            restaurants = []
            for place in data.get('results', []):
                # Filter by minimum reviews
                user_ratings_total = place.get('user_ratings_total', 0)
                if user_ratings_total < min_reviews:
                    continue
                
                # Extract restaurant data
                restaurant = {
                    'name': place.get('name', 'Unknown Restaurant'),
                    'rating': place.get('rating', 0),
                    'user_ratings_total': user_ratings_total,
                    'vicinity': place.get('vicinity', ''),
                    'place_id': place.get('place_id'),
                    'price_level': place.get('price_level'),
                    'types': place.get('types', []),
                    'geometry': place.get('geometry', {}),
                    # NEW: Initialize AI fields
                    'ai_summary': None,
                    'analysis_status': 'pending'
                }
                
                restaurants.append(restaurant)
                
                # Stop when we have enough results
                if len(restaurants) >= max_results:
                    break
            
            # Sort by rating and review count
            restaurants.sort(key=lambda x: (x['rating'], x['user_ratings_total']), reverse=True)
            
            print(f"✅ Found {len(restaurants)} restaurants")
            return restaurants
            
        except Exception as e:
            print(f"❌ Error fetching restaurants: {e}")
            return []
    
    def _add_distance_info(self, restaurants: List[Dict], user_lat: float, user_lng: float) -> List[Dict]:
        """
        Add walking distance and time to restaurants
        """
        try:
            if not restaurants:
                return restaurants
            
            print("📏 Calculating distances...")
            
            # Prepare destinations for Distance Matrix API
            destinations = []
            for restaurant in restaurants:
                geometry = restaurant.get('geometry', {})
                location = geometry.get('location', {})
                if location.get('lat') and location.get('lng'):
                    destinations.append(f"{location['lat']},{location['lng']}")
            
            if not destinations:
                # No valid coordinates found
                for restaurant in restaurants:
                    restaurant['distance'] = 'Unknown'
                    restaurant['duration'] = 'Unknown'
                return restaurants
            
            # Distance Matrix API call
            distance_url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
            params = {
                'origins': f"{user_lat},{user_lng}",
                'destinations': '|'.join(destinations),
                'mode': 'walking',
                'units': 'metric',
                'key': self.api_key
            }
            
            response = requests.get(distance_url, params=params, timeout=10)
            response.raise_for_status()
            distance_data = response.json()
            
            if distance_data.get('status') == 'OK':
                elements = distance_data.get('rows', [{}])[0].get('elements', [])
                
                for i, restaurant in enumerate(restaurants):
                    if i < len(elements) and elements[i].get('status') == 'OK':
                        distance_info = elements[i]
                        restaurant['distance'] = distance_info.get('distance', {}).get('text', 'Unknown')
                        restaurant['duration'] = distance_info.get('duration', {}).get('text', 'Unknown')
                    else:
                        restaurant['distance'] = 'Unknown'
                        restaurant['duration'] = 'Unknown'
            
            print("✅ Distance calculation completed")
            return restaurants
            
        except Exception as e:
            print(f"⚠️ Error calculating distances: {e}")
            # Return restaurants without distance info
            for restaurant in restaurants:
                restaurant['distance'] = 'Unknown'
                restaurant['duration'] = 'Unknown'
            return restaurants
    
    def _add_ai_analysis(self, restaurants: List[Dict]) -> List[Dict]:
        """
        NEW: Add AI-powered review analysis to restaurants
        """
        if not self.ai_analyzer:
            # Mark all as not analyzed
            for restaurant in restaurants:
                restaurant['analysis_status'] = 'ai_disabled'
            return restaurants
        
        try:
            # Only analyze top restaurants to save API quota
            restaurants_to_analyze = restaurants[:MAX_RESTAURANTS_FOR_AI_ANALYSIS]
            
            print(f"🤖 Starting AI analysis for top {len(restaurants_to_analyze)} restaurants...")
            
            for i, restaurant in enumerate(restaurants_to_analyze):
                try:
                    # Check if restaurant has enough reviews
                    if restaurant.get('user_ratings_total', 0) < MIN_REVIEWS_FOR_AI_ANALYSIS:
                        restaurant['analysis_status'] = 'insufficient_reviews'
                        continue
                    
                    place_id = restaurant.get('place_id')
                    name = restaurant.get('name')
                    
                    if not place_id or not name:
                        restaurant['analysis_status'] = 'missing_data'
                        continue
                    
                    # Update status
                    restaurant['analysis_status'] = 'analyzing'
                    
                    # Get AI analysis
                    print(f"🔍 Analyzing {name} ({i+1}/{len(restaurants_to_analyze)})")
                    
                    summary = self.ai_analyzer.get_analysis_for_restaurant(place_id, name)
                    
                    if summary:
                        restaurant['ai_summary'] = {
                            'summary': summary.summary,
                            'highlights': summary.highlights,
                            'criticisms': summary.criticisms,
                            'sentiment': summary.overall_sentiment,
                            'confidence': summary.confidence_score
                        }
                        restaurant['analysis_status'] = 'completed'
                        print(f"✅ Analysis completed for {name}")
                    else:
                        restaurant['analysis_status'] = 'failed'
                        print(f"❌ Analysis failed for {name}")
                    
                    # Brief pause between analyses
                    if i < len(restaurants_to_analyze) - 1:
                        time.sleep(0.5)
                        
                except Exception as e:
                    print(f"❌ Error analyzing {restaurant.get('name', 'Unknown')}: {e}")
                    restaurant['analysis_status'] = 'error'
            
            # Mark remaining restaurants as not analyzed
            for restaurant in restaurants[MAX_RESTAURANTS_FOR_AI_ANALYSIS:]:
                restaurant['analysis_status'] = 'not_analyzed'
            
            print("🎉 AI analysis phase completed!")
            return restaurants
            
        except Exception as e:
            print(f"❌ Error in AI analysis phase: {e}")
            # Mark all analyzing restaurants as failed
            for restaurant in restaurants:
                if restaurant.get('analysis_status') == 'analyzing':
                    restaurant['analysis_status'] = 'failed'
            return restaurants
    
    def get_restaurant_details(self, place_id: str) -> Dict:
        """
        Get detailed information for a specific restaurant
        """
        try:
            details_url = f"{self.base_url}/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,rating,user_ratings_total,formatted_address,formatted_phone_number,website,opening_hours,price_level,reviews',
                'key': self.api_key
            }
            
            response = requests.get(details_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK':
                return data.get('result', {})
            else:
                print(f"⚠️ Error getting restaurant details: {data.get('status')}")
                return {}
                
        except Exception as e:
            print(f"❌ Error fetching restaurant details: {e}")
            return {}
    
    def analyze_single_restaurant(self, place_id: str, restaurant_name: str) -> Optional[Dict]:
        """
        NEW: Get AI analysis for a single restaurant
        """
        if not self.ai_analyzer:
            return None
        
        summary = self.ai_analyzer.get_analysis_for_restaurant(place_id, restaurant_name)
        
        if summary:
            return {
                'summary': summary.summary,
                'highlights': summary.highlights,
                'criticisms': summary.criticisms,
                'sentiment': summary.overall_sentiment,
                'confidence': summary.confidence_score
            }
        
        return None
    
    def is_ai_enabled(self) -> bool:
        """Check if AI analysis is available"""
        return self.ai_analyzer is not None and self.ai_analyzer.is_enabled()
    
    # BACKWARD COMPATIBILITY METHODS
    def search_restaurants(self, lat: float, lng: float, radius: int = DEFAULT_RADIUS, 
                          min_reviews: int = 10, max_results: int = 5) -> List[Dict]:
        """
        Backward compatibility method - calls get_nearby_restaurants
        """
        return self.get_nearby_restaurants(lat, lng, radius, min_reviews, max_results)
    
    def get_restaurants(self, lat: float, lng: float, **kwargs) -> List[Dict]:
        """
        Alternative backward compatibility method
        """
        radius = kwargs.get('radius', DEFAULT_RADIUS)
        min_reviews = kwargs.get('min_reviews', 10)
        max_results = kwargs.get('max_results', 5)
        return self.get_nearby_restaurants(lat, lng, radius, min_reviews, max_results)


# Test function
def test_restaurant_service():
    """Test the enhanced restaurant service"""
    print("🧪 Testing Enhanced Restaurant Service...")
    
    service = RestaurantService()
    
    # Test coordinates (New York City)
    lat, lng = 40.7128, -74.0060
    
    print(f"🔍 Testing search near {lat}, {lng}")
    
    # Get restaurants
    restaurants = service.get_nearby_restaurants(lat, lng, radius=1000, max_results=3)
    
    print(f"\n📊 Results Summary:")
    print(f"Found {len(restaurants)} restaurants")
    print(f"AI Analysis Available: {'✅' if service.is_ai_enabled() else '❌'}")
    
    for i, restaurant in enumerate(restaurants, 1):
        print(f"\n🍽️ Restaurant {i}: {restaurant['name']}")
        print(f"   ⭐ Rating: {restaurant['rating']}/5 ({restaurant['user_ratings_total']} reviews)")
        print(f"   📍 Distance: {restaurant.get('distance', 'Unknown')}")
        print(f"   🤖 AI Status: {restaurant.get('analysis_status', 'unknown')}")
        
        if restaurant.get('ai_summary'):
            ai = restaurant['ai_summary']
            print(f"   📝 AI Summary: {ai['summary'][:100]}...")
            print(f"   😊 Sentiment: {ai['sentiment']} (confidence: {ai['confidence']:.1%})")

if __name__ == "__main__":
    test_restaurant_service()