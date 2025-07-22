"""
Enhanced UI with AI-powered restaurant analysis display
Updated version of ui.py with Gemini integration
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List, Callable

class RestaurantUI:
    """
    Enhanced restaurant UI with AI analysis display
    """
    
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.setup_styles()
        
        # Callback for restaurant search (will be set by main.py)
        self.search_callback: Callable = None
    
    def setup_styles(self):
        """Define colors and styles"""
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db', 
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'ai_bg': '#f8f9fa',
            'ai_border': '#dee2e6'
        }
    
    def setup_ui(self):
        """Setup the main UI components"""
        self.root.title("AI-Powered Restaurant Recommender")
        self.root.geometry("900x700")
        self.root.configure(bg=self.colors['light'])
        
        # Create main container
        main_frame = tk.Frame(self.root, bg=self.colors['light'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🍽️ AI Restaurant Recommender", 
                              font=('Arial', 18, 'bold'), bg=self.colors['light'], 
                              fg=self.colors['primary'])
        title_label.pack(pady=(0, 20))
        
        # Search section
        self.create_search_section(main_frame)
        
        # Results section
        self.create_results_section(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_search_section(self, parent):
        """Create the search input section"""
        search_frame = tk.LabelFrame(parent, text="Search Settings", font=('Arial', 12, 'bold'),
                                   bg=self.colors['light'], fg=self.colors['primary'])
        search_frame.pack(fill='x', pady=(0, 20))
        
        # Location selection frame
        location_frame = tk.Frame(search_frame, bg=self.colors['light'])
        location_frame.pack(fill='x', padx=10, pady=10)
        
        # Location type selection
        self.location_type = tk.StringVar(value="coordinates")
        
        coord_radio = tk.Radiobutton(location_frame, text="Use Coordinates", 
                                   variable=self.location_type, value="coordinates",
                                   bg=self.colors['light'], font=('Arial', 10))
        coord_radio.pack(side='left', padx=(0, 20))
        
        address_radio = tk.Radiobutton(location_frame, text="Use Address",
                                     variable=self.location_type, value="address", 
                                     bg=self.colors['light'], font=('Arial', 10))
        address_radio.pack(side='left')
        
        # Coordinates input
        coord_frame = tk.Frame(search_frame, bg=self.colors['light'])
        coord_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(coord_frame, text="Latitude:", bg=self.colors['light'], 
                font=('Arial', 10)).pack(side='left')
        self.lat_entry = tk.Entry(coord_frame, width=15, font=('Arial', 10))
        self.lat_entry.pack(side='left', padx=(5, 20))
        
        tk.Label(coord_frame, text="Longitude:", bg=self.colors['light'], 
                font=('Arial', 10)).pack(side='left')
        self.lng_entry = tk.Entry(coord_frame, width=15, font=('Arial', 10))
        self.lng_entry.pack(side='left', padx=5)
        
        # Address input
        address_frame = tk.Frame(search_frame, bg=self.colors['light'])
        address_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(address_frame, text="Address:", bg=self.colors['light'], 
                font=('Arial', 10)).pack(side='left')
        self.address_entry = tk.Entry(address_frame, width=50, font=('Arial', 10))
        self.address_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        # Search parameters
        params_frame = tk.Frame(search_frame, bg=self.colors['light'])
        params_frame.pack(fill='x', padx=10, pady=10)
        
        # Radius
        tk.Label(params_frame, text="Radius (m):", bg=self.colors['light'], 
                font=('Arial', 10)).pack(side='left')
        self.radius_var = tk.IntVar(value=1000)
        radius_scale = tk.Scale(params_frame, from_=100, to=5000, orient='horizontal',
                              variable=self.radius_var, length=150, bg=self.colors['light'])
        radius_scale.pack(side='left', padx=5)
        
        # Min reviews
        tk.Label(params_frame, text="Min Reviews:", bg=self.colors['light'], 
                font=('Arial', 10)).pack(side='left', padx=(20, 0))
        self.min_reviews_var = tk.IntVar(value=100)
        reviews_scale = tk.Scale(params_frame, from_=10, to=500, orient='horizontal',
                               variable=self.min_reviews_var, length=150, bg=self.colors['light'])
        reviews_scale.pack(side='left', padx=5)
        
        # Max results
        tk.Label(params_frame, text="Max Results:", bg=self.colors['light'], 
                font=('Arial', 10)).pack(side='left', padx=(20, 0))
        self.max_results_var = tk.IntVar(value=5)
        results_scale = tk.Scale(params_frame, from_=1, to=10, orient='horizontal',
                               variable=self.max_results_var, length=100, bg=self.colors['light'])
        results_scale.pack(side='left', padx=5)
        
        # Search button and AI status
        button_frame = tk.Frame(search_frame, bg=self.colors['light'])
        button_frame.pack(fill='x', padx=10, pady=10)
        
        self.search_button = tk.Button(button_frame, text="🔍 Search Restaurants", 
                                     command=self.perform_search, font=('Arial', 12, 'bold'),
                                     bg=self.colors['secondary'], fg='white', padx=20, pady=5)
        self.search_button.pack(side='left')
        
        # AI status indicator (NEW)
        self.ai_status_label = tk.Label(button_frame, text="🤖 AI: Ready", 
                                       font=('Arial', 10), bg=self.colors['light'], 
                                       fg=self.colors['success'])
        self.ai_status_label.pack(side='right')
        
        # Set default coordinates
        self.set_default_coordinates()
    
    def set_default_coordinates(self):
        """Set default coordinates (New York City)"""
        self.lat_entry.delete(0, tk.END)
        self.lng_entry.delete(0, tk.END)
        self.lat_entry.insert(0, "40.7128")
        self.lng_entry.insert(0, "-74.0060")
    
    def create_results_section(self, parent):
        """Create the results display section"""
        results_label_frame = tk.LabelFrame(parent, text="Restaurant Results", 
                                          font=('Arial', 12, 'bold'),
                                          bg=self.colors['light'], fg=self.colors['primary'])
        results_label_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create scrollable frame for results
        self.create_scrollable_results(results_label_frame)
    
    def create_scrollable_results(self, parent):
        """Create scrollable results area"""
        # Canvas and scrollbar for scrolling
        canvas = tk.Canvas(parent, bg='white')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.results_frame = tk.Frame(canvas, bg='white')
        
        self.results_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.results_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Store canvas reference for updating scroll region
        self.canvas = canvas
        
        # Initial message
        initial_label = tk.Label(self.results_frame, text="Enter search criteria and click 'Search Restaurants' to begin",
                               font=('Arial', 12), fg=self.colors['primary'], bg='white')
        initial_label.pack(pady=50)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_frame = tk.Frame(parent, bg=self.colors['primary'], height=30)
        self.status_frame.pack(fill='x', side='bottom')
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="Ready", 
                                   bg=self.colors['primary'], fg='white', 
                                   font=('Arial', 10))
        self.status_label.pack(side='left', padx=10, pady=5)
    
    def perform_search(self):
        """Perform restaurant search"""
        try:
            if self.location_type.get() == "coordinates":
                # Get coordinates
                lat = float(self.lat_entry.get())
                lng = float(self.lng_entry.get())
                location_data = {'type': 'coordinates', 'lat': lat, 'lng': lng}
            else:
                # Get address
                address = self.address_entry.get().strip()
                if not address:
                    messagebox.showerror("Error", "Please enter an address")
                    return
                location_data = {'type': 'address', 'address': address}
            
            # Get search parameters
            radius = self.radius_var.get()
            min_reviews = self.min_reviews_var.get()
            max_results = self.max_results_var.get()
            
            # Update UI state
            self.search_button.config(state='disabled', text="🔍 Searching...")
            self.update_ai_status("Searching...", self.colors['warning'])
            self.show_status("Searching for restaurants...")
            
            # Call search callback if set
            if self.search_callback:
                self.search_callback(location_data, radius, min_reviews, max_results)
            else:
                messagebox.showerror("Error", "Search functionality not connected")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid coordinates")
        except Exception as e:
            messagebox.showerror("Error", f"Search error: {e}")
        finally:
            self.search_button.config(state='normal', text="🔍 Search Restaurants")
    
    def display_restaurants(self, restaurants: List[Dict]):
        """Display restaurants with AI analysis"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if not restaurants:
            self.show_no_results()
            return
        
        self.show_status(f"Found {len(restaurants)} restaurants")
        
        row = 0
        for i, restaurant in enumerate(restaurants):
            # Basic restaurant info
            row = self._display_restaurant_info(restaurant, row)
            
            # AI analysis (NEW)
            if restaurant.get('ai_summary') and restaurant.get('analysis_status') == 'completed':
                row = self._display_ai_analysis(restaurant, row)
            elif restaurant.get('analysis_status') == 'analyzing':
                row = self._display_ai_loading(restaurant, row)
            elif restaurant.get('analysis_status') in ['failed', 'error']:
                row = self._display_ai_error(restaurant, row)
            
            # Separator
            if i < len(restaurants) - 1:
                row = self._add_separator(row)
        
        # Update scroll region
        self.results_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Update AI status
        ai_completed = sum(1 for r in restaurants if r.get('analysis_status') == 'completed')
        if ai_completed > 0:
            self.update_ai_status(f"Analyzed {ai_completed} restaurants", self.colors['success'])
        else:
            self.update_ai_status("Ready", self.colors['success'])
    
    def _display_restaurant_info(self, restaurant: Dict, row: int) -> int:
        """Display basic restaurant information"""
        # Restaurant name and rating frame
        info_frame = tk.Frame(self.results_frame, bg='white', padx=10, pady=10)
        info_frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Configure grid weight
        self.results_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Restaurant name
        name_label = tk.Label(info_frame, text=restaurant['name'], 
                             font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary'])
        name_label.grid(row=0, column=0, sticky='w')
        
        # Rating
        rating_text = f"⭐ {restaurant['rating']}/5 ({restaurant['user_ratings_total']} reviews)"
        rating_label = tk.Label(info_frame, text=rating_text,
                               font=('Arial', 11), bg='white', fg=self.colors['secondary'])
        rating_label.grid(row=0, column=1, sticky='e')
        
        # Address
        address_label = tk.Label(info_frame, text=f"📍 {restaurant['vicinity']}", 
                                font=('Arial', 10), bg='white', fg='#666')
        address_label.grid(row=1, column=0, sticky='w', pady=(2,0))
        
        # Distance and duration
        distance_text = f"🚶 {restaurant.get('distance', 'Unknown')} ({restaurant.get('duration', 'Unknown')})"
        distance_label = tk.Label(info_frame, text=distance_text,
                                 font=('Arial', 10), bg='white', fg='#666')
        distance_label.grid(row=1, column=1, sticky='e', pady=(2,0))
        
        # Price level (if available)
        if restaurant.get('price_level'):
            price_text = "💰" * restaurant['price_level']
            price_label = tk.Label(info_frame, text=price_text,
                                  font=('Arial', 10), bg='white')
            price_label.grid(row=2, column=0, sticky='w', pady=(2,0))
        
        return row + 1
    
    def _display_ai_analysis(self, restaurant: Dict, row: int) -> int:
        """Display AI analysis (NEW)"""
        ai_data = restaurant['ai_summary']
        
        # AI analysis frame
        ai_frame = tk.Frame(self.results_frame, bg=self.colors['ai_bg'], 
                           relief='ridge', bd=1, padx=15, pady=10)
        ai_frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=(0,5))
        ai_frame.grid_columnconfigure(0, weight=1)
        
        # AI header
        header_frame = tk.Frame(ai_frame, bg=self.colors['ai_bg'])
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0,8))
        header_frame.grid_columnconfigure(0, weight=1)
        
        ai_title = tk.Label(header_frame, text="🤖 AI Review Analysis", 
                           font=('Arial', 11, 'bold'), bg=self.colors['ai_bg'], 
                           fg=self.colors['secondary'])
        ai_title.grid(row=0, column=0, sticky='w')
        
        # Confidence and sentiment
        confidence = ai_data.get('confidence', 0)
        sentiment = ai_data.get('sentiment', 'unknown').title()
        
        confidence_color = self.colors['success'] if confidence > 0.7 else self.colors['warning']
        status_text = f"{sentiment} • {confidence:.0%} confidence"
        status_label = tk.Label(header_frame, text=status_text,
                               font=('Arial', 9, 'bold'), bg=self.colors['ai_bg'],
                               fg=confidence_color)
        status_label.grid(row=0, column=1, sticky='e')
        
        # Summary
        summary_label = tk.Label(ai_frame, text=ai_data['summary'], 
                                font=('Arial', 10), bg=self.colors['ai_bg'], 
                                fg=self.colors['primary'], wraplength=600, justify='left')
        summary_label.grid(row=1, column=0, sticky='ew', pady=(0,8))
        
        # Highlights
        if ai_data.get('highlights'):
            highlights_text = "✅ " + " • ".join(ai_data['highlights'][:2])
            highlights_label = tk.Label(ai_frame, text=highlights_text,
                                       font=('Arial', 9), bg=self.colors['ai_bg'],
                                       fg=self.colors['success'], wraplength=600, 
                                       justify='left')
            highlights_label.grid(row=2, column=0, sticky='ew', pady=(0,4))
        
        # Criticisms
        if ai_data.get('criticisms'):
            criticisms_text = "⚠️ " + " • ".join(ai_data['criticisms'][:1])
            criticisms_label = tk.Label(ai_frame, text=criticisms_text,
                                       font=('Arial', 9), bg=self.colors['ai_bg'],
                                       fg=self.colors['danger'], wraplength=600,
                                       justify='left')
            criticisms_label.grid(row=3, column=0, sticky='ew')
        
        # Detailed analysis button
        detail_button = tk.Button(ai_frame, text="View Detailed Analysis", 
                                 command=lambda: self.show_detailed_analysis(restaurant),
                                 font=('Arial', 8), bg=self.colors['secondary'], 
                                 fg='white', padx=10, pady=2)
        detail_button.grid(row=4, column=0, sticky='w', pady=(8,0))
        
        return row + 1
    
    def _display_ai_loading(self, restaurant: Dict, row: int) -> int:
        """Display AI analysis loading state (NEW)"""
        loading_frame = tk.Frame(self.results_frame, bg='#fff3cd', relief='solid', bd=1, pady=8)
        loading_frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=2)
        
        loading_label = tk.Label(loading_frame, text="🤖 Analyzing reviews... This may take a moment.",
                                font=('Arial', 10, 'italic'), bg='#fff3cd', fg='#856404')
        loading_label.pack()
        
        return row + 1
    
    def _display_ai_error(self, restaurant: Dict, row: int) -> int:
        """Display AI analysis error state (NEW)"""
        error_frame = tk.Frame(self.results_frame, bg='#f8d7da', relief='solid', bd=1, pady=6)
        error_frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=2)
        
        error_label = tk.Label(error_frame, text="🤖 AI analysis unavailable for this restaurant",
                              font=('Arial', 9, 'italic'), bg='#f8d7da', fg='#721c24')
        error_label.pack()
        
        return row + 1
    
    def _add_separator(self, row: int) -> int:
        """Add separator between restaurants"""
        separator = tk.Frame(self.results_frame, height=2, bg='#dee2e6')
        separator.grid(row=row, column=0, columnspan=2, sticky='ew', pady=10, padx=20)
        return row + 1
    
    def show_detailed_analysis(self, restaurant: Dict):
        """Show detailed AI analysis in popup (NEW)"""
        if not restaurant.get('ai_summary'):
            messagebox.showinfo("No Analysis", "No detailed analysis available.")
            return
        
        # Create popup window
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Detailed Analysis - {restaurant['name']}")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry(f"+{self.root.winfo_rootx() + 100}+{self.root.winfo_rooty() + 100}")
        
        # Scrolled text widget
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, padx=15, pady=15, 
                                               font=('Arial', 11))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Format detailed analysis
        ai_data = restaurant['ai_summary']
        analysis_text = f"""🍽️ {restaurant['name']}
{'=' * 60}

📊 OVERVIEW
Rating: {restaurant['rating']}/5 stars ({restaurant['user_ratings_total']} reviews)
Distance: {restaurant.get('distance', 'Unknown')}
AI Confidence: {ai_data.get('confidence', 0):.0%}
Overall Sentiment: {ai_data.get('sentiment', 'Unknown').title()}

📝 DETAILED SUMMARY
{ai_data.get('summary', 'No summary available')}

✅ CUSTOMER HIGHLIGHTS"""
        
        for highlight in ai_data.get('highlights', []):
            analysis_text += f"\n• {highlight}"
        
        if ai_data.get('criticisms'):
            analysis_text += f"\n\n⚠️ AREAS FOR IMPROVEMENT"
            for criticism in ai_data.get('criticisms', []):
                analysis_text += f"\n• {criticism}"
        
        analysis_text += f"\n\n🤖 This analysis was generated using AI based on customer reviews from Google Maps."
        
        text_widget.insert('1.0', analysis_text)
        text_widget.config(state='disabled')
        
        # Close button
        tk.Button(dialog, text="Close", command=dialog.destroy,
                 bg=self.colors['secondary'], fg='white', padx=20, pady=8, 
                 font=('Arial', 10)).pack(pady=10)
    
    def show_no_results(self):
        """Display no results message"""
        no_results_label = tk.Label(self.results_frame, 
                                   text="No restaurants found.\n\nTry:\n• Increasing search radius\n• Reducing minimum reviews\n• Checking your location",
                                   font=('Arial', 12), fg=self.colors['primary'], bg='white',
                                   justify='center')
        no_results_label.pack(pady=50)
    
    def show_status(self, message: str, color: str = 'white'):
        """Update status bar"""
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()
    
    def update_ai_status(self, status: str, color: str = None):
        """Update AI status indicator (NEW)"""
        color = color or self.colors['success']
        self.ai_status_label.config(text=f"🤖 AI: {status}", fg=color)
    
    def set_search_callback(self, callback: Callable):
        """Set the search callback function"""
        self.search_callback = callback


# Test the UI
if __name__ == "__main__":
    root = tk.Tk()
    ui = RestaurantUI(root)
    
    # Sample data for testing
    sample_restaurants = [
        {
            'name': 'Sample Italian Restaurant',
            'rating': 4.5,
            'user_ratings_total': 234,
            'vicinity': '123 Main St, Downtown',
            'distance': '0.3 km',
            'duration': '4 mins',
            'price_level': 2,
            'ai_summary': {
                'summary': 'Authentic Italian restaurant known for excellent pasta and warm atmosphere. Most customers praise the homemade sauces and attentive service.',
                'highlights': ['Exceptional pasta dishes', 'Friendly service', 'Cozy atmosphere'],
                'criticisms': ['Can be noisy during peak hours', 'Limited parking'],
                'sentiment': 'positive',
                'confidence': 0.87
            },
            'analysis_status': 'completed'
        }
    ]
    
    # Display sample data
    ui.display_restaurants(sample_restaurants)
    
    root.mainloop()