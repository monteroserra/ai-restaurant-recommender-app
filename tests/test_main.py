# test_main.py
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the UI import to avoid tkinter dependency in tests
sys.modules['ui'] = Mock()
sys.modules['restaurant_service'] = Mock()
sys.modules['location_service'] = Mock()

# Now import the main module
from main import RestaurantRecommenderApp

class TestRestaurantRecommenderApp(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the services
        self.mock_restaurant_service = Mock()
        self.mock_location_service = Mock()
        self.mock_ui = Mock()
        
        # Create app instance with mocked dependencies
        with patch('main.RestaurantFinderUI') as mock_ui_class:
            mock_ui_class.return_value = self.mock_ui
            self.app = RestaurantRecommenderApp()
            
        # Replace services with mocks
        self.app.restaurant_service = self.mock_restaurant_service
        self.app.location_service = self.mock_location_service
        self.app.ui = self.mock_ui
    
    def test_resolve_location_coordinates_valid(self):
        """Test resolving location with valid coordinates."""
        # Setup
        location_data = {"type": "coordinates", "lat": "40.7128", "lng": "-74.0060"}
        self.mock_location_service.validate_coordinates.return_value = (40.7128, -74.0060)
        
        # Test
        result = self.app.resolve_location(location_data)
        
        # Assert
        self.assertEqual(result, (40.7128, -74.0060))
        self.mock_location_service.validate_coordinates.assert_called_once_with("40.7128", "-74.0060")
    
    def test_resolve_location_coordinates_invalid(self):
        """Test resolving location with invalid coordinates."""
        # Setup
        location_data = {"type": "coordinates", "lat": "invalid", "lng": "-74.0060"}
        self.mock_location_service.validate_coordinates.return_value = None
        
        # Test
        result = self.app.resolve_location(location_data)
        
        # Assert
        self.assertIsNone(result)
        self.mock_ui.show_error.assert_called_once_with(
            "Invalid coordinates. Please check your latitude and longitude values."
        )
    
    def test_resolve_location_address_valid(self):
        """Test resolving location with valid address."""
        # Setup
        location_data = {"type": "address", "address": "New York, NY"}
        self.mock_location_service.get_coordinates_from_address.return_value = (40.7128, -74.0060)
        
        # Test
        result = self.app.resolve_location(location_data)
        
        # Assert
        self.assertEqual(result, (40.7128, -74.0060))
        self.mock_location_service.get_coordinates_from_address.assert_called_once_with("New York, NY")
    
    def test_resolve_location_address_invalid(self):
        """Test resolving location with invalid address."""
        # Setup
        location_data = {"type": "address", "address": "NonexistentPlace12345"}
        self.mock_location_service.get_coordinates_from_address.return_value = None
        
        # Test
        result = self.app.resolve_location(location_data)
        
        # Assert
        self.assertIsNone(result)
        self.mock_ui.show_error.assert_called_once_with(
            "Could not find coordinates for the given address. Please try a different address."
        )
    
    def test_format_location_string_coordinates(self):
        """Test formatting location string for coordinates."""
        location_data = {"type": "coordinates", "lat": "40.7128", "lng": "-74.0060"}
        result = self.app.format_location_string(location_data, 40.7128, -74.0060)
        
        self.assertEqual(result, "coordinates (40.7128, -74.0060)")
    
    def test_format_location_string_address(self):
        """Test formatting location string for address."""
        location_data = {"type": "address", "address": "New York, NY"}
        result = self.app.format_location_string(location_data, 40.7128, -74.0060)
        
        self.assertEqual(result, "New York, NY (40.7128, -74.0060)")
    
    def test_search_restaurants_success_flow(self):
        """Test successful restaurant search flow."""
        # Setup
        location_data = {"type": "coordinates", "lat": "40.7128", "lng": "-74.0060"}
        self.mock_location_service.validate_coordinates.return_value = (40.7128, -74.0060)
        
        # Mock restaurant search results
        mock_restaurants = [
            {
                "name": "Test Restaurant",
                "rating": 4.5,
                "user_ratings_total": 250,
                "vicinity": "Test Street",
                "geometry": {"location": {"lat": 40.7589, "lng": -73.9851}}
            }
        ]
        self.mock_restaurant_service.search_restaurants.return_value = mock_restaurants
        
        # Mock formatted restaurant data
        formatted_restaurant = {
            'name': 'Test Restaurant',
            'rating': 4.5,
            'reviews': 250,
            'address': 'Test Street',
            'walking_distance': '0.5 mi',
            'walking_duration': '10 mins'
        }
        self.mock_restaurant_service.format_restaurant_data.return_value = formatted_restaurant
        
        # Test
        self.app.search_restaurants(location_data, 1000, 100, 5)
        
        # Assert
        self.mock_location_service.validate_coordinates.assert_called_once_with("40.7128", "-74.0060")
        self.mock_restaurant_service.search_restaurants.assert_called_once_with(40.7128, -74.0060, 1000, 100, 5)
        self.mock_restaurant_service.add_walking_distances.assert_called_once_with(mock_restaurants, 40.7128, -74.0060)
        self.mock_restaurant_service.format_restaurant_data.assert_called_once_with(mock_restaurants[0])
        self.mock_ui.display_results.assert_called_once()
    
    def test_search_restaurants_no_results(self):
        """Test restaurant search with no results."""
        # Setup
        location_data = {"type": "coordinates", "lat": "40.7128", "lng": "-74.0060"}
        self.mock_location_service.validate_coordinates.return_value = (40.7128, -74.0060)
        self.mock_restaurant_service.search_restaurants.return_value = []
        
        # Test
        self.app.search_restaurants(location_data, 1000, 100, 5)
        
        # Assert
        self.mock_ui.display_results.assert_called_once_with([], "coordinates (40.7128, -74.0060)")
    
    def test_search_restaurants_location_resolution_fails(self):
        """Test restaurant search when location resolution fails."""
        # Setup
        location_data = {"type": "coordinates", "lat": "invalid", "lng": "-74.0060"}
        self.mock_location_service.validate_coordinates.return_value = None
        
        # Test
        self.app.search_restaurants(location_data, 1000, 100, 5)
        
        # Assert
        self.mock_restaurant_service.search_restaurants.assert_not_called()
        self.mock_ui.show_error.assert_called_once()
    
    def test_search_restaurants_exception_handling(self):
        """Test exception handling in restaurant search."""
        # Setup
        location_data = {"type": "coordinates", "lat": "40.7128", "lng": "-74.0060"}
        self.mock_location_service.validate_coordinates.side_effect = Exception("Test exception")
        
        # Test
        self.app.search_restaurants(location_data, 1000, 100, 5)
        
        # Assert
        self.mock_ui.show_error.assert_called_once()
        # Check that the error message starts with "Search failed:"
        args, kwargs = self.mock_ui.show_error.call_args
        self.assertTrue(args[0].startswith("Search failed:"))
    
    def test_search_restaurants_with_address_input(self):
        """Test restaurant search using address input."""
        # Setup
        location_data = {"type": "address", "address": "Times Square, NYC"}
        self.mock_location_service.get_coordinates_from_address.return_value = (40.7580, -73.9855)
        
        mock_restaurants = [
            {
                "name": "Times Square Restaurant",
                "rating": 4.2,
                "user_ratings_total": 180,
                "vicinity": "Times Square",
                "geometry": {"location": {"lat": 40.7580, "lng": -73.9855}}
            }
        ]
        self.mock_restaurant_service.search_restaurants.return_value = mock_restaurants
        
        formatted_restaurant = {
            'name': 'Times Square Restaurant',
            'rating': 4.2,
            'reviews': 180,
            'address': 'Times Square',
            'walking_distance': '0.1 mi',
            'walking_duration': '2 mins'
        }
        self.mock_restaurant_service.format_restaurant_data.return_value = formatted_restaurant
        
        # Test
        self.app.search_restaurants(location_data, 1500, 150, 10)
        
        # Assert
        self.mock_location_service.get_coordinates_from_address.assert_called_once_with("Times Square, NYC")
        self.mock_restaurant_service.search_restaurants.assert_called_once_with(40.7580, -73.9855, 1500, 150, 10)
        self.mock_ui.display_results.assert_called_once()
        
        # Check that the location string includes the address
        display_call_args = self.mock_ui.display_results.call_args[0]
        location_string = display_call_args[1]
        self.assertIn("Times Square, NYC", location_string)


class TestMainFunction(unittest.TestCase):
    """Test the main function and application entry point."""
    
    @patch('main.RestaurantRecommenderApp')
    def test_main_function_success(self, mock_app_class):
        """Test successful main function execution."""
        # Setup
        mock_app = Mock()
        mock_app_class.return_value = mock_app
        
        # Import and test main function
        from main import main
        main()
        
        # Assert
        mock_app_class.assert_called_once()
        mock_app.run.assert_called_once()
    
    @patch('main.RestaurantRecommenderApp')
    @patch('builtins.print')
    def test_main_function_import_error(self, mock_print, mock_app_class):
        """Test main function with import error."""
        # Setup
        mock_app_class.side_effect = ImportError("No module named 'config'")
        
        # Import and test main function
        from main import main
        main()
        
        # Assert
        mock_print.assert_called()
        # Check that configuration error message was printed
        call_args = [call[0][0] for call in mock_print.call_args_list]
        self.assertTrue(any("Configuration Error:" in arg for arg in call_args))
    
    @patch('main.RestaurantRecommenderApp')
    @patch('builtins.print')
    def test_main_function_general_exception(self, mock_print, mock_app_class):
        """Test main function with general exception."""
        # Setup
        mock_app_class.side_effect = Exception("General error")
        
        # Import and test main function
        from main import main
        main()
        
        # Assert
        mock_print.assert_called()
        # Check that application error message was printed
        call_args = [call[0][0] for call in mock_print.call_args_list]
        self.assertTrue(any("Application Error:" in arg for arg in call_args))

if __name__ == '__main__':
    unittest.main()