# main.py
"""
AI Restaurant Recommender App
Main application entry point that coordinates UI, location services, and restaurant services
"""

import sys
import os

# Add the parent directory (project root) to sys.path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui import RestaurantFinderUI
from restaurant_service import RestaurantService
from location_service import LocationService

class RestaurantRecommenderApp:
    def __init__(self):
        self.restaurant_service = RestaurantService()
        self.location_service = LocationService()
        self.ui = RestaurantFinderUI(self.search_restaurants)
        
    def search_restaurants(self, location_data, radius, min_reviews, max_results):
        """
        Main search logic that coordinates location resolution and restaurant search
        """
        try:
            # Step 1: Get coordinates
            coordinates = self.resolve_location(location_data)
            if coordinates is None:
                return
            
            lat, lng = coordinates
            
            # Step 2: Search for restaurants
            self.ui.status_var.set("Searching for restaurants...")
            restaurants = self.restaurant_service.search_restaurants(
                lat, lng, radius, min_reviews, max_results
            )
            
            if not restaurants:
                location_str = self.format_location_string(location_data, lat, lng)
                self.ui.display_results([], location_str)
                return
            
            # Step 3: Add walking distances
            self.ui.status_var.set("Calculating walking distances...")
            self.restaurant_service.add_walking_distances(restaurants, lat, lng)
            
            # Step 4: Format results
            formatted_restaurants = [
                self.restaurant_service.format_restaurant_data(place) 
                for place in restaurants
            ]
            
            # Step 5: Display results
            location_str = self.format_location_string(location_data, lat, lng)
            self.ui.display_results(formatted_restaurants, location_str)
            
        except Exception as e:
            self.ui.show_error(f"Search failed: {str(e)}")
            print(f"Search error: {e}")  # For debugging
    
    def resolve_location(self, location_data):
        """
        Convert location data to coordinates
        Returns (lat, lng) tuple or None if failed
        """
        if location_data["type"] == "coordinates":
            # Validate coordinates
            coordinates = self.location_service.validate_coordinates(
                location_data["lat"], location_data["lng"]
            )
            if coordinates is None:
                self.ui.show_error("Invalid coordinates. Please check your latitude and longitude values.")
                return None
            return coordinates
            
        elif location_data["type"] == "address":
            # Convert address to coordinates
            self.ui.status_var.set("Converting address to coordinates...")
            coordinates = self.location_service.get_coordinates_from_address(
                location_data["address"]
            )
            if coordinates is None:
                self.ui.show_error("Could not find coordinates for the given address. Please try a different address.")
                return None
            return coordinates
        
        return None
    
    def format_location_string(self, location_data, lat, lng):
        """
        Create a readable location string for display
        """
        if location_data["type"] == "coordinates":
            return f"coordinates ({lat:.4f}, {lng:.4f})"
        else:
            return f"{location_data['address']} ({lat:.4f}, {lng:.4f})"
    
    def run(self):
        """
        Start the application
        """
        print("🍽️ Starting AI Restaurant Recommender App...")
        print("Make sure you have your Google Maps API key configured in config.py")
        self.ui.run()

def main():
    """
    Application entry point
    """
    try:
        app = RestaurantRecommenderApp()
        app.run()
    except ImportError as e:
        print(f"Configuration Error: {e}")
        print("Please make sure you have a config.py file with your GOOGLE_MAP_API_KEY")
    except Exception as e:
        print(f"Application Error: {e}")

if __name__ == "__main__":
    main()