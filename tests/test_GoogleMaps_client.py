import sys
import os

# Add the parent directory (project root) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GoogleMaps_client import search_places_by_rating_with_min_reviews, add_walking_distance_to_places 

## test Top 5 restaurants by rating with at least 200 reviews

latitude = 41.3870
longitude =  2.1700
radius = 200
min_reviews = 100

top_places = search_places_by_rating_with_min_reviews("restaurant", radius, min_reviews)
add_walking_distance_to_places(top_places)

# Print the results with walking distance
if top_places:
    print(f"\nTop {len(top_places)} restaurants by rating (>=200 reviews) within 1000m, including walking distance:\n")
    for place in top_places:
        name = place.get("name", "No Name")
        rating = place.get("rating", "No Rating")
        reviews = place.get("user_ratings_total", 0)
        address = place.get("vicinity", "No Address")
        walk_dist = place.get("walking_distance", "N/A")
        walk_dur = place.get("walking_duration", "N/A")

        print(f"Name: {name}")
        print(f"Rating: {rating}")
        print(f"Reviews: {reviews}")
        print(f"Address: {address}")
        print(f"Walking Distance: {walk_dist}, Walking Duration: {walk_dur}\n")