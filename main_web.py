# main_web.py
"""
Main entry point for the AI Restaurant Recommender Web App
Launches the Flask web server with the modern UI
"""

import sys
import os
import webbrowser
import threading
import time

# Add the parent directory (project root) to sys.path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    
    try:
        import flask
    except ImportError:
        missing_deps.append('flask')
    
    try:
        import flask_cors
    except ImportError:
        missing_deps.append('flask-cors')
    
    try:
        import requests
    except ImportError:
        missing_deps.append('requests')
    
    if missing_deps:
        print("❌ Missing dependencies. Please install:")
        for dep in missing_deps:
            print(f"   pip install {dep}")
        print("\nOr install all at once:")
        print("   pip install flask flask-cors requests")
        return False
    
    return True

def check_config():
    """Check if config.py exists and has the required API key"""
    try:
        from config import GOOGLE_MAP_API_KEY
        if GOOGLE_MAP_API_KEY == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
            print("⚠️  Warning: Please update your Google Maps API key in config.py")
            print("   Get your API key from: https://console.cloud.google.com/")
            return False
        return True
    except ImportError:
        print("❌ config.py not found. Please create it with your Google Maps API key.")
        return False
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def open_browser(url, delay=1.5):
    """Open the web browser after a delay"""
    def delayed_open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"🌐 Opening browser at {url}")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print(f"Please manually open: {url}")
    
    thread = threading.Thread(target=delayed_open)
    thread.daemon = True
    thread.start()

def main():
    """Main application entry point"""
    print("🍽️ AI Restaurant Recommender - Web Edition")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check configuration
    if not check_config():
        print("\n🔧 Please configure your API key and try again.")
        return
    
    # Import and start web server
    try:
        from web_server import app
        
        print("✅ All dependencies found")
        print("✅ Configuration loaded")
        print("\n🚀 Starting web server...")
        print("📱 The app will open in your browser automatically")
        print("🛑 Press Ctrl+C to stop the server")
        print("\n" + "=" * 50)
        
        # Open browser after a short delay
        open_browser("http://localhost:5000")
        
        # Start the Flask app
        app.run(
            debug=False,  # Set to False for production-like experience
            host='0.0.0.0',
            port=5000,
            threaded=True,
            use_reloader=False  # Disable reloader to prevent browser opening twice
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all files are in the correct location")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()