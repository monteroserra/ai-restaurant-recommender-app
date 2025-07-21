# test_restaurant_service.py
import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from restaurant_service import RestaurantService

class TestRestaurantService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.restaurant_service = RestaurantService()
        
        # Sample restaurant data for testing
        self.sample_restaurant = {
            "name": "Test Restaurant",
            "rating": 4.5,
            "user_ratings_total": 250,
            "vicinity": "123 Test Street",
            "geometry": {
                "location": {
                    "lat": 40.7589,
                    "lng": -73.9851
                }
            }
        }
    
    @patch('restaurant_service.requests.get')
    def test_search_restaurants_success(self, mock_get):
        """Test successful restaurant search."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "OK",
            "results": [
                self.sample_restaurant,
                {
                    "name": "Another Restaurant",
                    "rating": 4.2,
                    "user_ratings_total": 150,
                    "vicinity": "456 Another Street",
                    "geometry": {
                        "location": {
                            "lat": 40.7500,
                            "lng": -73.9800
                        }
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Test the method
        result = self.restaurant_service.search_restaurants(40.7128, -74.0060, 1000, 100, 5)
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Test Restaurant")
        self.assertEqual(result[1]["name"], "Another Restaurant")
        mock_get.assert_called_once()
    
    @patch('restaurant_service.requests.get')
    def test_search_restaurants_with_filtering(self, mock_get):
        """Test restaurant search with review filtering."""
        # Mock API response with restaurants having different review counts
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "OK",
            "results": [
                self.sample_restaurant,  # 250 reviews - should be included
                {
                    "name": "Low Review Restaurant",
                    "rating": 4.0,
                    "user_ratings_total": 50,  # Below minimum - should be filtered out
                    "vicinity": "789 Low Review Street",
                    "geometry": {
                        "location": {