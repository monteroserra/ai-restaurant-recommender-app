"""
Location Service for address-to-coordinates conversion and location utilities
"""
import requests
import logging
from typing import Optional, Tuple, Dict, Any

from config import GOOGLE_MAPS_API_KEY, GOOGLE_GEOCODING_BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocationService:
    def __init__(self):
        self.api_key = GOOGLE_MAPS_API_KEY
        self.session = requests.Session()  # Reuse connections
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates using Google Geocoding API.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        if not address or not address.strip():
            logger.error("Empty address provided for geocoding")
            return None
        
        try:
            url = f"{GOOGLE_GEOCODING_BASE_URL}/json"
            
            params = {
                'address': address.strip(),
                'key': self.api_key
            }
            
            logger.info(f"Geocoding address: {address}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.error(f"Geocoding API error: {data.get('status')} - {data.get('error_message', '')}")
                return None
            
            results = data.get('results', [])
            if not results:
                logger.warning(f"No results found for address: {address}")
                return None
            
            # Get the first result's coordinates
            location = results[0]['geometry']['location']
            coordinates = (location['lat'], location['lng'])
            
            logger.info(f"Geocoded '{address}' to {coordinates}")
            return coordinates
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during geocoding: {e}")
            return None
        except KeyError as e:
            logger.error(f"Unexpected API response structure: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during geocoding: {e}")
            return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Convert coordinates to address using Google Geocoding API.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Formatted address string or None if not found
        """
        if not self.validate_coordinates(latitude, longitude):
            logger.error(f"Invalid coordinates provided: {latitude}, {longitude}")
            return None
        
        try:
            url = f"{GOOGLE_GEOCODING_BASE_URL}/json"
            
            params = {
                'latlng': f"{latitude},{longitude}",
                'key': self.api_key
            }
            
            logger.info(f"Reverse geocoding coordinates: {latitude}, {longitude}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.error(f"Reverse geocoding API error: {data.get('status')} - {data.get('error_message', '')}")
                return None
            
            results = data.get('results', [])
            if not results:
                logger.warning(f"No results found for coordinates: {latitude}, {longitude}")
                return None
            
            # Get the first result's formatted address
            address = results[0].get('formatted_address', '')
            
            logger.info(f"Reverse geocoded {latitude}, {longitude} to '{address}'")
            return address
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during reverse geocoding: {e}")
            return None
        except KeyError as e:
            logger.error(f"Unexpected API response structure: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during reverse geocoding: {e}")
            return None
    
    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed place information from Google Places API.
        
        Args:
            place_id: Google Places ID
            
        Returns:
            Place details dictionary or None if not found
        """
        if not place_id:
            logger.error("Empty place_id provided")
            return None
        
        try:
            from config import GOOGLE_PLACES_BASE_URL
            url = f"{GOOGLE_PLACES_BASE_URL}/details/json"
            
            params = {
                'place_id': place_id,
                'fields': 'formatted_address,geometry,name,place_id,types,vicinity',
                'key': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.error(f"Place details API error: {data.get('status')} - {data.get('error_message', '')}")
                return None
            
            result = data.get('result')
            if not result:
                logger.warning(f"No place details found for place_id: {place_id}")
                return None
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting place details: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting place details: {e}")
            return None
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate latitude and longitude values.
        
        Args:
            latitude: Latitude value
            longitude: Longitude value
            
        Returns:
            True if coordinates are valid, False otherwise
        """
        try:
            lat = float(latitude)
            lng = float(longitude)
            
            # Check latitude bounds (-90 to 90)
            if lat < -90 or lat > 90:
                return False
            
            # Check longitude bounds (-180 to 180)
            if lng < -180 or lng > 180:
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great-circle distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in meters
        """
        import math
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in meters
        r = 6371000
        
        return r * c
    
    def format_distance(self, distance_meters: float) -> str:
        """
        Format distance for human-readable display.
        
        Args:
            distance_meters: Distance in meters
            
        Returns:
            Formatted distance string
        """
        if distance_meters < 1000:
            return f"{distance_meters:.0f} m"
        else:
            return f"{distance_meters / 1000:.1f} km"
    
    def estimate_walking_time(self, distance_meters: float, walking_speed_kmh: float = 5.0) -> str:
        """
        Estimate walking time based on distance.
        
        Args:
            distance_meters: Distance in meters
            walking_speed_kmh: Walking speed in km/h (default 5 km/h)
            
        Returns:
            Formatted walking time string
        """
        distance_km = distance_meters / 1000
        hours = distance_km / walking_speed_kmh
        minutes = hours * 60
        
        if minutes < 1:
            return "< 1 min"
        elif minutes < 60:
            return f"{minutes:.0f} min"
        else:
            hours = minutes / 60
            return f"{hours:.1f} h"
    
    def get_nearby_places(
        self, 
        latitude: float, 
        longitude: float, 
        place_type: str = 'restaurant',
        radius: int = 1000
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get nearby places of a specific type.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            place_type: Type of place to search for
            radius: Search radius in meters
            
        Returns:
            List of place dictionaries or None if error
        """
        if not self.validate_coordinates(latitude, longitude):
            logger.error(f"Invalid coordinates: {latitude}, {longitude}")
            return None
        
        try:
            from config import GOOGLE_PLACES_BASE_URL
            url = f"{GOOGLE_PLACES_BASE_URL}/nearbysearch/json"
            
            params = {
                'location': f"{latitude},{longitude}",
                'radius': radius,
                'type': place_type,
                'key': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.error(f"Nearby search API error: {data.get('status')} - {data.get('error_message', '')}")
                return None
            
            return data.get('results', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during nearby search: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during nearby search: {e}")
            return None

# Create global instance
location_service = LocationService()