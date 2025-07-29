"""
Enhanced Restaurant Service with detailed information support
"""
import requests
import logging
from typing import List, Dict, Any, Optional, Tuple
import time

from config import GOOGLE_MAPS_API_KEY, GOOGLE_PLACES_BASE_URL, GOOGLE_GEOCODING_BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RestaurantService:
    def __init__(self):
        self.api_key = GOOGLE_MAPS_API_KEY
        self.session = requests.Session()  # Reuse connections
    
    def find_restaurants(
        self,
        latitude: float,
        longitude: float,
        radius: int = 1000,
        min_reviews: int = 10,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find restaurants near given coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in meters
            min_reviews: Minimum number of reviews required
            max_results: Maximum number of results to return
            
        Returns:
            List of restaurant dictionaries with enhanced data
        """
        try:
            # Use Places API Nearby Search
            url = f"{GOOGLE_PLACES_BASE_URL}/nearbysearch/json"
            
            params = {
                'location': f"{latitude},{longitude}",
                'radius': radius,
                'type': 'restaurant',
                'key': self.api_key,
            }
            
            logger.info(f"Searching for restaurants near {latitude}, {longitude}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.error(f"Places API error: {data.get('status')} - {data.get('error_message', '')}")
                return []
            
            # Process and filter results
            restaurants = []
            places = data.get('results', [])
            
            for place in places:
                restaurant = self._process_restaurant_data(place, latitude, longitude)
                
                # Apply filters
                if (restaurant.get('user_ratings_total', 0) >= min_reviews and
                    restaurant.get('rating', 0) > 0):
                    restaurants.append(restaurant)
                
                # Limit results
                if len(restaurants) >= max_results:
                    break
            
            # Sort by rating (descending) and then by number of reviews
            restaurants.sort(
                key=lambda x: (x.get('rating', 0), x.get('user_ratings_total', 0)),
                reverse=True
            )
            
            logger.info(f"Found {len(restaurants)} restaurants matching criteria")
            return restaurants
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in find_restaurants: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in find_restaurants: {e}")
            return []
    
    def _process_restaurant_data(
        self,
        place: Dict[str, Any],
        user_lat: float,
        user_lng: float
    ) -> Dict[str, Any]:
        """
        Process raw place data into restaurant dictionary.
        
        Args:
            place: Raw place data from Google Places API
            user_lat: User's latitude for distance calculation
            user_lng: User's longitude for distance calculation
            
        Returns:
            Processed restaurant dictionary
        """
        # Extract location
        location = place.get('geometry', {}).get('location', {})
        restaurant_lat = location.get('lat', 0)
        restaurant_lng = location.get('lng', 0)
        
        # Calculate distance and walking time
        distance_info = self._get_distance_and_time(
            user_lat, user_lng,
            restaurant_lat, restaurant_lng
        )
        
        # Extract photos
        photos = []
        if 'photos' in place:
            for photo in place['photos'][:3]:  # Get up to 3 photos
                photo_reference = photo.get('photo_reference')
                if photo_reference:
                    photo_url = self._get_photo_url(photo_reference, 400)
                    photos.append({
                        'reference': photo_reference,
                        'url': photo_url,
                        'width': photo.get('width', 400),
                        'height': photo.get('height', 400)
                    })
        
        # Extract price level
        price_level = place.get('price_level')
        price_text = self._format_price_level(price_level)
        
        # Check if currently open
        opening_hours = place.get('opening_hours', {})
        is_open_now = opening_hours.get('open_now', None)
        
        restaurant = {
            # Basic information
            'place_id': place.get('place_id', ''),
            'name': place.get('name', 'Unknown Restaurant'),
            'rating': place.get('rating', 0),
            'user_ratings_total': place.get('user_ratings_total', 0),
            'price_level': price_level,
            'price_text': price_text,
            
            # Location and contact
            'vicinity': place.get('vicinity', ''),
            'formatted_address': place.get('formatted_address', ''),
            'latitude': restaurant_lat,
            'longitude': restaurant_lng,
            
            # Distance and time
            'distance_meters': distance_info['distance_meters'],
            'distance_text': distance_info['distance_text'],
            'walking_time': distance_info['walking_time'],
            
            # Additional info
            'types': place.get('types', []),
            'photos': photos,
            'is_open_now': is_open_now,
            'permanently_closed': place.get('permanently_closed', False),
            
            # Business status
            'business_status': place.get('business_status', 'UNKNOWN'),
            
            # For detail analysis
            'has_detailed_info': False,  # Will be set to True after analysis
            'analysis_timestamp': None,
            
            # Display formatting
            'display_name': place.get('name', 'Unknown Restaurant')[:50],  # Truncate long names
            'display_rating': f"{place.get('rating', 0):.1f}/5" if place.get('rating') else "No rating",
            'display_reviews': f"({place.get('user_ratings_total', 0)} reviews)" if place.get('user_ratings_total') else "(No reviews)"
        }
        
        return restaurant
    
    def _get_distance_and_time(
        self,
        user_lat: float,
        user_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> Dict[str, Any]:
        """
        Calculate distance and walking time between two points.
        
        Returns:
            Dictionary with distance and time information
        """
        try:
            # Use Distance Matrix API for accurate walking time
            url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
            
            params = {
                'origins': f"{user_lat},{user_lng}",
                'destinations': f"{dest_lat},{dest_lng}",
                'mode': 'walking',
                'units': 'metric',
                'key': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if (data.get('status') == 'OK' and 
                data.get('rows') and 
                data['rows'][0].get('elements') and 
                data['rows'][0]['elements'][0].get('status') == 'OK'):
                
                element = data['rows'][0]['elements'][0]
                distance = element.get('distance', {})
                duration = element.get('duration', {})
                
                return {
                    'distance_meters': distance.get('value', 0),
                    'distance_text': distance.get('text', ''),
                    'walking_time': duration.get('text', ''),
                    'walking_time_seconds': duration.get('value', 0)
                }
            
        except Exception as e:
            logger.warning(f"Distance calculation failed: {e}")
        
        # Fallback: calculate straight-line distance
        distance_m = self._haversine_distance(user_lat, user_lng, dest_lat, dest_lng)
        walking_speed = 5  # km/h
        walking_time_hours = (distance_m / 1000) / walking_speed
        walking_time_minutes = int(walking_time_hours * 60)
        
        return {
            'distance_meters': int(distance_m),
            'distance_text': f"{distance_m:.0f} m" if distance_m < 1000 else f"{distance_m/1000:.1f} km",
            'walking_time': f"{walking_time_minutes} min" if walking_time_minutes > 0 else "< 1 min",
            'walking_time_seconds': walking_time_minutes * 60
        }
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate straight-line distance between two points using Haversine formula."""
        import math
        
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _get_photo_url(self, photo_reference: str, max_width: int = 400) -> str:
        """Generate photo URL from photo reference."""
        return (f"{GOOGLE_PLACES_BASE_URL}/photo?"
                f"maxwidth={max_width}&"
                f"photo_reference={photo_reference}&"
                f"key={self.api_key}")
    
    def _format_price_level(self, price_level: Optional[int]) -> str:
        """Format price level into readable text."""
        if price_level is None:
            return "Price not available"
        
        price_map = {
            0: "Free",
            1: "Inexpensive ($)",
            2: "Moderate ($$)",
            3: "Expensive ($$$)",
            4: "Very Expensive ($$$$)"
        }
        
        return price_map.get(price_level, "Price not available")
    
    def get_restaurant_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific restaurant.
        
        Args:
            place_id: Google Places ID
            
        Returns:
            Detailed restaurant information or None if not found
        """
        try:
            url = f"{GOOGLE_PLACES_BASE_URL}/details/json"
            
            params = {
                'place_id': place_id,
                'fields': ('name,rating,user_ratings_total,formatted_address,'
                          'international_phone_number,website,opening_hours,'
                          'price_level,photos,reviews,types,geometry'),
                'key': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.error(f"Place details error: {data.get('status')}")
                return None
            
            return data.get('result')
            
        except Exception as e:
            logger.error(f"Error getting restaurant details: {e}")
            return None
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """Validate latitude and longitude values."""
        try:
            lat = float(latitude)
            lng = float(longitude)
            return (-90 <= lat <= 90) and (-180 <= lng <= 180)
        except (ValueError, TypeError):
            return False
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates using Google Geocoding API.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            url = f"{GOOGLE_GEOCODING_BASE_URL}/json"
            
            params = {
                'address': address,
                'key': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK' or not data.get('results'):
                logger.error(f"Geocoding error: {data.get('status')}")
                return None
            
            location = data['results'][0]['geometry']['location']
            return (location['lat'], location['lng'])
            
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None

# Create global instance
restaurant_service = RestaurantService()