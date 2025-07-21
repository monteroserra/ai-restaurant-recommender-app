# web_server.py
"""
Web server for the AI Restaurant Recommender App
Serves the modern HTML UI and provides API endpoints for restaurant search
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import sys
import os
import json

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from restaurant_service import RestaurantService
from location_service import LocationService

app = Flask(__name__)
CORS(app)  # Enable CORS for API requests

# Initialize services
restaurant_service = RestaurantService()
location_service = LocationService()

# Store the HTML template (you can also load from file)
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍽️ AI Restaurant Recommender</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --warm-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            --cool-gradient: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            
            --text-primary: #2d3748;
            --text-secondary: #4a5568;
            --text-muted: #718096;
            --bg-primary: #ffffff;
            --bg-secondary: #f7fafc;
            --bg-card: #ffffff;
            --border-color: #e2e8f0;
            --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }

        .app-container {
            min-height: 100vh;
            padding: 2rem 1rem;
            background: radial-gradient(ellipse at top, rgba(255,255,255,0.1) 0%, transparent 70%);
        }

        .main-card {
            max-width: 1200px;
            margin: 0 auto;
            background: var(--bg-card);
            border-radius: 24px;
            box-shadow: var(--shadow-xl);
            overflow: hidden;
            backdrop-filter: blur(20px);
        }

        .header {
            background: var(--primary-gradient);
            padding: 3rem 2rem;
            text-align: center;
            color: white;
            position: relative;
            overflow: hidden;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
            opacity: 0.3;
        }

        .header-content {
            position: relative;
            z-index: 1;
        }

        .app-title {
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .app-subtitle {
            font-size: clamp(1rem, 2.5vw, 1.25rem);
            font-weight: 300;
            opacity: 0.9;
            margin-bottom: 2rem;
        }

        .stats-row {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
        }

        .stat-item {
            text-align: center;
            padding: 1rem;
            background: rgba(255,255,255,0.1);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            min-width: 120px;
        }

        .stat-number {
            font-size: 1.5rem;
            font-weight: 600;
            display: block;
        }

        .stat-label {
            font-size: 0.875rem;
            opacity: 0.8;
        }

        .content-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            padding: 2rem;
        }

        .section-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .section-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--secondary-gradient);
            border-radius: 20px 20px 0 0;
        }

        .section-card:hover {
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
        }

        .section-header {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
            gap: 0.75rem;
        }

        .section-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            background: var(--cool-gradient);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            color: white;
            box-shadow: var(--shadow-sm);
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-label {
            display: block;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: var(--text-secondary);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .radio-group {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .radio-option {
            flex: 1;
        }

        .radio-input {
            display: none;
        }

        .radio-label {
            display: block;
            padding: 0.75rem 1rem;
            border: 2px solid var(--border-color);
            border-radius: 12px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            background: var(--bg-secondary);
        }

        .radio-input:checked + .radio-label {
            border-color: transparent;
            background: var(--success-gradient);
            color: white;
            box-shadow: var(--shadow-md);
            transform: scale(1.02);
        }

        .input-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }

        .input-group {
            position: relative;
        }

        .input-field {
            width: 100%;
            padding: 0.875rem 1rem;
            border: 2px solid var(--border-color);
            border-radius: 12px;
            font-size: 0.875rem;
            transition: all 0.3s ease;
            background: var(--bg-secondary);
        }

        .input-field:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            background: white;
        }

        .slider-container {
            margin-bottom: 1rem;
        }

        .slider-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }

        .slider-label {
            font-weight: 500;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }

        .slider-value {
            background: var(--warm-gradient);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            box-shadow: var(--shadow-sm);
        }

        .slider {
            width: 100%;
            height: 8px;
            border-radius: 4px;
            background: var(--border-color);
            outline: none;
            appearance: none;
            cursor: pointer;
        }

        .slider::-webkit-slider-thumb {
            appearance: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: var(--primary-gradient);
            cursor: pointer;
            box-shadow: var(--shadow-md);
            transition: all 0.3s ease;
        }

        .slider::-webkit-slider-thumb:hover {
            transform: scale(1.1);
            box-shadow: var(--shadow-lg);
        }

        .search-button {
            width: 100%;
            padding: 1rem 2rem;
            background: var(--secondary-gradient);
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 1.125rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-md);
            position: relative;
            overflow: hidden;
            margin-top: 1rem;
        }

        .search-button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            transition: all 0.6s ease;
            transform: translate(-50%, -50%);
        }

        .search-button:hover::before {
            width: 300px;
            height: 300px;
        }

        .search-button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-xl);
        }

        .search-button:active {
            transform: translateY(0);
        }

        .search-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .button-content {
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .results-section {
            grid-column: 1 / -1;
            margin-top: 1rem;
        }

        .results-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.5rem;
        }

        .results-count {
            background: var(--success-gradient);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
            box-shadow: var(--shadow-sm);
        }

        .restaurant-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
        }

        .restaurant-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 1.5rem;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .restaurant-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--warm-gradient);
            border-radius: 20px 20px 0 0;
        }

        .restaurant-card:hover {
            box-shadow: var(--shadow-lg);
            transform: translateY(-4px);
        }

        .restaurant-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 1rem;
        }

        .restaurant-name {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }

        .restaurant-rating {
            display: flex;
            align-items: center;
            gap: 0.25rem;
            background: var(--success-gradient);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
            box-shadow: var(--shadow-sm);
        }

        .restaurant-details {
            space-y: 0.75rem;
        }

        .detail-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }

        .detail-icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: var(--cool-gradient);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.875rem;
            color: white;
        }

        .detail-text {
            font-size: 0.875rem;
            color: var(--text-secondary);
        }

        .loading-state {
            text-align: center;
            padding: 3rem 2rem;
            color: var(--text-muted);
        }

        .loading-spinner {
            width: 48px;
            height: 48px;
            border: 4px solid var(--border-color);
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .status-bar {
            grid-column: 1 / -1;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.875rem;
            margin-top: 1rem;
        }

        .error-message {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .content-grid {
                grid-template-columns: 1fr;
                padding: 1rem;
            }

            .header {
                padding: 2rem 1rem;
            }

            .stats-row {
                gap: 1rem;
            }

            .stat-item {
                min-width: 100px;
                padding: 0.75rem;
            }

            .input-row {
                grid-template-columns: 1fr;
            }

            .radio-group {
                flex-direction: column;
            }

            .restaurant-grid {
                grid-template-columns: 1fr;
            }

            .results-header {
                flex-direction: column;
                gap: 1rem;
                align-items: flex-start;
            }
        }

        @media (max-width: 480px) {
            .app-container {
                padding: 1rem 0.5rem;
            }

            .section-card {
                padding: 1.5rem;
            }

            .main-card {
                border-radius: 16px;
            }
        }

        /* Custom animations */
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="main-card">
            <!-- Header Section -->
            <div class="header">
                <div class="header-content">
                    <h1 class="app-title">🍽️ AI Restaurant Recommender</h1>
                    <p class="app-subtitle">Discover amazing restaurants near you with smart recommendations</p>
                    
                    <div class="stats-row">
                        <div class="stat-item">
                            <span class="stat-number">1M+</span>
                            <span class="stat-label">Restaurants</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">500K+</span>
                            <span class="stat-label">Reviews</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">50+</span>
                            <span class="stat-label">Cities</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="content-grid">
                <!-- Location Settings -->
                <div class="section-card">
                    <div class="section-header">
                        <div class="section-icon">📍</div>
                        <h2 class="section-title">Location Settings</h2>
                    </div>

                    <div class="form-group">
                        <label class="form-label">🎯 How would you like to set your location?</label>
                        <div class="radio-group">
                            <div class="radio-option">
                                <input type="radio" id="coordinates" name="locationType" value="coordinates" class="radio-input" checked>
                                <label for="coordinates" class="radio-label">
                                    <i class="fas fa-map-marked-alt"></i> Coordinates
                                </label>
                            </div>
                            <div class="radio-option">
                                <input type="radio" id="address" name="locationType" value="address" class="radio-input">
                                <label for="address" class="radio-label">
                                    <i class="fas fa-map-marker-alt"></i> Address
                                </label>
                            </div>
                        </div>
                    </div>

                    <div id="coordinates-section" class="form-group">
                        <label class="form-label">🗺️ Coordinates</label>
                        <div class="input-row">
                            <div class="input-group">
                                <input type="number" id="latitude" class="input-field" placeholder="Latitude" value="40.7128" step="any">
                            </div>
                            <div class="input-group">
                                <input type="number" id="longitude" class="input-field" placeholder="Longitude" value="-74.0060" step="any">
                            </div>
                        </div>
                    </div>

                    <div id="address-section" class="form-group" style="display: none;">
                        <label class="form-label">🏠 Enter Address</label>
                        <input type="text" id="addressInput" class="input-field" placeholder="e.g., Times Square, New York, NY">
                    </div>
                </div>

                <!-- Search Parameters -->
                <div class="section-card">
                    <div class="section-header">
                        <div class="section-icon">⚙️</div>
                        <h2 class="section-title">Search Parameters</h2>
                    </div>

                    <div class="slider-container">
                        <div class="slider-header">
                            <span class="slider-label">🔍 Search Radius</span>
                            <span class="slider-value" id="radiusValue">1000m</span>
                        </div>
                        <input type="range" id="radiusSlider" class="slider" min="100" max="5000" value="1000" step="100">
                    </div>

                    <div class="slider-container">
                        <div class="slider-header">
                            <span class="slider-label">⭐ Minimum Reviews</span>
                            <span class="slider-value" id="reviewsValue">100 reviews</span>
                        </div>
                        <input type="range" id="reviewsSlider" class="slider" min="10" max="1000" value="100" step="10">
                    </div>

                    <div class="slider-container">
                        <div class="slider-header">
                            <span class="slider-label">📊 Maximum Results</span>
                            <span class="slider-value" id="resultsValue">5 results</span>
                        </div>
                        <input type="range" id="resultsSlider" class="slider" min="1" max="20" value="5" step="1">
                    </div>

                    <button id="searchButton" class="search-button">
                        <div class="button-content">
                            <i class="fas fa-search"></i>
                            <span>Find Amazing Restaurants</span>
                            <span>🎉</span>
                        </div>
                    </button>
                </div>

                <!-- Results Section -->
                <div id="resultsSection" class="section-card results-section" style="display: none;">
                    <div class="section-header">
                        <div>
                            <div class="section-icon">📊</div>
                            <h2 class="section-title">Search Results</h2>
                        </div>
                        <div id="resultsCount" class="results-count">0 restaurants found</div>
                    </div>

                    <div id="restaurantGrid" class="restaurant-grid">
                        <!-- Restaurant cards will be inserted here -->
                    </div>
                </div>

                <!-- Loading State -->
                <div id="loadingSection" class="section-card results-section" style="display: none;">
                    <div class="loading-state">
                        <div class="loading-spinner"></div>
                        <h3>🔍 Searching for amazing restaurants...</h3>
                        <p>Please wait while we find the best spots near you</p>
                    </div>
                </div>
            </div>

            <!-- Status Bar -->
            <div id="statusBar" class="status-bar">
                <i class="fas fa-info-circle"></i>
                Ready to discover amazing restaurants near you! 🚀
            </div>
        </div>
    </div>

    <script>
        // UI State Management
        const ui = {
            elements: {
                locationTypeRadios: document.querySelectorAll('input[name="locationType"]'),
                coordinatesSection: document.getElementById('coordinates-section'),
                addressSection: document.getElementById('address-section'),
                radiusSlider: document.getElementById('radiusSlider'),
                reviewsSlider: document.getElementById('reviewsSlider'),
                resultsSlider: document.getElementById('resultsSlider'),
                radiusValue: document.getElementById('radiusValue'),
                reviewsValue: document.getElementById('reviewsValue'),
                resultsValue: document.getElementById('resultsValue'),
                searchButton: document.getElementById('searchButton'),
                resultsSection: document.getElementById('resultsSection'),
                loadingSection: document.getElementById('loadingSection'),
                restaurantGrid: document.getElementById('restaurantGrid'),
                resultsCount: document.getElementById('resultsCount'),
                statusBar: document.getElementById('statusBar'),
                latitude: document.getElementById('latitude'),
                longitude: document.getElementById('longitude'),
                addressInput: document.getElementById('addressInput')
            },

            init() {
                this.bindEvents();
                this.updateSliderValues();
            },

            bindEvents() {
                // Location type toggle
                this.elements.locationTypeRadios.forEach(radio => {
                    radio.addEventListener('change', () => this.toggleLocationInput());
                });

                // Slider updates
                this.elements.radiusSlider.addEventListener('input', () => this.updateSliderValues());
                this.elements.reviewsSlider.addEventListener('input', () => this.updateSliderValues());
                this.elements.resultsSlider.addEventListener('input', () => this.updateSliderValues());

                // Search button
                this.elements.searchButton.addEventListener('click', () => this.handleSearch());

                // Enter key support
                this.elements.addressInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') this.handleSearch();
                });
            },

            toggleLocationInput() {
                const selectedType = document.querySelector('input[name="locationType"]:checked').value;
                
                if (selectedType === 'coordinates') {
                    this.elements.coordinatesSection.style.display = 'block';
                    this.elements.addressSection.style.display = 'none';
                } else {
                    this.elements.coordinatesSection.style.display = 'none';
                    this.elements.addressSection.style.display = 'block';
                }
            },

            updateSliderValues() {
                const radius = this.elements.radiusSlider.value;
                const reviews = this.elements.reviewsSlider.value;
                const results = this.elements.resultsSlider.value;

                this.elements.radiusValue.textContent = `${radius}m`;
                this.elements.reviewsValue.textContent = `${reviews} reviews`;
                this.elements.resultsValue.textContent = `${results} result${results > 1 ? 's' : ''}`;
            },

            showLoading() {
                this.elements.resultsSection.style.display = 'none';
                this.elements.loadingSection.style.display = 'block';
                this.elements.searchButton.disabled = true;
                this.updateStatus('🔍 Searching for restaurants...');
            },

            hideLoading() {
                this.elements.loadingSection.style.display = 'none';
                this.elements.searchButton.disabled = false;
            },

            showResults(restaurants, locationInfo) {
                this.hideLoading();
                this.elements.resultsSection.style.display = 'block';
                this.elements.resultsSection.classList.add('fade-in');
                
                this.elements.resultsCount.textContent = `${restaurants.length} restaurant${restaurants.length !== 1 ? 's' : ''} found`;
                this.renderRestaurants(restaurants);
                this.updateStatus(`✅ Found ${restaurants.length} restaurants near ${locationInfo}`);
            },

            renderRestaurants(restaurants) {
                this.elements.restaurantGrid.innerHTML = '';

                if (restaurants.length === 0) {
                    this.elements.restaurantGrid.innerHTML = `
                        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted);">
                            <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
                            <h3>No restaurants found</h3>
                            <p>Try adjusting your search parameters or expanding the search radius</p>
                        </div>
                    `;
                    return;
                }

                restaurants.forEach((restaurant, index) => {
                    const card = this.createRestaurantCard(restaurant, index);
                    this.elements.restaurantGrid.appendChild(card);
                });
            },

            createRestaurantCard(restaurant, index) {
                const card = document.createElement('div');
                card.className = 'restaurant-card fade-in';
                card.style.animationDelay = `${index * 0.1}s`;

                card.innerHTML = `
                    <div class="restaurant-header">
                        <div>
                            <h3 class="restaurant-name">${restaurant.name}</h3>
                        </div>
                        <div class="restaurant-rating">
                            <i class="fas fa-star"></i>
                            ${restaurant.rating}
                        </div>
                    </div>
                    
                    <div class="restaurant-details">
                        <div class="detail-item">
                            <div class="detail-icon">
                                <i class="fas fa-users"></i>
                            </div>
                            <span class="detail-text">${restaurant.reviews.toLocaleString()} reviews</span>
                        </div>
                        
                        <div class="detail-item">
                            <div class="detail-icon">
                                <i class="fas fa-map-marker-alt"></i>
                            </div>
                            <span class="detail-text">${restaurant.address}</span>
                        </div>
                        
                        <div class="detail-item">
                            <div class="detail-icon">
                                <i class="fas fa-walking"></i>
                            </div>
                            <span class="detail-text">${restaurant.walking_distance} • ${restaurant.walking_duration}</span>
                        </div>
                    </div>
                `;

                return card;
            },

            updateStatus(message) {
                this.elements.statusBar.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
            },

            showError(message) {
                this.hideLoading();
                this.updateStatus(`❌ ${message}`);
                
                // Show error in results area
                this.elements.resultsSection.style.display = 'block';
                this.elements.restaurantGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted);">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                        <h3>Search Error</h3>
                        <p>${message}</p>
                    </div>
                `;
            },

            async handleSearch() {
                const searchParams = this.getSearchParameters();
                
                if (!searchParams) return;

                this.showLoading();

                try {
                    const response = await fetch('/api/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(searchParams)
                    });

                    const data = await response.json();

                    if (data.success) {
                        this.showResults(data.restaurants, data.location_info);
                    } else {
                        this.showError(data.error || 'Search failed');
                    }
                } catch (error) {
                    this.showError('Network error. Please check your connection and try again.');
                    console.error('Search error:', error);
                }
            },

            getSearchParameters() {
                const locationType = document.querySelector('input[name="locationType"]:checked').value;
                
                const params = {
                    locationType,
                    radius: parseInt(this.elements.radiusSlider.value),
                    minReviews: parseInt(this.elements.reviewsSlider.value),
                    maxResults: parseInt(this.elements.resultsSlider.value)
                };

                if (locationType === 'coordinates') {
                    const lat = parseFloat(this.elements.latitude.value);
                    const lng = parseFloat(this.elements.longitude.value);
                    
                    if (isNaN(lat) || isNaN(lng)) {
                        this.showError('Please enter valid latitude and longitude values');
                        return null;
                    }
                    
                    if (lat < -90 || lat > 90 || lng < -180 || lng > 180) {
                        this.showError('Coordinates are out of valid range');
                        return null;
                    }
                    
                    params.latitude = lat;
                    params.longitude = lng;
                } else {
                    const address = this.elements.addressInput.value.trim();
                    if (!address) {
                        this.showError('Please enter an address');
                        return null;
                    }
                    
                    params.address = address;
                }

                return params;
            }
        };

        // Initialize the UI when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            ui.init();
        });
    </script>
</body>
</html>"""

