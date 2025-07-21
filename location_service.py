# location_service.py
import requests
from config import GOOGLE_MAP_API_KEY

class LocationService:
    def __init__(self):
        self.geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
        
    def get_coordinates_from_address(self, address):
        """
        Convert an address to latitude and longitude coordinates
        Returns tuple (lat, lng) or None if not found
        """
        if not address.strip():
            return None
            
        params = {
            "key": GOOGLE_MAP_API_KEY,
            "address": address
        }
        
        try:
            response = requests.get(self.geocoding_url, params=params)
            data = response.json()
            
            if data.get("status") == "OK" and data.get("results"):
                location = data["results"][0]["geometry"]["location"]
                return (location["lat"], location["lng"])
            else:
                print(f"Geocoding error: {data.get('status')}")
                return None
                
        except Exception as e:
            print(f"Error getting coordinates: {e}")
            return None
    
    def validate_coordinates(self, lat, lng):
        """
        Validate latitude and longitude values
        """
        try:
            lat = float(lat)
            lng = float(lng)
            
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return (lat, lng)
            else:
                return None
        except (ValueError, TypeError):
            return None