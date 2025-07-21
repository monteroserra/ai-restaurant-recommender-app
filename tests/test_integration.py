# test_integration.py
"""
Integration tests for the AI Restaurant Recommender App
These tests verify that different components work together correctly
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock config
import test_config
sys.modules['config'] = test_config

from restaurant_service import RestaurantService
from location_service import LocationService

class TestRestaurantLocationIntegration(unittest.TestCase):
    """Test integration between restaurant and location services."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.restaurant_service = RestaurantService()
        self.location_service = LocationService()
    
    @patch('restaurant_service.requests.get')
    @patch('location_service.requests.get')
    def test_address_to_restaurant_search_flow(self, mock_location_get, mock_restaurant_get):
        """Test complete flow from address to restaurant results."""
        # Mock geocoding API response
        mock_location_response = Mock()
        mock_location_response.json.return_value = {
            "status": "OK",
            "results": [
                {
                    "geometry": {
                        "location": {
                            "lat": 40.7580,
                            "lng": -73.9855
                        }
                    }
                }
            ]
        }
        mock_location_get.return_value = mock_location_response
        
        # Mock restaurant search API response
        mock_restaurant_response = Mock()
        mock_restaurant_response.json.return_value = {
            "status": "OK",
            "results": [
                {
                    "name": "Times Square Diner",
                    "rating": 4.2,
                    "user_ratings_total": 250,
                    "vicinity": "Broadway, New York",
                    "geometry": {
                        "location": {
                            "lat": 40.7581,
                            "lng": -73.9856
                        }
                    }
                }
            ]
        }
        mock_restaurant_get.return_value = mock_restaurant_response
        
        # Test the flow
        # Step 1: Convert address to coordinates
        coordinates = self.location_service.get_coordinates_from_address("Times Square, NYC")
        self.assertIsNotNone(coordinates)
        lat, lng = coordinates
        
        # Step 2: Search for restaurants using those coordinates
        restaurants = self.restaurant_service.search_restaurants(lat, lng, 1000, 100, 5)
        self.assertEqual(len(restaurants), 1)
        self.assertEqual(restaurants[0]["name"], "Times Square Diner")
        
        # Verify API calls were made correctly
        mock_location_get.assert_called_once()
        mock_restaurant_get.assert_called_once()
    
    @patch('restaurant_service.requests.get')
    def test_restaurant_search_with_walking_distances(self, mock_get):
        """Test restaurant search with walking distance calculation."""
        # Mock API responses for both nearby search and distance matrix
        responses = [
            # First call: nearby search
            Mock(json=lambda: {
                "status": "OK",
                "results": [
                    {
                        "name": "Test Restaurant",
                        "rating": 4.5,
                        "user_ratings_total": 200,
                        "vicinity": "Test Street",
                        "geometry": {
                            "location": {
                                "lat": 40.7589,
                                "lng": -73.9851
                            }
                        }
                    }
                ]
            }),
            # Second call: distance matrix
            Mock(json=lambda: {
                "status": "OK",
                "rows": [
                    {
                        "elements": [
                            {
                                "status": "OK",
                                "distance": {"text": "0.3 mi"},
                                "duration": {"text": "6 mins"}
                            }
                        ]
                    }
                ]
            })
        ]
        mock_get.side_effect = responses
        
        # Test the complete flow
        lat, lng = 40.7128, -74.0060
        restaurants = self.restaurant_service.search_restaurants(lat, lng, 1000, 100, 5)
        
        # Add walking distances
        self.restaurant_service.add_walking_distances(restaurants, lat, lng)
        
        # Verify results
        self.assertEqual(len(restaurants), 1)
        restaurant = restaurants[0]
        self.assertEqual(restaurant["name"], "Test Restaurant")
        self.assertEqual(restaurant["walking_distance"], "0.3 mi")
        self.assertEqual(restaurant["walking_duration"], "6 mins")
        
        # Verify both API calls were made
        self.assertEqual(mock_get.call_count, 2)


