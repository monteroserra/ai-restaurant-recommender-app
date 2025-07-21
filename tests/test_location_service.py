# test_location_service.py
import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from location_service import LocationService

class TestLocationService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.location_service = LocationService()
    
    @patch('location_service.requests.get')
    def test_get_coordinates_from_address_success(self, mock_get):
        """Test successful address to coordinates conversion."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "OK",
            "results": [
                {
                    "geometry": {
                        "location": {
                            "lat": 40.7128,
                            "lng": -74.0060
                        }
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Test the method
        result = self.location_service.get_coordinates_from_address("New York, NY")
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result, (40.7128, -74.0060))
        mock_get.assert_called_once()
    
    @patch('location_service.requests.get')
    def test_get_coordinates_from_address_not_found(self, mock_get):
        """Test address not found scenario."""
        # Mock API response for address not found
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "ZERO_RESULTS",
            "results": []
        }
        mock_get.return_value = mock_response
        
        # Test the method
        result = self.location_service.get_coordinates_from_address("NonexistentPlace12345")
        
        # Assertions
        self.assertIsNone(result)
    
    @patch('location_service.requests.get')
    def test_get_coordinates_from_address_api_error(self, mock_get):
        """Test API error handling."""
        # Mock API response with error
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "REQUEST_DENIED",
            "error_message": "API key invalid"
        }
        mock_get.return_value = mock_response
        
        # Test the method
        result = self.location_service.get_coordinates_from_address("New York, NY")
        
        # Assertions
        self.assertIsNone(result)
    
    def test_get_coordinates_from_address_empty_input(self):
        """Test empty address input."""
        result = self.location_service.get_coordinates_from_address("")
        self.assertIsNone(result)
        
        result = self.location_service.get_coordinates_from_address("   ")
        self.assertIsNone(result)
    
    @patch('location_service.requests.get')
    def test_get_coordinates_from_address_network_error(self, mock_get):
        """Test network error handling."""
        # Mock network exception
        mock_get.side_effect = Exception("Network error")
        
        # Test the method
        result = self.location_service.get_coordinates_from_address("New York, NY")
        
        # Assertions
        self.assertIsNone(result)
    
    def test_validate_coordinates_valid(self):
        """Test valid coordinate validation."""
        # Test valid coordinates
        result = self.location_service.validate_coordinates(40.7128, -74.0060)
        self.assertEqual(result, (40.7128, -74.0060))
        
        # Test boundary values
        result = self.location_service.validate_coordinates(90, 180)
        self.assertEqual(result, (90.0, 180.0))
        
        result = self.location_service.validate_coordinates(-90, -180)
        self.assertEqual(result, (-90.0, -180.0))
    
    def test_validate_coordinates_invalid(self):
        """Test invalid coordinate validation."""
        # Test out of range latitude
        result = self.location_service.validate_coordinates(91, 0)
        self.assertIsNone(result)
        
        result = self.location_service.validate_coordinates(-91, 0)
        self.assertIsNone(result)
        
        # Test out of range longitude
        result = self.location_service.validate_coordinates(0, 181)
        self.assertIsNone(result)
        
        result = self.location_service.validate_coordinates(0, -181)
        self.assertIsNone(result)
    
    def test_validate_coordinates_invalid_types(self):
        """Test coordinate validation with invalid types."""
        # Test non-numeric inputs
        result = self.location_service.validate_coordinates("invalid", 0)
        self.assertIsNone(result)
        
        result = self.location_service.validate_coordinates(0, "invalid")
        self.assertIsNone(result)
        
        result = self.location_service.validate_coordinates(None, 0)
        self.assertIsNone(result)
    
    def test_validate_coordinates_string_numbers(self):
        """Test coordinate validation with string numbers."""
        result = self.location_service.validate_coordinates("40.7128", "-74.0060")
        self.assertEqual(result, (40.7128, -74.0060))

if __name__ == '__main__':
    unittest.main()