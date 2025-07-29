"""
Detail View Window for displaying restaurant analysis results
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from typing import Dict, Any, Optional

from restaurant_analyzer import restaurant_analyzer
from config import DETAIL_WINDOW_WIDTH, DETAIL_WINDOW_HEIGHT

class RestaurantDetailView:
    def __init__(self, parent, restaurant_data: Dict[str, Any]):
        self.parent = parent
        self.restaurant_data = restaurant_data
        self.window = None
        self.progress_var = None
        self.status_var = None
        self.content_frame = None
        self.progress_frame = None
        self.is_analyzing = False
        
        self.create_window()
        self.start_analysis()
    
    def create_window(self):
        """Create the detail view window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"Restaurant Details - {self.restaurant_data.get('name', 'Unknown')}")
        self.window.geometry(f"{DETAIL_WINDOW_WIDTH}x{DETAIL_WINDOW_HEIGHT}")
        self.window.resizable(True, True)
        
        # Configure window
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center the window
        self.center_window()
        
        # Create main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Create header
        self.create_header(main_frame)
        
        # Create progress frame (initially visible)
        self.create_progress_frame(main_frame)
        
        # Create content frame (initially hidden)
        self.create_content_frame(main_frame)
        
        # Create buttons frame
        self.create_buttons_frame(main_frame)
    
    def center_window(self):
        """Center the window on screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_header(self, parent):
        """Create the header section."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        # Restaurant name
        name_label = ttk.Label(
            header_frame, 
            text=self.restaurant_data.get('name', 'Unknown Restaurant'),
            font=('TkDefaultFont', 14, 'bold')
        )
        name_label.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Basic info
        info_text = f"Rating: {self.restaurant_data.get('rating', 'N/A')}/5"
        if 'user_ratings_total' in self.restaurant_data:
            info_text += f" • {self.restaurant_data['user_ratings_total']} reviews"
        
        info_label = ttk.Label(header_frame, text=info_text)
        info_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Address
        if 'vicinity' in self.restaurant_data:
            address_label = ttk.Label(
                header_frame, 
                text=self.restaurant_data['vicinity'],
                foreground='gray'
            )
            address_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(2, 0))
    
    def create_progress_frame(self, parent):
        """Create the progress indicator frame."""
        self.progress_frame = ttk.Frame(parent)
        self.progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        self.progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(50, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Initializing analysis...")
        status_label = ttk.Label(self.progress_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, pady=(0, 10))
        
        # Cancel button
        cancel_btn = ttk.Button(
            self.progress_frame,
            text="Cancel",
            command=self.cancel_analysis
        )
        cancel_btn.grid(row=2, column=0, pady=10)
    
    def create_content_frame(self, parent):
        """Create the main content frame for analysis results."""
        self.content_frame = ttk.Frame(parent)
        # Don't grid it initially - will be shown when analysis completes
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(self.content_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Overview tab
        self.create_overview_tab(notebook)
        
        # Details tab
        self.create_details_tab(notebook)
        
        # Reviews tab
        self.create_reviews_tab(notebook)
    
    def create_overview_tab(self, notebook):
        """Create the overview tab."""
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="Overview")
        
        # Create scrollable content
        canvas = tk.Canvas(overview_frame)
        scrollbar = ttk.Scrollbar(overview_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        overview_frame.columnconfigure(0, weight=1)
        overview_frame.rowconfigure(0, weight=1)
        
        self.overview_content = scrollable_frame
    
    def create_details_tab(self, notebook):
        """Create the details tab."""
        details_frame = ttk.Frame(notebook)
        notebook.add(details_frame, text="Detailed Analysis")
        
        # Create scrollable text widget
        text_widget = scrolledtext.ScrolledText(
            details_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=('TkDefaultFont', 10)
        )
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        
        self.details_text = text_widget
    
    def create_reviews_tab(self, notebook):
        """Create the reviews summary tab."""
        reviews_frame = ttk.Frame(notebook)
        notebook.add(reviews_frame, text="Review Summary")
        
        # Create scrollable text widget
        text_widget = scrolledtext.ScrolledText(
            reviews_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=('TkDefaultFont', 10)
        )
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        reviews_frame.columnconfigure(0, weight=1)
        reviews_frame.rowconfigure(0, weight=1)
        
        self.reviews_text = text_widget
    
    def create_buttons_frame(self, parent):
        """Create the buttons frame."""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Export button
        export_btn = ttk.Button(
            buttons_frame,
            text="Export Report",
            command=self.export_report,
            state='disabled'
        )
        export_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(
            buttons_frame,
            text="Refresh Analysis",
            command=self.refresh_analysis,
            state='disabled'
        )
        refresh_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Close button
        close_btn = ttk.Button(
            buttons_frame,
            text="Close",
            command=self.close_window
        )
        close_btn.grid(row=0, column=2)
        
        # Store button references
        self.export_btn = export_btn
        self.refresh_btn = refresh_btn
    
    def start_analysis(self):
        """Start the restaurant analysis process."""
        place_id = self.restaurant_data.get('place_id')
        if not place_id:
            self.show_error("No place ID available for this restaurant")
            return
        
        restaurant_name = self.restaurant_data.get('name', '')
        
        self.is_analyzing = True
        
        # Start analysis in background thread
        restaurant_analyzer.analyze_restaurant_async(
            place_id=place_id,
            restaurant_name=restaurant_name,
            progress_callback=self.update_progress,
            completion_callback=self.analysis_complete,
            error_callback=self.analysis_error
        )
    
    def update_progress(self, message: str, progress: float):
        """Update progress indicator."""
        if self.window and self.window.winfo_exists():
            self.window.after(0, lambda: self._update_progress_ui(message, progress))
    
    def _update_progress_ui(self, message: str, progress: float):
        """Update progress UI in main thread."""
        if self.status_var:
            self.status_var.set(message)
        if self.progress_var:
            self.progress_var.set(progress)
    
    def analysis_complete(self, result: Dict[str, Any]):
        """Handle analysis completion."""
        if self.window and self.window.winfo_exists():
            self.window.after(0, lambda: self._show_analysis_results(result))
    
    def analysis_error(self, error_message: str):
        """Handle analysis error."""
        if self.window and self.window.winfo_exists():
            self.window.after(0, lambda: self.show_error(error_message))
    
    def _show_analysis_results(self, result: Dict[str, Any]):
        """Display analysis results in the UI."""
        self.is_analyzing = False
        
        # Hide progress frame
        self.progress_frame.grid_remove()
        
        # Show content frame
        self.content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Populate content
        self.populate_overview(result)
        self.populate_details(result)
        self.populate_reviews_summary(result)
        
        # Enable buttons
        self.export_btn.configure(state='normal')
        self.refresh_btn.configure(state='normal')
        
        # Store result for export
        self.analysis_result = result
    
    def populate_overview(self, result: Dict[str, Any]):
        """Populate the overview tab."""
        summary = restaurant_analyzer.get_analysis_summary(result)
        
        # Clear existing content
        for widget in self.overview_content.winfo_children():
            widget.destroy()
        
        row = 0
        
        # Basic Information
        self.add_section_header(self.overview_content, "Basic Information", row)
        row += 1
        
        self.add_info_row(self.overview_content, "Cuisine Type:", summary.get('cuisine_type', 'N/A'), row)
        row += 1
        self.add_info_row(self.overview_content, "Price Range:", summary.get('price_range', 'N/A'), row)
        row += 1
        self.add_info_row(self.overview_content, "Reviews Analyzed:", summary.get('total_reviews', 'N/A'), row)
        row += 1
        
        # Ambience
        self.add_section_header(self.overview_content, "Atmosphere", row)
        row += 1
        self.add_text_content(self.overview_content, summary.get('ambience', 'Not described'), row)
        row += 1
        
        # Highlights
        self.add_section_header(self.overview_content, "Customer Highlights", row, color='green')
        row += 1
        self.add_text_content(self.overview_content, summary.get('highlights', 'None mentioned'), row)
        row += 1
        
        # Complaints
        if summary.get('complaints', 'None mentioned') != 'None mentioned':
            self.add_section_header(self.overview_content, "Main Concerns", row, color='orange')
            row += 1
            self.add_text_content(self.overview_content, summary.get('complaints', 'None mentioned'), row)
            row += 1
        
        # Best Dishes
        if summary.get('best_dishes', 'Not mentioned') != 'Not mentioned':
            self.add_section_header(self.overview_content, "Recommended Dishes", row)
            row += 1
            self.add_text_content(self.overview_content, summary.get('best_dishes', 'Not mentioned'), row)
            row += 1
    
    def add_section_header(self, parent, text, row, color='black'):
        """Add a section header."""
        label = ttk.Label(
            parent,
            text=text,
            font=('TkDefaultFont', 11, 'bold'),
            foreground=color
        )
        label.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        parent.columnconfigure(0, weight=1)
    
    def add_info_row(self, parent, label_text, value_text, row):
        """Add an information row."""
        label = ttk.Label(parent, text=label_text, font=('TkDefaultFont', 10, 'bold'))
        label.grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        
        value = ttk.Label(parent, text=str(value_text))
        value.grid(row=row, column=1, sticky=(tk.W, tk.E))
        
        parent.columnconfigure(1, weight=1)
    
    def add_text_content(self, parent, text, row):
        """Add text content."""
        label = ttk.Label(
            parent,
            text=str(text),
            wraplength=600,
            justify=tk.LEFT
        )
        label.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    
    def populate_details(self, result: Dict[str, Any]):
        """Populate the details tab."""
        analysis = result.get('analysis', {})
        
        details_text = f"""RESTAURANT ANALYSIS REPORT
{'=' * 50}

Restaurant: {result.get('restaurant_name', 'Unknown')}
Analysis Date: {self.format_timestamp(result.get('timestamp', 0))}
Reviews Analyzed: {result.get('review_data', {}).get('total_reviews', 0)}
Overall Rating: {result.get('review_data', {}).get('overall_rating', 0):.1f}/5.0

CUISINE & ATMOSPHERE
{'-' * 30}
Cuisine Type: {analysis.get('cuisine_type', 'Not specified')}
Price Range: {analysis.get('price_range', 'Not mentioned')}

Ambience: {analysis.get('ambience', 'Not described')}

CUSTOMER HIGHLIGHTS
{'-' * 30}
"""
        
        highlights = analysis.get('highlights', [])
        if highlights:
            for i, highlight in enumerate(highlights, 1):
                details_text += f"{i}. {highlight}\n"
        else:
            details_text += "None mentioned\n"
        
        details_text += f"""
MAIN COMPLAINTS
{'-' * 30}
"""
        
        complaints = analysis.get('complaints', [])
        if complaints:
            for i, complaint in enumerate(complaints, 1):
                details_text += f"{i}. {complaint}\n"
        else:
            details_text += "None mentioned\n"
        
        details_text += f"""
RECOMMENDED DISHES
{'-' * 30}
{', '.join(analysis.get('best_dishes', [])) if analysis.get('best_dishes') else 'Not mentioned'}

SERVICE QUALITY
{'-' * 30}
{analysis.get('service_quality', 'Not mentioned')}

OVERALL SENTIMENT
{'-' * 30}
{analysis.get('overall_sentiment', 'Mixed')}

CACHE STATUS
{'-' * 30}
Analysis from cache: {'Yes' if result.get('analysis_from_cache', False) else 'No'}
Reviews from cache: {'Yes' if result.get('review_data', {}).get('from_cache', False) else 'No'}
"""
        
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details_text)
    
    def populate_reviews_summary(self, result: Dict[str, Any]):
        """Populate the reviews summary tab."""
        review_data = result.get('review_data', {})
        
        summary_text = f"""REVIEW SUMMARY
{'=' * 30}

Total Reviews Analyzed: {review_data.get('total_reviews', 0)}
Overall Rating: {review_data.get('overall_rating', 0):.1f}/5.0
Total Ratings (Google): {review_data.get('total_ratings', 0)}

DATA SOURCE
{'-' * 20}
Reviews from cache: {'Yes' if review_data.get('from_cache', False) else 'No'}
Analysis from cache: {'Yes' if result.get('analysis_from_cache', False) else 'No'}

ANALYSIS BREAKDOWN
{'-' * 20}
The analysis was performed using Google's Gemini AI to extract key insights from the most recent reviews. The AI analyzed review text to identify:

• Common themes and sentiments
• Frequently mentioned dishes and highlights  
• Service quality patterns
• Ambience descriptions
• Pricing indications
• Common complaints or concerns

This provides a comprehensive overview based on actual customer experiences shared in recent reviews.
"""
        
        self.reviews_text.delete(1.0, tk.END)
        self.reviews_text.insert(1.0, summary_text)
    
    def format_timestamp(self, timestamp):
        """Format timestamp for display."""
        import datetime
        try:
            dt = datetime.datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return 'Unknown'
    
    def show_error(self, error_message: str):
        """Show error message and close window."""
        self.is_analyzing = False
        messagebox.showerror("Analysis Error", error_message)
        self.close_window()
    
    def cancel_analysis(self):
        """Cancel ongoing analysis."""
        self.is_analyzing = False
        self.close_window()
    
    def export_report(self):
        """Export the analysis report."""
        if not hasattr(self, 'analysis_result'):
            messagebox.showwarning("Export Error", "No analysis data to export")
            return
        
        from tkinter import filedialog
        
        # Ask user for file location
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Analysis Report"
        )
        
        if filename:
            try:
                format_type = 'json' if filename.lower().endswith('.json') else 'text'
                exported_data = restaurant_analyzer.export_analysis(self.analysis_result, format_type)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(exported_data)
                
                messagebox.showinfo("Export Success", f"Report exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
    
    def refresh_analysis(self):
        """Refresh the analysis with new data."""
        # Clear caches and restart analysis
        restaurant_analyzer.clear_all_caches()
        
        # Hide content and show progress
        self.content_frame.grid_remove()
        self.progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Refreshing analysis...")
        
        # Disable buttons
        self.export_btn.configure(state='disabled')
        self.refresh_btn.configure(state='disabled')
        
        # Start new analysis
        self.start_analysis()
    
    def close_window(self):
        """Close the detail window."""
        if self.window:
            self.window.destroy()