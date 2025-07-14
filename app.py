# Here we have the main logic of the app

user_name = 'Nacho'

print(f'Hello {user_name}!, we are initializing the app')


## UI for this prototype or MVp

import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
import os

# Add the parent directory (project root) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GoogleMaps_client import search_places_by_rating_with_min_reviews, add_walking_distance_to_places 

def get_top_restaurants():
    radius = radius_scale.get()
    min_reviews = reviews_scale.get()

    output_text.delete('1.0', tk.END)  # Clear previous output

    top_places = search_places_by_rating_with_min_reviews("restaurant", radius, min_reviews)
    add_walking_distance_to_places(top_places)

    if not top_places:
        output_text.insert(tk.END, "No restaurants found with the given criteria.\n")
        return

    output_text.insert(tk.END, f"Top {len(top_places)} restaurants by rating (≥ {min_reviews} reviews) within {radius}m:\n\n")

    for place in top_places:
        name = place.get("name", "No Name")
        rating = place.get("rating", "No Rating")
        reviews = place.get("user_ratings_total", 0)
        address = place.get("vicinity", "No Address")
        walk_dist = place.get("walking_distance", "N/A")
        walk_dur = place.get("walking_duration", "N/A")

        output_text.insert(tk.END, f"Name: {name}\n")
        output_text.insert(tk.END, f"Rating: {rating}\n")
        output_text.insert(tk.END, f"Reviews: {reviews}\n")
        output_text.insert(tk.END, f"Address: {address}\n")
        output_text.insert(tk.END, f"Walking Distance: {walk_dist}, Duration: {walk_dur}\n")
        output_text.insert(tk.END, "-"*40 + "\n")


# Build the UI
root = tk.Tk()
root.title("Top Restaurants Finder")

frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky="WENS")

# Radius slider
ttk.Label(frame, text="Search Radius (meters):").grid(row=0, column=0, sticky="W")
radius_scale = tk.Scale(frame, from_=100, to=2000, orient=tk.HORIZONTAL)
radius_scale.set(200)  # default
radius_scale.grid(row=1, column=0, sticky="WE")

# Min reviews slider
ttk.Label(frame, text="Minimum Reviews:").grid(row=2, column=0, sticky="W")
reviews_scale = tk.Scale(frame, from_=10, to=500, orient=tk.HORIZONTAL)
reviews_scale.set(100)  # default
reviews_scale.grid(row=3, column=0, sticky="WE")

# Search button
search_btn = ttk.Button(frame, text="Find Top Restaurants", command=get_top_restaurants)
search_btn.grid(row=4, column=0, pady=10)

# Output text box
output_text = scrolledtext.ScrolledText(frame, width=60, height=20, wrap=tk.WORD)
output_text.grid(row=5, column=0, pady=10)

root.mainloop()
