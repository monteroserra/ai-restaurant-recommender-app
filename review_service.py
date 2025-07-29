"""
Review Service for fetching restaurant reviews from Google Places API
"""
import json
import os
import time
import logging
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime, timedelta

from config import (
    GOOGLE_MAPS_API_KEY, GOOGLE_PLACES_BASE_URL, DEFAULT_REVIEW_COUNT,
    MAX_REVIEW_COUNT, REVIEW_CACHE_DURATION, CACHE_DIR, REVIEW_CACHE_FILE,
    MAX_RETRIES, REQUEST_TIMEOUT
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReviewService:
    def __init__(self):
        self.api_key = GOOGLE_MAPS_API_KEY
        self.cache_file = os.path.join(CACHE_DIR, REVIEW_CACHE_FILE)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load review cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
        return {}
    
    def _save_cache(self) -> None:
        """Save review cache to file."""
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _is_cache_valid(self, place_id: str) -> bool:
        """Check if cached reviews are still valid."""
        if place_id not in self.cache:
            return False
        
        cache_time = self.cache[place_id].get('timestamp', 0)
        return (time.time() - cache_time) < REVIEW_CACHE_DURATION
    
    def _make_request(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All request attempts failed for URL: {url}")
                    return None
        return None
    
    def get_restaurant_reviews(self, place_id: str, max_reviews: int = DEFAULT_REVIEW_COUNT) -> Dict[str, Any]:
        """
        Get reviews for a restaurant from Google Places API.
        
        Args:
            place_id: Google Places ID for the restaurant
            max_reviews: Maximum number of reviews to fetch
            
        Returns:
            Dictionary containing reviews and metadata
        """
        # Validate input
        if not place_id:
            return {"success": False, "error": "Invalid place_id"}
        
        max_reviews = min(max_reviews, MAX_REVIEW_COUNT)
        
        # Check cache first
        if self._is_cache_valid(place_id):
            logger.info(f"Using cached reviews for place_id: {place_id}")
            cached_data = self.cache[place_id]
            # Filter to requested number of reviews
            reviews = cached_data.get('reviews', [])[:max_reviews]
            return {
                "success": True,
                "reviews": reviews,
                "total_count": len(reviews),
                "from_cache": True,
                "place_id": place_id
            }
        
        # Fetch fresh reviews
        logger.info(f"Fetching fresh reviews for place_id: {place_id}")
        return self._fetch_reviews_from_api(place_id, max_reviews)
    
    def _fetch_reviews_from_api(self, place_id: str, max_reviews: int) -> Dict[str, Any]:
        """Fetch reviews from Google Places API."""
        # Get place details with reviews
        url = f"{GOOGLE_PLACES_BASE_URL}/details/json"
        params = {
            'place_id': place_id,
            'fields': 'name,reviews,rating,user_ratings_total',
            'key': self.api_key,
            'reviews_sort': 'newest'  # Get most recent reviews
        }
        
        response_data = self._make_request(url, params)
        
        if not response_data:
            return {"success": False, "error": "Failed to fetch data from API"}
        
        if response_data.get('status') != 'OK':
            error_msg = response_data.get('error_message', f"API Error: {response_data.get('status')}")
            logger.error(f"Google Places API error: {error_msg}")
            return {"success": False, "error": error_msg}
        
        result = response_data.get('result', {})
        raw_reviews = result.get('reviews', [])
        
        if not raw_reviews:
            return {"success": False, "error": "No reviews found for this restaurant"}
        
        # Process and clean reviews
        processed_reviews = self._process_reviews(raw_reviews, max_reviews)
        
        # Cache the results
        self.cache[place_id] = {
            'reviews': processed_reviews,
            'restaurant_name': result.get('name', 'Unknown'),
            'overall_rating': result.get('rating', 0),
            'total_ratings': result.get('user_ratings_total', 0),
            'timestamp': time.time()
        }
        self._save_cache()
        
        return {
            "success": True,
            "reviews": processed_reviews[:max_reviews],
            "total_count": len(processed_reviews),
            "restaurant_name": result.get('name', 'Unknown'),
            "overall_rating": result.get('rating', 0),
            "total_ratings": result.get('user_ratings_total', 0),
            "from_cache": False,
            "place_id": place_id
        }
    
    def _process_reviews(self, raw_reviews: List[Dict], max_reviews: int) -> List[Dict[str, Any]]:
        """Process and clean raw review data."""
        processed_reviews = []
        
        for review in raw_reviews[:max_reviews]:
            try:
                processed_review = {
                    'text': review.get('text', '').strip(),
                    'rating': review.get('rating', 0),
                    'author_name': review.get('author_name', 'Anonymous'),
                    'time': review.get('time', 0),
                    'relative_time_description': review.get('relative_time_description', ''),
                    'language': review.get('language', 'en')
                }
                
                # Only include reviews with text content
                if processed_review['text'] and len(processed_review['text']) > 10:
                    processed_reviews.append(processed_review)
                    
            except Exception as e:
                logger.warning(f"Error processing review: {e}")
                continue
        
        # Sort by time (newest first)
        processed_reviews.sort(key=lambda x: x.get('time', 0), reverse=True)
        
        return processed_reviews
    
    def clear_cache(self, place_id: str = None) -> bool:
        """Clear review cache for specific place or all places."""
        try:
            if place_id:
                if place_id in self.cache:
                    del self.cache[place_id]
                    self._save_cache()
                    logger.info(f"Cleared cache for place_id: {place_id}")
            else:
                self.cache = {}
                self._save_cache()
                logger.info("Cleared entire review cache")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached reviews."""
        total_places = len(self.cache)
        total_reviews = sum(len(data.get('reviews', [])) for data in self.cache.values())
        
        # Check for expired entries
        current_time = time.time()
        expired_count = sum(
            1 for data in self.cache.values()
            if (current_time - data.get('timestamp', 0)) > REVIEW_CACHE_DURATION
        )
        
        return {
            'total_places_cached': total_places,
            'total_reviews_cached': total_reviews,
            'expired_entries': expired_count,
            'cache_file_exists': os.path.exists(self.cache_file)
        }
    
    def validate_reviews_data(self, reviews_data: Dict[str, Any]) -> bool:
        """Validate reviews data structure."""
        if not isinstance(reviews_data, dict):
            return False
        
        if not reviews_data.get('success', False):
            return False
        
        reviews = reviews_data.get('reviews', [])
        if not isinstance(reviews, list) or len(reviews) == 0:
            return False
        
        # Check if reviews have required fields
        for review in reviews[:3]:  # Check first 3 reviews
            if not isinstance(review, dict):
                return False
            if not review.get('text') or not isinstance(review.get('rating'), (int, float)):
                return False
        
        return True

# Create global instance
review_service = ReviewService()