"""
Flask Web Application for AI Restaurant Recommender
"""
import os
import json
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from threading import Thread
import time

# Import our services
from restaurant_service import restaurant_service
from restaurant_analyzer import restaurant_analyzer
from config import (
    WEB_HOST, WEB_PORT, WEB_DEBUG, validate_config,
    DEFAULT_RADIUS, DEFAULT_MIN_REVIEWS, DEFAULT_MAX_RESULTS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Store for ongoing analyses
ongoing_analyses = {}

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/search_restaurants', methods=['POST'])
def search_restaurants():
    """Search for restaurants API endpoint."""
    try:
        data = request.get_json()
        
        # Extract parameters
        location_type = data.get('location_type', 'coordinates')
        radius = int(data.get('radius', DEFAULT_RADIUS))
        min_reviews = int(data.get('min_reviews', DEFAULT_MIN_REVIEWS))
        max_results = int(data.get('max_results', DEFAULT_MAX_RESULTS))
        
        # Get coordinates
        if location_type == 'coordinates':
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
        else:
            address = data.get('address', '')
            if not address:
                return jsonify({'success': False, 'error': 'Address is required'})
            
            coordinates = restaurant_service.geocode_address(address)
            if not coordinates:
                return jsonify({'success': False, 'error': 'Could not geocode address'})
            
            latitude, longitude = coordinates
        
        # Validate coordinates
        if not restaurant_service.validate_coordinates(latitude, longitude):
            return jsonify({'success': False, 'error': 'Invalid coordinates'})
        
        # Search for restaurants
        restaurants = restaurant_service.find_restaurants(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            min_reviews=min_reviews,
            max_results=max_results
        )
        
        if not restaurants:
            return jsonify({
                'success': False,
                'error': 'No restaurants found matching criteria'
            })
        
        return jsonify({
            'success': True,
            'restaurants': restaurants,
            'count': len(restaurants),
            'search_location': {'latitude': latitude, 'longitude': longitude}
        })
        
    except Exception as e:
        logger.error(f"Restaurant search error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/analyze_restaurant', methods=['POST'])
def analyze_restaurant():
    """Start restaurant analysis."""
    try:
        data = request.get_json()
        place_id = data.get('place_id')
        restaurant_name = data.get('restaurant_name', '')
        max_reviews = int(data.get('max_reviews', 200))
        
        if not place_id:
            return jsonify({'success': False, 'error': 'Place ID is required'})
        
        # Check if analysis is already running for this restaurant
        if place_id in ongoing_analyses:
            return jsonify({
                'success': False,
                'error': 'Analysis already in progress for this restaurant'
            })
        
        # Generate analysis ID
        analysis_id = f"{place_id}_{int(time.time())}"
        
        # Store analysis status
        ongoing_analyses[analysis_id] = {
            'place_id': place_id,
            'restaurant_name': restaurant_name,
            'status': 'starting',
            'progress': 0,
            'message': 'Initializing analysis...',
            'result': None,
            'error': None
        }
        
        # Start analysis in background thread
        def run_analysis():
            try:
                def progress_callback(message, progress):
                    if analysis_id in ongoing_analyses:
                        ongoing_analyses[analysis_id]['message'] = message
                        ongoing_analyses[analysis_id]['progress'] = progress
                
                def completion_callback(result):
                    if analysis_id in ongoing_analyses:
                        ongoing_analyses[analysis_id]['status'] = 'completed'
                        ongoing_analyses[analysis_id]['progress'] = 100
                        ongoing_analyses[analysis_id]['result'] = result
                        ongoing_analyses[analysis_id]['message'] = 'Analysis completed'
                
                def error_callback(error):
                    if analysis_id in ongoing_analyses:
                        ongoing_analyses[analysis_id]['status'] = 'error'
                        ongoing_analyses[analysis_id]['error'] = error
                        ongoing_analyses[analysis_id]['message'] = f'Error: {error}'
                
                # Update status
                ongoing_analyses[analysis_id]['status'] = 'running'
                
                # Run the analysis
                restaurant_analyzer.analyze_restaurant_async(
                    place_id=place_id,
                    restaurant_name=restaurant_name,
                    max_reviews=max_reviews,
                    progress_callback=progress_callback,
                    completion_callback=completion_callback,
                    error_callback=error_callback
                )
                
            except Exception as e:
                logger.error(f"Analysis thread error: {e}")
                if analysis_id in ongoing_analyses:
                    ongoing_analyses[analysis_id]['status'] = 'error'
                    ongoing_analyses[analysis_id]['error'] = str(e)
        
        # Start the thread
        analysis_thread = Thread(target=run_analysis, daemon=True)
        analysis_thread.start()
        
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'message': 'Analysis started'
        })
        
    except Exception as e:
        logger.error(f"Analysis start error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/analysis_status/<analysis_id>')
def analysis_status(analysis_id):
    """Get analysis status."""
    try:
        if analysis_id not in ongoing_analyses:
            return jsonify({'success': False, 'error': 'Analysis not found'})
        
        analysis = ongoing_analyses[analysis_id]
        
        response = {
            'success': True,
            'status': analysis['status'],
            'progress': analysis['progress'],
            'message': analysis['message']
        }
        
        # Include result if completed
        if analysis['status'] == 'completed' and analysis['result']:
            response['result'] = analysis['result']
            # Clean up completed analysis after returning result
            del ongoing_analyses[analysis_id]
        
        # Include error if failed
        if analysis['status'] == 'error':
            response['error'] = analysis['error']
            # Clean up failed analysis
            del ongoing_analyses[analysis_id]
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/cancel_analysis/<analysis_id>', methods=['POST'])
def cancel_analysis(analysis_id):
    """Cancel an ongoing analysis."""
    try:
        if analysis_id in ongoing_analyses:
            del ongoing_analyses[analysis_id]
            return jsonify({'success': True, 'message': 'Analysis cancelled'})
        else:
            return jsonify({'success': False, 'error': 'Analysis not found'})
    except Exception as e:
        logger.error(f"Cancel analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/cache_info')
def cache_info():
    """Get cache information."""
    try:
        cache_status = restaurant_analyzer.get_cache_status()
        return jsonify({'success': True, 'cache_info': cache_status})
    except Exception as e:
        logger.error(f"Cache info error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    """Clear all caches."""
    try:
        clear_results = restaurant_analyzer.clear_all_caches()
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully',
            'details': clear_results
        })
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/export_analysis', methods=['POST'])
def export_analysis():
    """Export analysis results."""
    try:
        data = request.get_json()
        analysis_result = data.get('analysis_result')
        format_type = data.get('format', 'json')
        
        if not analysis_result:
            return jsonify({'success': False, 'error': 'No analysis result provided'})
        
        exported_data = restaurant_analyzer.export_analysis(analysis_result, format_type)
        
        return jsonify({
            'success': True,
            'exported_data': exported_data,
            'format': format_type
        })
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'ongoing_analyses': len(ongoing_analyses)
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

def check_web_dependencies():
    """Check if Flask and other web dependencies are available."""
    try:
        import flask
        return True
    except ImportError:
        print("Flask not found. Please install it with: pip install flask")
        return False

def main():
    """Main entry point for web application."""
    print("Starting AI Restaurant Recommender Web App...")
    print("=" * 50)
    
    # Check dependencies
    if not check_web_dependencies():
        return
    
    # Validate configuration
    config_status = validate_config()
    if not config_status['valid']:
        print("Configuration Issues:")
        for issue in config_status['issues']:
            print(f"  - {issue}")
        print("\nPlease fix configuration issues before starting the web app.")
        return
    
    # Start the Flask app
    try:
        print(f"Starting web server on http://{WEB_HOST}:{WEB_PORT}")
        print("Press Ctrl+C to stop the server")
        
        app.run(
            host=WEB_HOST,
            port=WEB_PORT,
            debug=WEB_DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\nWeb server stopped by user")
    except Exception as e:
        logger.error(f"Web server error: {e}")
        print(f"Error starting web server: {e}")

if __name__ == "__main__":
    main()