class TestEndToEndFlow(unittest.TestCase):
    """Test end-to-end application flow with mocked external dependencies."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the UI to avoid tkinter dependencies
        self.mock_ui = Mock()
        
        # Create services
        self.restaurant_service = RestaurantService()
        self.location_service = LocationService()
    
    @patch('restaurant_service.requests.get')
    @patch('location_service.requests.get')
    def test_complete_coordinate_search_flow(self, mock_location_get, mock_restaurant_get):
        """Test complete flow with coordinate input."""
        # Mock restaurant search and distance matrix APIs
        responses = [
            # Nearby search response
            Mock(json=lambda: {
                "status": "OK",
                "results": [
                    {
                        "name": "Best Restaurant",
                        "rating": 4.8,
                        "user_ratings_total": 500,
                        "vicinity": "Main Street",
                        "geometry": {"location": {"lat": 40.7590, "lng": -73.9852}}
                    },
                    {
                        "name": "Good Restaurant", 
                        "rating": 4.3,
                        "user_ratings_total": 300,
                        "vicinity": "Second Street",
                        "geometry": {"location": {"lat": 40.7585, "lng": -73.9850}}
                    }
                ]
            }),
            # Distance matrix response
            Mock(json=lambda: {
                "status": "OK",
                "rows": [{
                    "elements": [
                        {"status": "OK", "distance": {"text": "0.2 mi"}, "duration": {"text": "4 mins"}},
                        {"status": "OK", "distance": {"text": "0.3 mi"}, "duration": {"text": "6 mins"}}
                    ]
                }]
            })
        ]
        mock_restaurant_get.side_effect = responses
        
        # Simulate the complete flow
        # 1. Validate coordinates
        coordinates = self.location_service.validate_coordinates("40.7128", "-74.0060")
        self.assertIsNotNone(coordinates)
        lat, lng = coordinates
        
        # 2. Search restaurants
        restaurants = self.restaurant_service.search_restaurants(lat, lng, 1000, 200, 5)
        self.assertEqual(len(restaurants), 2)
        
        # 3. Add walking distances
        self.restaurant_service.add_walking_distances(restaurants, lat, lng)
        
        # 4. Format results
        formatted_restaurants = [
            self.restaurant_service.format_restaurant_data(place)
            for place in restaurants
        ]
        
        # Verify results
        self.assertEqual(len(formatted_restaurants), 2)
        
        # Check sorting (should be by rating, descending)
        self.assertEqual(formatted_restaurants[0]['name'], 'Best Restaurant')
        self.assertEqual(formatted_restaurants[0]['rating'], 4.8)
        self.assertEqual(formatted_restaurants[0]['walking_distance'], '0.2 mi')
        
        self.assertEqual(formatted_restaurants[1]['name'], 'Good Restaurant')
        self.assertEqual(formatted_restaurants[1]['rating'], 4.3)
        self.assertEqual(formatted_restaurants[1]['walking_distance'], '0.3 mi')
    
    @patch('restaurant_service.requests.get')
    @patch('location_service.requests.get')
    def test_complete_address_search_flow(self, mock_location_get, mock_restaurant_get):
        """Test complete flow with address input."""
        # Mock geocoding API response
        mock_location_response = Mock()
        mock_location_response.json.return_value = {
            "status": "OK",
            "results": [{
                "geometry": {
                    "location": {"lat": 37.7749, "lng": -122.4194}
                }
            }]
        }
        mock_location_get.return_value = mock_location_response
        
        # Mock restaurant search API responses
        restaurant_responses = [
            # Nearby search
            Mock(json=lambda: {
                "status": "OK", 
                "results": [{
                    "name": "SF Restaurant",
                    "rating": 4.6,
                    "user_ratings_total": 150,
                    "vicinity": "Market Street, San Francisco",
                    "geometry": {"location": {"lat": 37.7750, "lng": -122.4195}}
                }]
            }),
            # Distance matrix
            Mock(json=lambda: {
                "status": "OK",
                "rows": [{
                    "elements": [{
                        "status": "OK",
                        "distance": {"text": "0.1 mi"},
                        "duration": {"text": "2 mins"}
                    }]
                }]
            })
        ]
        mock_restaurant_get.side_effect = restaurant_responses
        
        # Simulate complete address flow
        # 1. Convert address to coordinates
        coordinates = self.location_service.get_coordinates_from_address("San Francisco, CA")
        self.assertIsNotNone(coordinates)
        lat, lng = coordinates
        
        # 2. Search restaurants
        restaurants = self.restaurant_service.search_restaurants(lat, lng, 1500, 100, 10)
        self.assertEqual(len(restaurants), 1)
        
        # 3. Add walking distances
        self.restaurant_service.add_walking_distances(restaurants, lat, lng)
        
        # 4. Format and verify results
        restaurant = self.restaurant_service.format_restaurant_data(restaurants[0])
        self.assertEqual(restaurant['name'], 'SF Restaurant')
        self.assertEqual(restaurant['walking_distance'], '0.1 mi')
        self.assertEqual(restaurant['walking_duration'], '2 mins')
        
        # Verify API calls
        mock_location_get.assert_called_once()
        self.assertEqual(mock_restaurant_get.call_count, 2)


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling across integrated components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.restaurant_service = RestaurantService()
        self.location_service = LocationService()
    
    @patch('restaurant_service.requests.get')
    @patch('location_service.requests.get')
    def test_geocoding_failure_handling(self, mock_location_get, mock_restaurant_get):
        """Test handling when geocoding fails."""
        # Mock failed geocoding response
        mock_location_response = Mock()
        mock_location_response.json.return_value = {
            "status": "ZERO_RESULTS",
            "results": []
        }
        mock_location_get.return_value = mock_location_response
        
        # Test geocoding failure
        coordinates = self.location_service.get_coordinates_from_address("InvalidAddress12345")
        self.assertIsNone(coordinates)
        
        # Restaurant search should not be called
        mock_restaurant_get.assert_not_called()
    
    @patch('restaurant_service.requests.get')
    def test_restaurant_api_failure_handling(self, mock_get):
        """Test handling when restaurant API fails."""
        # Mock failed restaurant API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "REQUEST_DENIED",
            "error_message": "API key invalid"
        }
        mock_get.return_value = mock_response
        
        # Test restaurant search failure
        restaurants = self.restaurant_service.search_restaurants(40.7128, -74.0060, 1000, 100, 5)
        self.assertEqual(restaurants, [])
    
    @patch('restaurant_service.requests.get')
    def test_partial_distance_matrix_failure(self, mock_get):
        """Test handling when distance matrix partially fails."""
        # Mock responses: successful restaurant search, failed distance matrix
        responses = [
            # Successful nearby search
            Mock(json=lambda: {
                "status": "OK",
                "results": [{
                    "name": "Test Restaurant",
                    "rating": 4.0,
                    "user_ratings_total": 100,
                    "vicinity": "Test Street",
                    "geometry": {"location": {"lat": 40.7590, "lng": -73.9850}}
                }]
            }),
            # Failed distance matrix
            Mock(json=lambda: {
                "status": "REQUEST_DENIED",
                "error_message": "Quota exceeded"
            })
        ]
        mock_get.side_effect = responses
        
        # Test the flow
        restaurants = self.restaurant_service.search_restaurants(40.7128, -74.0060, 1000, 50, 5)
        self.assertEqual(len(restaurants), 1)
        
        # Try to add walking distances (should fail gracefully)
        self.restaurant_service.add_walking_distances(restaurants, 40.7128, -74.0060)
        
        # Restaurant should still have N/A for walking info
        self.assertEqual(restaurants[0]["walking_distance"], "N/A")
        self.assertEqual(restaurants[0]["walking_duration"], "N/A")

if __name__ == '__main__':
    unittest.main()