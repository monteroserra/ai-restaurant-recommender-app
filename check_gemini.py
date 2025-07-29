#!/usr/bin/env python3
"""
Quick Gemini API availability checker
"""
import requests
import time
from config import GEMINI_API_KEY

def quick_gemini_test():
    """Quick test to see if Gemini API is available."""
    
    print("🤖 Quick Gemini API Test")
    print("-" * 30)
    
    # Simple test payload
    payload = {
        "contents": [{
            "parts": [{
                "text": "Say 'working' if you can read this."
            }]
        }],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 10
        }
    }
    
    # Try different endpoints
    endpoints = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent",
    ]
    
    for i, url in enumerate(endpoints, 1):
        model_name = url.split('/')[-1].split(':')[0]
        print(f"\n{i}. Testing {model_name}...")
        
        try:
            response = requests.post(
                url,
                headers={
                    'Content-Type': 'application/json',
                    'x-goog-api-key': GEMINI_API_KEY
                },
                json=payload,
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ WORKING! Gemini API is available")
                return True
            elif response.status_code == 429:
                print("   ⏳ Rate limited - try again later")
                # Try to get rate limit reset time from headers
                if 'retry-after' in response.headers:
                    retry_after = response.headers['retry-after']
                    print(f"   Retry after: {retry_after} seconds")
            elif response.status_code == 403:
                print("   ❌ Forbidden - check API key")
            elif response.status_code == 404:
                print("   ❌ Not found - model unavailable")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ⏳ Timeout - server might be slow")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n❌ All endpoints failed")
    return False

def monitor_api_status():
    """Monitor API status until it becomes available."""
    print("\n🔄 Monitoring Gemini API status...")
    print("Press Ctrl+C to stop")
    
    check_interval = 30  # seconds
    
    try:
        while True:
            print(f"\n[{time.strftime('%H:%M:%S')}] Checking...")
            
            if quick_gemini_test():
                print("\n🎉 API is working! You can now use the restaurant app.")
                break
            
            print(f"💤 Waiting {check_interval} seconds before next check...")
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")

if __name__ == "__main__":
    print("Gemini API Status Checker")
    print("========================")
    
    # Do initial test
    if quick_gemini_test():
        print("\n🎉 Great! Your app should work now.")
    else:
        print("\n⏳ API not available right now.")
        
        choice = input("\nWould you like to monitor until it's available? (y/n): ")
        if choice.lower().startswith('y'):
            monitor_api_status()
        else:
            print("\n💡 Tips while waiting:")
            print("• Rate limits usually reset within 1-24 hours")
            print("• The app will work with basic analysis in the meantime")
            print("• You can run this script again later: python check_gemini.py")