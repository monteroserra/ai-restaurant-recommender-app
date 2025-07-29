"""
Main application entry point for Restaurant Recommender with AI Analysis
"""
import tkinter as tk
from tkinter import messagebox
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('restaurant_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required modules are available."""
    required_modules = [
        'requests',
        'tkinter'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"Missing required modules: {', '.join(missing_modules)}\n"
        error_msg += "Please install them using: pip install " + " ".join(missing_modules)
        print(error_msg)
        return False
    
    return True

def validate_configuration():
    """Validate application configuration."""
    try:
        from config import validate_config
        config_status = validate_config()
        
        if not config_status['valid']:
            error_msg = "Configuration Issues:\n" + "\n".join(config_status['issues'])
            error_msg += "\n\nPlease check your config.py file and ensure API keys are set."
            
            # Show error in GUI if possible
            try:
                root = tk.Tk()
                root.withdraw()  # Hide main window
                messagebox.showerror("Configuration Error", error_msg)
                root.destroy()
            except:
                print(error_msg)
            
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False

def create_cache_directory():
    """Create cache directory if it doesn't exist."""
    try:
        from config import CACHE_DIR
        os.makedirs(CACHE_DIR, exist_ok=True)
        logger.info(f"Cache directory ready: {CACHE_DIR}")
    except Exception as e:
        logger.warning(f"Could not create cache directory: {e}")

class RestaurantApp:
    def __init__(self):
        self.root = None
        self.ui = None
    
    def initialize(self):
        """Initialize the application."""
        logger.info("Initializing Restaurant Recommender Application")
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("AI Restaurant Recommender")
        
        # Set window properties
        from config import WINDOW_WIDTH, WINDOW_HEIGHT
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(600, 500)
        
        # Center window on screen
        self.center_window()
        
        # Set window icon (if available)
        try:
            # You can add an icon file here
            # self.root.iconbitmap("icon.ico")
            pass
        except:
            pass
        
        # Configure window close behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize UI
        from ui import RestaurantUI
        self.ui = RestaurantUI(self.root)
        
        logger.info("Application initialized successfully")
    
    def center_window(self):
        """Center the main window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def run(self):
        """Run the application main loop."""
        if not self.root:
            raise RuntimeError("Application not initialized. Call initialize() first.")
        
        try:
            logger.info("Starting application main loop")
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
            messagebox.showerror("Application Error", f"An unexpected error occurred: {e}")
        finally:
            logger.info("Application shutting down")
    
    def on_closing(self):
        """Handle application closing."""
        try:
            # Cleanup operations
            if self.ui:
                self.ui.cleanup()
            
            # Clear any ongoing operations
            from restaurant_analyzer import restaurant_analyzer
            if restaurant_analyzer.is_analyzing:
                result = messagebox.askquestion(
                    "Analysis in Progress",
                    "An analysis is currently running. Do you want to exit anyway?",
                    icon='warning'
                )
                if result != 'yes':
                    return
            
            logger.info("Application closed by user")
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.root.destroy()

def main():
    """Main application entry point."""
    print("Starting AI Restaurant Recommender...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Validate configuration
    if not validate_configuration():
        sys.exit(1)
    
    # Create cache directory
    create_cache_directory()
    
    # Create and run application
    try:
        app = RestaurantApp()
        app.initialize()
        app.run()
        
    except Exception as e:
        logger.error(f"Fatal application error: {e}")
        try:
            messagebox.showerror(
                "Fatal Error",
                f"The application encountered a fatal error and must close:\n\n{e}"
            )
        except:
            print(f"Fatal Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()