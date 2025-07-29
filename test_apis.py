#!/usr/bin/env python3
"""
API Connection Test Script
Tests Google Maps API and Gemini API connections independently
"""
import requests
import json
from config import (
    GOOGLE_MAPS_API_KEY, GEMINI_API_KEY, 
    GOOGLE_PLACES_BASE_URL, validate_config
)

def test_google_maps_api():
    """Test Google Maps Places API connection."""
    print("Testing Google Maps API...")
    print("-" * 30)
    
    try:
        # Test with a simple place search
        url = f"{GOOGLE_PLACES_BASE_URL}/nearbysearch/json"
        params = {
            'location': '40.7128,-74.0060',  # NYC
            'radius': 1000,
            'type': 'restaurant',
            'key': GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API Status: {data.get('status')}")
            
            if data.get('status') == 'OK':
                results = data.get('results', [])
                print(f"✅ Google Maps API: Working! Found {len(results)} restaurants")
                if results:
                    print(f"Sample restaurant: {results[0].get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ Google Maps API Error: {data.get('error_message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Google Maps API Test Failed: {e}")
        return False

def test_gemini_api():
    """Test Gemini API connection with multiple configurations."""
    print("\nTesting Gemini API...")
    print("-" * 30)
    
    # Test different model names and endpoints
    test_configs = [
        {
            "name": "Gemini 1.5 Flash (v1beta)",
            "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            "model": "gemini-1.5-flash",
            "auth": "header"
        },
        {
            "name": "Gemini 1.5 Pro (v1beta)",
            "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent",
            "model": "gemini-1.5-pro", 
            "auth": "header"
        },
        {
            "name": "Gemini Pro (v1beta)",
            "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            "model": "gemini-pro",
            "auth": "header"
        },
        {
            "name": "Gemini 1.5 Flash (param auth)",
            "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            "model": "gemini-1.5-flash",
            "auth": "param"
        }
    ]
    
    payload = {
        "contents": [{
            "parts": [{
                "text": "Respond with exactly this JSON: {\"test\": \"success\", \"message\": \"API is working\"}"
            }]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 100
        }
    }
    
    for config in test_configs:
        print(f"\nTrying {config['name']}...")
        
        try:
            headers = {'Content-Type': 'application/json'}
            params = {}
            
            if config['auth'] == 'header':
                headers['x-goog-api-key'] = GEMINI_API_KEY
            else:
                params['key'] = GEMINI_API_KEY
            
            response = requests.post(
                config['url'],
                headers=headers,
                params=params if params else None,
                json=payload,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Gemini API: Working!")
                
                # Try to extract response text
                try:
                    candidates = data.get('candidates', [])
                    if candidates:
                        content = candidates[0].get('content', {})
                        parts = content.get('parts', [])
                        if parts:
                            text = parts[0].get('text', '')
                            print(f"Response: {text[:100]}...")
                except:
                    print("Response structure looks different than expected")
                    print(f"Raw response: {json.dumps(data, indent=2)[:200]}...")
                
                return True
                
            elif response.status_code == 403:
                print("❌ 403 Forbidden - Check API key permissions")
            elif response.status_code == 404:
                print("❌ 404 Not Found - Invalid endpoint or model name")
            elif response.status_code == 429:
                print("❌ 429 Rate Limited - Too many requests")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print("❌ All Gemini API configurations failed")
    return False

def test_restaurant_analysis_workflow():
    """Test the complete workflow with a real restaurant."""
    print("\nTesting Complete Workflow...")
    print("-" * 30)
    
    try:
        # First get a restaurant
        print("1. Finding a restaurant...")
        from restaurant_service import restaurant_service
        
        restaurants = restaurant_service.find_restaurants(
            latitude=40.7128,
            longitude=-74.0060,
            radius=1000,
            min_reviews=50,
            max_results=1
        )
        
        if not restaurants:
            print("❌ No restaurants found")
            return False
        
        restaurant = restaurants[0]
        print(f"✅ Found restaurant: {restaurant['name']}")
        
        # Get reviews
        print("2. Fetching reviews...")
        from review_service import review_service
        
        reviews_result = review_service.get_restaurant_reviews(
            restaurant['place_id'], 
            max_reviews=5  # Small number for testing
        )
        
        if not reviews_result.get('success'):
            print(f"❌ Failed to fetch reviews: {reviews_result.get('error')}")
            return False
        
        reviews = reviews_result.get('reviews', [])
        print(f"✅ Fetched {len(reviews)} reviews")
        
        # Test analysis
        print("3. Testing analysis...")
        from analysis_service import analysis_service
        
        analysis_result = analysis_service.analyze_reviews(
            reviews=reviews[:3],  # Use just 3 reviews for testing
            restaurant_name=restaurant['name']
        )
        
        if analysis_result.get('success'):
            print("✅ Analysis completed successfully!")
            analysis = analysis_result.get('analysis', {})
            print(f"Cuisine: {analysis.get('cuisine_type', 'N/A')}")
            print(f"Sentiment: {analysis.get('overall_sentiment', 'N/A')}")
            return True
        else:
            print(f"❌ Analysis failed: {analysis_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def main():
    """Run all API tests."""
    print("🍽️ AI Restaurant Recommender - API Test Suite")
    print("=" * 50)
    
    # Check configuration
    print("Checking configuration...")
    config_status = validate_config()
    
    if not config_status['valid']:
        print("❌ Configuration issues found:")
        for issue in config_status['issues']:
            print(f"  - {issue}")
        print("\nPlease fix these issues before running tests.")
        return
    
    print("✅ Configuration looks good")
    
    # Test APIs individually
    google_ok = test_google_maps_api()
    gemini_ok = test_gemini_api()
    
    # Test complete workflow if both APIs work
    if google_ok and gemini_ok:
        workflow_ok = test_restaurant_analysis_workflow()
    else:
        workflow_ok = False
        print("\nSkipping workflow test due to API failures")
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print(f"Google Maps API: {'✅ PASS' if google_ok else '❌ FAIL'}")
    print(f"Gemini API: {'✅ PASS' if gemini_ok else '❌ FAIL'}")
    print(f"Complete Workflow: {'✅ PASS' if workflow_ok else '❌ FAIL'}")
    
    if google_ok and gemini_ok and workflow_ok:
        print("\n🎉 All tests passed! Your app should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        
        if not gemini_ok:
            print("\nGemini API troubleshooting:")
            print("1. Verify your API key is correct")
            print("2. Check if the API key has proper permissions")
            print("3. Try visiting https://makersuite.google.com/app/apikey")
            print("4. Make sure you're using the latest Gemini API")

if __name__ == "__main__":
    main()