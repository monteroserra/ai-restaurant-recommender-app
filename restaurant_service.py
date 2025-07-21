# restaurant_service.py
import requests
from config import GOOGLE_MAP_API_KEY

class RestaurantService:
    def __init__(self):
        self.nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.distance_matrix_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    
    def search_restaurants(self, lat, lng, radius=1000, min_reviews=200, max_results=5):
        """
        Search for restaurants near given coordinates
        """
        params = {
            "key": GOOGLE_MAP_API_KEY,
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "restaurant"
        }
        
        try:
            response = requests.get(self.nearby_url, params=params)
            data = response.json()

            if data.get("status") == "OK":
                places = data.get("results", [])
                
                # Filter places: must have rating and user_ratings_total >= min_reviews
                filtered_places = [
                    p for p in places 
                    if 'rating' in p and p.get('user_ratings_total', 0) >= min_reviews
                ]

                # Sort by rating descending
                filtered_places.sort(key=lambda x: x['rating'], reverse=True)
                
                return filtered_places[:max_results]
            else:
                print(f"Places API Error: {data.get('status')} - {data.get('error_message')}")
                return []
                
        except Exception as e:
            print(f"Error searching restaurants: {e}")
            return []

    def add_walking_distances(self, places, origin_lat, origin_lng):
        """
        Add walking distance and duration to restaurant data
        """
        if not places:
            return

        # Extract destination coordinates from places
        destinations = []
        for place in places:
            loc = place["geometry"]["location"]
            dest_str = f"{loc['lat']},{loc['lng']}"
            destinations.append(dest_str)

        # Join destinations with '|'
        destination_param = "|".join(destinations)

        params = {
            "key": GOOGLE_MAP_API_KEY,
            "origins": f"{origin_lat},{origin_lng}",
            "destinations": destination_param,
            "mode": "walking"
        }

        try:
            response = requests.get(self.distance_matrix_url, params=params)
            data = response.json()

            if data.get("status") == "OK":
                rows = data.get("rows", [])
                if rows and len(rows) > 0:
                    elements = rows[0].get("elements", [])
                    for i, element in enumerate(elements):
                        if i < len(places):  # Safety check
                            if element.get("status") == "OK":
                                distance_text = element["distance"]["text"]
                                duration_text = element["duration"]["text"]
                                places[i]["walking_distance"] = distance_text
                                places[i]["walking_duration"] = duration_text
                            else:
                                places[i]["walking_distance"] = "N/A"
                                places[i]["walking_duration"] = "N/A"
            else:
                print(f"Distance Matrix Error: {data.get('status')} - {data.get('error_message')}")
                # If error, mark all as N/A
                for place in places:
                    place["walking_distance"] = "N/A"
                    place["walking_duration"] = "N/A"
                    
        except Exception as e:
            print(f"Error getting walking distances: {e}")
            # If error, mark all as N/A
            for place in places:
                place["walking_distance"] = "N/A"
                place["walking_duration"] = "N/A"

    def format_restaurant_data(self, place):
        """
        Format restaurant data for display
        """
        return {
            'name': place.get("name", "No Name"),
            'rating': place.get("rating", "No Rating"),
            'reviews': place.get("user_ratings_total", 0),
            'address': place.get("vicinity", "No Address"),
            'walking_distance': place.get("walking_distance", "N/A"),
            'walking_duration': place.get("walking_duration", "N/A")
        }