@app.route('/')
def index():
    """Serve the main HTML page"""
    return HTML_TEMPLATE

@app.route('/api/search', methods=['POST'])
def search_restaurants():
    """API endpoint for restaurant search"""
    try:
        data = request.get_json()
        
        # Extract search parameters
        location_type = data.get('locationType')
        radius = data.get('radius', 1000)
        min_reviews = data.get('minReviews', 100)
        max_results = data.get('maxResults', 5)
        
        # Resolve location to coordinates
        if location_type == 'coordinates':
            lat = data.get('latitude')
            lng = data.get('longitude')
            
            # Validate coordinates
            coordinates = location_service.validate_coordinates(lat, lng)
            if coordinates is None:
                return jsonify({
                    'success': False,
                    'error': 'Invalid coordinates. Please check your latitude and longitude values.'
                })
            
            lat, lng = coordinates
            location_info = f"coordinates ({lat:.4f}, {lng:.4f})"
            
        elif location_type == 'address':
            address = data.get('address')
            if not address:
                return jsonify({
                    'success': False,
                    'error': 'Address is required'
                })
            
            # Convert address to coordinates
            coordinates = location_service.get_coordinates_from_address(address)
            if coordinates is None:
                return jsonify({
                    'success': False,
                    'error': 'Could not find coordinates for the given address. Please try a different address.'
                })
            
            lat, lng = coordinates
            location_info = f"{address} ({lat:.4f}, {lng:.4f})"
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid location type'
            })
        
        # Search for restaurants
        restaurants = restaurant_service.search_restaurants(lat, lng, radius, min_reviews, max_results)
        
        if not restaurants:
            return jsonify({
                'success': True,
                'restaurants': [],
                'location_info': location_info
            })
        
        # Add walking distances
        restaurant_service.add_walking_distances(restaurants, lat, lng)
        
        # Format restaurant data for frontend
        formatted_restaurants = []
        for place in restaurants:
            formatted_data = restaurant_service.format_restaurant_data(place)
            formatted_restaurants.append(formatted_data)
        
        return jsonify({
            'success': True,
            'restaurants': formatted_restaurants,
            'location_info': location_info
        })
        
    except Exception as e:
        print(f"Search error: {e}")  # For debugging
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Restaurant Recommender'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("🍽️ Starting AI Restaurant Recommender Web Server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔧 Make sure you have your Google Maps API key configured in config.py")
    
    # Run the Flask app
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )