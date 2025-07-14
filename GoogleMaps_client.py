# imports
import sys
import os
import requests
# Add the parent directory (project root) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import GOOGLE_MAP_API_KEY, latitude, longitude

# Define URLs before functions
nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
distance_matrix_url = "https://maps.googleapis.com/maps/api/distancematrix/json"


def search_places_by_rating_with_min_reviews(place_type, radius=1000, min_reviews=200):
    params = {
        "key": GOOGLE_MAP_API_KEY,
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "type": place_type
    }
    response = requests.get(nearby_url, params=params)
    data = response.json()

    if data.get("status") == "OK":
        places = data.get("results", [])
        # Filter places: must have rating and user_ratings_total >= min_reviews
        places = [p for p in places if 'rating' in p and p.get('user_ratings_total', 0) >= min_reviews]

        # Sort by rating descending
        places.sort(key=lambda x: x['rating'], reverse=True)

        top_5 = places[:5]

        if not top_5:
            print(f"No {place_type}(s) found with at least {min_reviews} reviews.")
            return []

        return top_5
    else:
        print("Error:", data.get("status"), data.get("error_message"))
        return []

def add_walking_distance_to_places(places):
    if not places:
        return

    # Extract destination coordinates from places
    destinations = []
    for p in places:
        loc = p["geometry"]["location"]
        dest_str = f"{loc['lat']},{loc['lng']}"
        destinations.append(dest_str)

    # Join destinations with '|'
    destination_param = "|".join(destinations)

    params = {
        "key": GOOGLE_MAP_API_KEY,
        "origins": f"{latitude},{longitude}",
        "destinations": destination_param,
        "mode": "walking"
    }

    response = requests.get(distance_matrix_url, params=params)
    data = response.json()

    if data.get("status") == "OK":
        rows = data.get("rows", [])
        if rows and len(rows) > 0:
            elements = rows[0].get("elements", [])
            for i, element in enumerate(elements):
                if element.get("status") == "OK":
                    distance_text = element["distance"]["text"]
                    duration_text = element["duration"]["text"]
                    # Add this info back into the place dictionary
                    places[i]["walking_distance"] = distance_text
                    places[i]["walking_duration"] = duration_text
                else:
                    places[i]["walking_distance"] = "N/A"
                    places[i]["walking_duration"] = "N/A"
    else:
        print("Distance Matrix Error:", data.get("status"), data.get("error_message"))
        # If error, just mark as N/A
        for p in places:
            p["walking_distance"] = "N/A"
            p["walking_duration"] = "N/A"
