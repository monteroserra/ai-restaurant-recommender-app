"""
Enhanced User Interface with Restaurant Analysis Feature
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from typing import List, Dict, Any, Optional

from restaurant_service import restaurant_service
from detail_view import RestaurantDetailView
from config import DEFAULT_RADIUS, DEFAULT_MIN_REVIEWS, DEFAULT_MAX_RESULTS

# Configure logging
logger = logging.getLogger(__name__)

class RestaurantUI:
    def __init__(self, root):
        self.root = root
        self.current_restaurants = []
        self.location_type = tk.StringVar(value="coordinates")
        self.status_var = tk.StringVar(value="Ready")
        
        # Initialize UI components
        self.setup_ui()
        self.set_default_values()
    
    def setup_ui(self):
        """Set up the main user interface."""
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Results frame should expand
        
        # Create sections
        self.create_location_section(main_frame)
        self.create_parameters_section(main_frame)
        self.create_results_section(main_frame)
        self.create_status_section(main_frame)
    
    def create_location_section(self, parent):
        """Create the location input section."""
        # Location frame
        location_frame = ttk.LabelFrame(parent, text="Location", padding="10")
        location_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        location_frame.columnconfigure(1, weight=1)
        
        # Location type selection
        coord_radio = ttk.Radiobutton(
            location_frame,
            text="Use Coordinates",
            variable=self.location_type,
            value="coordinates",
            command=self.on_location_type_change
        )
        coord_radio.grid(row=0, column=0, sticky=tk.W)
        
        address_radio = ttk.Radiobutton(
            location_frame,
            text="Use Address",
            variable=self.location_type,
            value="address",
            command=self.on_location_type_change
        )
        address_radio.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Coordinates input
        self.coord_frame = ttk.Frame(location_frame)
        self.coord_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        self.coord_frame.columnconfigure(1, weight=1)
        self.coord_frame.columnconfigure(3, weight=1)
        
        ttk.Label(self.coord_frame, text="Latitude:").grid(row=0, column=0, sticky=tk.W)
        self.lat_entry = ttk.Entry(self.coord_frame, width=15)
        self.lat_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 10))
        
        ttk.Label(self.coord_frame, text="Longitude:").grid(row=0, column=2, sticky=tk.W)
        self.lng_entry = ttk.Entry(self.coord_frame, width=15)
        self.lng_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Address input
        self.address_frame = ttk.Frame(location_frame)
        self.address_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        self.address_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.address_frame, text="Address:").grid(row=0, column=0, sticky=tk.W)
        self.address_entry = ttk.Entry(self.address_frame)
        self.address_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Initially hide address frame
        self.address_frame.grid_remove()
    
    def create_parameters_section(self, parent):
        """Create the search parameters section."""
        params_frame = ttk.LabelFrame(parent, text="Search Parameters", padding="10")
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        params_frame.columnconfigure(1, weight=1)
        
        # Search radius
        ttk.Label(params_frame, text="Search Radius:").grid(row=0, column=0, sticky=tk.W)
        
        radius_frame = ttk.Frame(params_frame)
        radius_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        radius_frame.columnconfigure(0, weight=1)
        
        self.radius_var = tk.IntVar(value=DEFAULT_RADIUS)
        self.radius_scale = ttk.Scale(
            radius_frame,
            from_=100, to=5000,
            variable=self.radius_var,
            orient=tk.HORIZONTAL,
            command=self.update_radius_label
        )
        self.radius_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.radius_label = ttk.Label(radius_frame, text=f"{DEFAULT_RADIUS}m")
        self.radius_label.grid(row=0, column=1, padx=(10, 0))
        
        # Minimum reviews
        ttk.Label(params_frame, text="Min Reviews:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        reviews_frame = ttk.Frame(params_frame)
        reviews_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        reviews_frame.columnconfigure(0, weight=1)
        
        self.min_reviews_var = tk.IntVar(value=DEFAULT_MIN_REVIEWS)
        self.min_reviews_scale = ttk.Scale(
            reviews_frame,
            from_=10, to=1000,
            variable=self.min_reviews_var,
            orient=tk.HORIZONTAL,
            command=self.update_reviews_label
        )
        self.min_reviews_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.reviews_label = ttk.Label(reviews_frame, text=f"{DEFAULT_MIN_REVIEWS}")
        self.reviews_label.grid(row=0, column=1, padx=(10, 0))
        
        # Maximum results
        ttk.Label(params_frame, text="Max Results:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        results_frame = ttk.Frame(params_frame)
        results_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        
        self.max_results_var = tk.IntVar(value=DEFAULT_MAX_RESULTS)
        self.max_results_scale = ttk.Scale(
            results_frame,
            from_=1, to=20,
            variable=self.max_results_var,
            orient=tk.HORIZONTAL,
            command=self.update_results_label
        )
        self.max_results_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.results_label = ttk.Label(results_frame, text=f"{DEFAULT_MAX_RESULTS}")
        self.results_label.grid(row=0, column=1, padx=(10, 0))
        
        # Search button
        search_btn = ttk.Button(
            params_frame,
            text="Find Restaurants",
            command=self.search_restaurants,
            style="Accent.TButton"
        )
        search_btn.grid(row=3, column=0, columnspan=2, pady=(15, 0))
    
    def create_results_section(self, parent):
        """Create the results display section."""
        results_frame = ttk.LabelFrame(parent, text="Results", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create scrollable frame for results
        self.create_scrollable_results(results_frame)
    
    def create_scrollable_results(self, parent):
        """Create scrollable results area."""
        # Create canvas and scrollbar
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        
        # Create frame for restaurant items
        self.results_inner_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        self.results_inner_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.results_inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid canvas and scrollbar
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Store references
        self.results_canvas = canvas
        self.results_scrollbar = scrollbar
        
        # Bind mousewheel to canvas
        canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.results_inner_frame.bind("<MouseWheel>", self.on_mousewheel)
    
    def create_status_section(self, parent):
        """Create the status bar section."""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        # Status label
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            padding=(5, 2)
        )
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Cache info button
        cache_btn = ttk.Button(
            status_frame,
            text="Cache Info",
            command=self.show_cache_info,
            width=12
        )
        cache_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Clear cache button
        clear_cache_btn = ttk.Button(
            status_frame,
            text="Clear Cache",
            command=self.clear_all_caches,
            width=12
        )
        clear_cache_btn.grid(row=0, column=2, padx=(5, 0))
    
    def set_default_values(self):
        """Set default values for form fields."""
        # Set default coordinates (New York City)
        self.lat_entry.insert(0, "40.7128")
        self.lng_entry.insert(0, "-74.0060")
        
        # Set default address
        self.address_entry.insert(0, "Times Square, New York, NY")
    
    def on_location_type_change(self):
        """Handle location type radio button change."""
        if self.location_type.get() == "coordinates":
            self.coord_frame.grid()
            self.address_frame.grid_remove()
        else:
            self.coord_frame.grid_remove()
            self.address_frame.grid()
    
    def update_radius_label(self, value):
        """Update radius label when scale changes."""
        radius_m = int(float(value))
        if radius_m >= 1000:
            self.radius_label.configure(text=f"{radius_m/1000:.1f}km")
        else:
            self.radius_label.configure(text=f"{radius_m}m")
    
    def update_reviews_label(self, value):
        """Update reviews label when scale changes."""
        self.reviews_label.configure(text=str(int(float(value))))
    
    def update_results_label(self, value):
        """Update results label when scale changes."""
        self.results_label.configure(text=str(int(float(value))))
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling in results."""
        if self.results_canvas:
            self.results_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def search_restaurants(self):
        """Search for restaurants based on current parameters."""
        try:
            self.status_var.set("Searching for restaurants...")
            self.root.update()
            
            # Clear previous results
            self.clear_results()
            
            # Get coordinates
            latitude, longitude = self.get_coordinates()
            if latitude is None or longitude is None:
                return
            
            # Get search parameters
            radius = int(self.radius_var.get())
            min_reviews = int(self.min_reviews_var.get())
            max_results = int(self.max_results_var.get())
            
            # Search for restaurants
            logger.info(f"Searching restaurants at {latitude}, {longitude}")
            restaurants = restaurant_service.find_restaurants(
                latitude=latitude,
                longitude=longitude,
                radius=radius,
                min_reviews=min_reviews,
                max_results=max_results
            )
            
            if not restaurants:
                self.status_var.set("No restaurants found matching criteria")
                messagebox.showinfo("No Results", "No restaurants found matching your criteria. Try adjusting the search parameters.")
                return
            
            # Display results
            self.display_restaurants(restaurants)
            self.current_restaurants = restaurants
            
            self.status_var.set(f"Found {len(restaurants)} restaurants")
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            self.status_var.set("Search failed")
            messagebox.showerror("Search Error", f"An error occurred while searching: {str(e)}")
    
    def get_coordinates(self) -> tuple[Optional[float], Optional[float]]:
        """Get coordinates from current input method."""
        try:
            if self.location_type.get() == "coordinates":
                # Get from coordinate inputs
                lat_str = self.lat_entry.get().strip()
                lng_str = self.lng_entry.get().strip()
                
                if not lat_str or not lng_str:
                    messagebox.showerror("Input Error", "Please enter both latitude and longitude")
                    return None, None
                
                latitude = float(lat_str)
                longitude = float(lng_str)
                
                if not restaurant_service.validate_coordinates(latitude, longitude):
                    messagebox.showerror("Input Error", "Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180")
                    return None, None
                
                return latitude, longitude
                
            else:
                # Get from address
                address = self.address_entry.get().strip()
                
                if not address:
                    messagebox.showerror("Input Error", "Please enter an address")
                    return None, None
                
                self.status_var.set("Converting address to coordinates...")
                self.root.update()
                
                coordinates = restaurant_service.geocode_address(address)
                
                if coordinates is None:
                    messagebox.showerror("Geocoding Error", "Could not find coordinates for the specified address")
                    return None, None
                
                return coordinates
                
        except ValueError:
            messagebox.showerror("Input Error", "Invalid coordinate values. Please enter numeric values.")
            return None, None
        except Exception as e:
            logger.error(f"Coordinate conversion error: {e}")
            messagebox.showerror("Error", f"Error getting coordinates: {str(e)}")
            return None, None
    
    def clear_results(self):
        """Clear the results display."""
        for widget in self.results_inner_frame.winfo_children():
            widget.destroy()
        
        self.current_restaurants = []
        self.results_canvas.yview_moveto(0)  # Scroll to top
    
    def display_restaurants(self, restaurants: List[Dict[str, Any]]):
        """Display the list of restaurants."""
        for i, restaurant in enumerate(restaurants):
            self.create_restaurant_item(restaurant, i)
    
    def create_restaurant_item(self, restaurant: Dict[str, Any], index: int):
        """Create a single restaurant item widget."""
        # Create main item frame
        item_frame = ttk.Frame(self.results_inner_frame, relief=tk.RAISED, borderwidth=1)
        item_frame.grid(row=index, column=0, sticky=(tk.W, tk.E), pady=2, padx=2)
        item_frame.columnconfigure(0, weight=1)
        
        # Restaurant info frame
        info_frame = ttk.Frame(item_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=8)
        info_frame.columnconfigure(0, weight=1)
        
        # Restaurant name and rating (first row)
        name_frame = ttk.Frame(info_frame)
        name_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        name_frame.columnconfigure(0, weight=1)
        
        name_label = ttk.Label(
            name_frame,
            text=restaurant.get('display_name', 'Unknown'),
            font=('TkDefaultFont', 11, 'bold')
        )
        name_label.grid(row=0, column=0, sticky=tk.W)
        
        rating_label = ttk.Label(
            name_frame,
            text=f"{restaurant.get('display_rating', 'No rating')} {restaurant.get('display_reviews', '')}",
            foreground='gray'
        )
        rating_label.grid(row=0, column=1, sticky=tk.E)
        
        # Address and distance (second row)
        details_frame = ttk.Frame(info_frame)
        details_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(3, 0))
        details_frame.columnconfigure(0, weight=1)
        
        address_label = ttk.Label(
            details_frame,
            text=restaurant.get('vicinity', 'Address not available'),
            foreground='gray',
            font=('TkDefaultFont', 9)
        )
        address_label.grid(row=0, column=0, sticky=tk.W)
        
        distance_text = f"{restaurant.get('distance_text', 'Unknown distance')}"
        if restaurant.get('walking_time'):
            distance_text += f" • {restaurant.get('walking_time')} walk"
        
        distance_label = ttk.Label(
            details_frame,
            text=distance_text,
            foreground='blue',
            font=('TkDefaultFont', 9)
        )
        distance_label.grid(row=0, column=1, sticky=tk.E)
        
        # Additional info (third row)
        if restaurant.get('price_text') or restaurant.get('is_open_now') is not None:
            extra_frame = ttk.Frame(info_frame)
            extra_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(2, 0))
            
            extra_info = []
            if restaurant.get('price_text') and restaurant.get('price_text') != 'Price not available':
                extra_info.append(restaurant.get('price_text'))
            
            if restaurant.get('is_open_now') is not None:
                status = "Open now" if restaurant.get('is_open_now') else "Closed"
                color = 'green' if restaurant.get('is_open_now') else 'red'
                extra_info.append(status)
            
            if extra_info:
                extra_label = ttk.Label(
                    extra_frame,
                    text=" • ".join(extra_info),
                    foreground='dark green' if restaurant.get('is_open_now') else 'gray',
                    font=('TkDefaultFont', 9)
                )
                extra_label.grid(row=0, column=0, sticky=tk.W)
        
        # More Info button
        more_info_btn = ttk.Button(
            item_frame,
            text="More Info",
            command=lambda r=restaurant: self.show_restaurant_details(r),
            width=12
        )
        more_info_btn.grid(row=0, column=1, padx=(5, 10), pady=8)
        
        # Configure grid weights for the results frame
        self.results_inner_frame.columnconfigure(0, weight=1)
    
    def show_restaurant_details(self, restaurant: Dict[str, Any]):
        """Show detailed analysis for a restaurant."""
        try:
            # Create and show detail view
            detail_view = RestaurantDetailView(self.root, restaurant)
            
        except Exception as e:
            logger.error(f"Error showing restaurant details: {e}")
            messagebox.showerror(
                "Detail View Error",
                f"Could not open restaurant details: {str(e)}"
            )
    
    def show_cache_info(self):
        """Show cache information dialog."""
        try:
            from restaurant_analyzer import restaurant_analyzer
            cache_status = restaurant_analyzer.get_cache_status()
            
            info_text = "CACHE STATUS\n" + "="*30 + "\n\n"
            
            # Review cache info
            review_info = cache_status.get('reviews', {})
            info_text += f"REVIEW CACHE:\n"
            info_text += f"Places cached: {review_info.get('total_places_cached', 0)}\n"
            info_text += f"Total reviews: {review_info.get('total_reviews_cached', 0)}\n"
            info_text += f"Expired entries: {review_info.get('expired_entries', 0)}\n\n"
            
            # Analysis cache info
            analysis_info = cache_status.get('analysis', {})
            info_text += f"ANALYSIS CACHE:\n"
            info_text += f"Analyses cached: {analysis_info.get('total_analyses_cached', 0)}\n"
            info_text += f"Expired entries: {analysis_info.get('expired_entries', 0)}\n\n"
            
            # Current status
            info_text += f"CURRENT STATUS:\n"
            info_text += f"Analysis in progress: {'Yes' if cache_status.get('is_analyzing', False) else 'No'}\n"
            info_text += f"Current analysis available: {'Yes' if cache_status.get('current_analysis_available', False) else 'No'}\n"
            
            # Show in dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Cache Information")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=50, height=15)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(1.0, info_text)
            text_widget.configure(state='disabled')
            
            close_btn = ttk.Button(dialog, text="Close", command=dialog.destroy)
            close_btn.pack(pady=(0, 10))
            
        except Exception as e:
            logger.error(f"Error showing cache info: {e}")
            messagebox.showerror("Cache Info Error", f"Could not retrieve cache information: {str(e)}")
    
    def clear_all_caches(self):
        """Clear all application caches."""
        try:
            result = messagebox.askyesno(
                "Clear Cache",
                "Are you sure you want to clear all cached data? This will remove stored reviews and analyses."
            )
            
            if result:
                from restaurant_analyzer import restaurant_analyzer
                clear_results = restaurant_analyzer.clear_all_caches()
                
                success_msg = []
                if clear_results.get('reviews_cleared', False):
                    success_msg.append("Review cache cleared")
                if clear_results.get('analysis_cleared', False):
                    success_msg.append("Analysis cache cleared")
                
                if success_msg:
                    messagebox.showinfo("Cache Cleared", "\n".join(success_msg))
                    self.status_var.set("Cache cleared successfully")
                else:
                    messagebox.showwarning("Cache Clear", "No cache data to clear or clearing failed")
                    
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            messagebox.showerror("Cache Error", f"Could not clear cache: {str(e)}")
    
    def cleanup(self):
        """Cleanup UI resources."""
        try:
            # Clear any ongoing operations
            self.clear_results()
            logger.info("UI cleanup completed")
        except Exception as e:
            logger.error(f"UI cleanup error: {e}")