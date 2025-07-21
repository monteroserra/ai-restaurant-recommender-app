# ui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class RestaurantFinderUI:
    def __init__(self, search_callback):
        self.search_callback = search_callback
        self.setup_ui()
    
    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("AI Restaurant Recommender 🍽️")
        self.root.geometry("800x700")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.grid(row=0, column=0, sticky="NSEW")
        
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🍽️ AI Restaurant Recommender", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Location Frame
        location_frame = ttk.LabelFrame(main_frame, text="📍 Location Settings", padding=10)
        location_frame.grid(row=1, column=0, sticky="EW", pady=(0, 15))
        location_frame.columnconfigure(1, weight=1)
        
        # Location type selection
        self.location_type = tk.StringVar(value="coordinates")
        
        coords_radio = ttk.Radiobutton(location_frame, text="Use Coordinates", 
                                      variable=self.location_type, value="coordinates",
                                      command=self.toggle_location_inputs)
        coords_radio.grid(row=0, column=0, sticky="W")
        
        address_radio = ttk.Radiobutton(location_frame, text="Use Address", 
                                       variable=self.location_type, value="address",
                                       command=self.toggle_location_inputs)
        address_radio.grid(row=0, column=1, sticky="W")
        
        # Coordinates inputs
        self.coords_frame = ttk.Frame(location_frame)
        self.coords_frame.grid(row=1, column=0, columnspan=2, sticky="EW", pady=(10, 0))
        self.coords_frame.columnconfigure(1, weight=1)
        self.coords_frame.columnconfigure(3, weight=1)
        
        ttk.Label(self.coords_frame, text="Latitude:").grid(row=0, column=0, padx=(0, 5))
        self.lat_entry = ttk.Entry(self.coords_frame)
        self.lat_entry.grid(row=0, column=1, padx=(0, 20), sticky="EW")
        
        ttk.Label(self.coords_frame, text="Longitude:").grid(row=0, column=2, padx=(0, 5))
        self.lng_entry = ttk.Entry(self.coords_frame)
        self.lng_entry.grid(row=0, column=3, sticky="EW")
        
        # Address input
        self.address_frame = ttk.Frame(location_frame)
        self.address_frame.grid(row=2, column=0, columnspan=2, sticky="EW", pady=(10, 0))
        self.address_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.address_frame, text="Address:").grid(row=0, column=0, padx=(0, 10))
        self.address_entry = ttk.Entry(self.address_frame, width=50)
        self.address_entry.grid(row=0, column=1, sticky="EW")
        
        # Search Parameters Frame
        params_frame = ttk.LabelFrame(main_frame, text="🔍 Search Parameters", padding=10)
        params_frame.grid(row=2, column=0, sticky="EW", pady=(0, 15))
        params_frame.columnconfigure(0, weight=1)
        
        # Radius slider
        ttk.Label(params_frame, text="Search Radius (meters):").grid(row=0, column=0, sticky="W")
        self.radius_scale = tk.Scale(params_frame, from_=100, to=5000, orient=tk.HORIZONTAL,
                                    resolution=100)
        self.radius_scale.set(1000)
        self.radius_scale.grid(row=1, column=0, sticky="EW", pady=(5, 10))
        
        # Min reviews slider
        ttk.Label(params_frame, text="Minimum Reviews:").grid(row=2, column=0, sticky="W")
        self.reviews_scale = tk.Scale(params_frame, from_=10, to=1000, orient=tk.HORIZONTAL,
                                     resolution=10)
        self.reviews_scale.set(100)
        self.reviews_scale.grid(row=3, column=0, sticky="EW", pady=(5, 10))
        
        # Max results slider
        ttk.Label(params_frame, text="Maximum Results:").grid(row=4, column=0, sticky="W")
        self.max_results_scale = tk.Scale(params_frame, from_=1, to=20, orient=tk.HORIZONTAL)
        self.max_results_scale.set(5)
        self.max_results_scale.grid(row=5, column=0, sticky="EW", pady=(5, 10))
        
        # Search button
        self.search_btn = ttk.Button(main_frame, text="🔍 Find Top Restaurants", 
                                    command=self.handle_search, style="Accent.TButton")
        self.search_btn.grid(row=3, column=0, pady=15)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="📊 Results", padding=10)
        results_frame.grid(row=4, column=0, sticky="NSEW", pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Output text box with scrollbar
        self.output_text = scrolledtext.ScrolledText(results_frame, width=70, height=15, 
                                                    wrap=tk.WORD, font=("Consolas", 10))
        self.output_text.grid(row=0, column=0, sticky="NSEW")
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to search for restaurants...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor="w")
        status_bar.grid(row=5, column=0, sticky="EW", pady=(5, 0))
        
        # Configure grid weights for main frame
        main_frame.rowconfigure(4, weight=1)
        
        # Initialize UI state
        self.toggle_location_inputs()
        self.set_default_coordinates()
    
    def set_default_coordinates(self):
        """Set default coordinates (you can change these to your preferred defaults)"""
        # Default to New York City coordinates
        self.lat_entry.insert(0, "40.7128")
        self.lng_entry.insert(0, "-74.0060")
    
    def toggle_location_inputs(self):
        """Show/hide location input fields based on selection"""
        if self.location_type.get() == "coordinates":
            self.coords_frame.grid()
            self.address_frame.grid_remove()
        else:
            self.coords_frame.grid_remove()
            self.address_frame.grid()
    
    def handle_search(self):
        """Handle the search button click"""
        try:
            self.search_btn.config(state="disabled")
            self.status_var.set("Searching for restaurants...")
            self.root.update()
            
            # Get search parameters
            radius = self.radius_scale.get()
            min_reviews = self.reviews_scale.get()
            max_results = self.max_results_scale.get()
            
            # Get location based on input type
            if self.location_type.get() == "coordinates":
                lat = self.lat_entry.get().strip()
                lng = self.lng_entry.get().strip()
                
                if not lat or not lng:
                    self.show_error("Please enter both latitude and longitude")
                    return
                
                location_data = {"type": "coordinates", "lat": lat, "lng": lng}
            else:
                address = self.address_entry.get().strip()
                if not address:
                    self.show_error("Please enter an address")
                    return
                
                location_data = {"type": "address", "address": address}
            
            # Call the search callback
            self.search_callback(location_data, radius, min_reviews, max_results)
            
        except Exception as e:
            self.show_error(f"An error occurred: {str(e)}")
        finally:
            self.search_btn.config(state="normal")
            self.status_var.set("Search completed")
    
    def display_results(self, restaurants, location_info):
        """Display search results in the text area"""
        self.output_text.delete('1.0', tk.END)
        
        if not restaurants:
            self.output_text.insert(tk.END, "No restaurants found with the given criteria.\n")
            self.output_text.insert(tk.END, "Try adjusting your search parameters (radius, minimum reviews).")
            return
        
        # Header
        header = f"🎯 Found {len(restaurants)} restaurants near {location_info}\n"
        header += "="*60 + "\n\n"
        self.output_text.insert(tk.END, header)
        
        # Restaurant details
        for i, restaurant in enumerate(restaurants, 1):
            restaurant_text = f"{i}. 🍽️ {restaurant['name']}\n"
            restaurant_text += f"   ⭐ Rating: {restaurant['rating']}/5 ({restaurant['reviews']} reviews)\n"
            restaurant_text += f"   📍 Address: {restaurant['address']}\n"
            restaurant_text += f"   🚶 Walking: {restaurant['walking_distance']} ({restaurant['walking_duration']})\n"
            restaurant_text += "-" * 50 + "\n\n"
            
            self.output_text.insert(tk.END, restaurant_text)
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
        self.status_var.set("Error occurred")
    
    def show_info(self, message):
        """Show info message"""
        messagebox.showinfo("Information", message)
    
    def run(self):
        """Start the UI main loop"""
        self.root.mainloop()