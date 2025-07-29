"""
Analysis Service for processing restaurant reviews using Gemini AI
"""
import json
import os
import time
import logging
import re
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime

from config import (
    GEMINI_API_KEY, GEMINI_API_BASE_URL, GEMINI_ANALYSIS_PROMPT,
    ANALYSIS_CACHE_DURATION, CACHE_DIR, ANALYSIS_CACHE_FILE,
    MAX_RETRIES, REQUEST_TIMEOUT
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.cache_file = os.path.join(CACHE_DIR, ANALYSIS_CACHE_FILE)
        self.cache = self._load_cache()
        self.model_name = "gemini-1.5-flash"  # Updated to current model name
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load analysis cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading analysis cache: {e}")
        return {}
    
    def _save_cache(self) -> None:
        """Save analysis cache to file."""
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving analysis cache: {e}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached analysis is still valid."""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key].get('timestamp', 0)
        return (time.time() - cache_time) < ANALYSIS_CACHE_DURATION
    
    def _generate_cache_key(self, reviews: List[Dict[str, Any]]) -> str:
        """Generate a unique cache key for reviews."""
        # Create a hash based on review texts and ratings
        review_signature = ""
        for review in reviews[:10]:  # Use first 10 reviews for signature
            text = review.get('text', '')[:100]  # First 100 chars
            rating = review.get('rating', 0)
            review_signature += f"{text}{rating}"
        
        # Simple hash function
        return str(hash(review_signature))
    
    def _make_gemini_request(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Make request to Gemini API with retry logic."""
        # Updated API configs with working endpoints
        api_configs = [
            {
                "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                "auth_method": "header",
                "model": "gemini-1.5-flash"
            },
            {
                "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent",
                "auth_method": "header", 
                "model": "gemini-1.0-pro"
            },
            {
                "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                "auth_method": "param",
                "model": "gemini-1.5-flash"
            }
        ]
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,  # Reduced for rate limits
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        for config in api_configs:
            logger.info(f"Trying Gemini model: {config['model']}")
            
            for attempt in range(MAX_RETRIES):
                try:
                    headers = {'Content-Type': 'application/json'}
                    params = {}
                    
                    if config["auth_method"] == "header":
                        headers['x-goog-api-key'] = self.api_key
                    else:
                        params['key'] = self.api_key
                    
                    # Longer timeout for slow responses
                    timeout = 60 if attempt == 0 else 30
                    
                    response = requests.post(
                        config["url"], 
                        headers=headers,
                        params=params if params else None,
                        json=payload,
                        timeout=timeout
                    )
                    
                    logger.info(f"Gemini API response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        logger.info("✅ Gemini API request successful!")
                        return response.json()
                    elif response.status_code == 429:
                        wait_time = min(60 * (attempt + 1), 300)  # Wait 1-5 minutes
                        logger.warning(f"Rate limited. Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    elif response.status_code == 404:
                        logger.warning(f"Model {config['model']} not found, trying next...")
                        break  # Try next config
                    elif response.status_code == 403:
                        logger.error("Gemini API 403 error. Check API key permissions")
                        return None
                    else:
                        logger.warning(f"HTTP {response.status_code}: {response.text[:200]}")
                        if attempt < MAX_RETRIES - 1:
                            time.sleep(5)
                            continue
                        break
                    
                except requests.exceptions.Timeout:
                    logger.warning(f"Request timeout on attempt {attempt + 1}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(10)  # Wait before retry
                        continue
                    break
                    
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request failed on attempt {attempt + 1}: {e}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(2 ** attempt)
                        continue
                    break
        
        logger.error("All Gemini API attempts failed")
        return None
    
    def analyze_reviews(self, reviews: List[Dict[str, Any]], restaurant_name: str = "") -> Dict[str, Any]:
        """
        Analyze restaurant reviews using Gemini AI.
        
        Args:
            reviews: List of review dictionaries
            restaurant_name: Name of the restaurant (optional)
            
        Returns:
            Dictionary containing structured analysis
        """
        if not reviews or len(reviews) == 0:
            return {"success": False, "error": "No reviews provided for analysis"}
        
        # Check cache first
        cache_key = self._generate_cache_key(reviews)
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached analysis for key: {cache_key}")
            cached_data = self.cache[cache_key]
            return {
                "success": True,
                "analysis": cached_data['analysis'],
                "from_cache": True,
                "review_count": len(reviews),
                "restaurant_name": restaurant_name
            }
        
        # Prepare reviews text for analysis
        reviews_text = self._prepare_reviews_text(reviews)
        
        if not reviews_text.strip():
            return {"success": False, "error": "No valid review text found"}
        
        # Create the prompt
        prompt = GEMINI_ANALYSIS_PROMPT.format(reviews_text=reviews_text)
        
        # Make API request
        logger.info(f"Analyzing {len(reviews)} reviews with Gemini AI")
        response = self._make_gemini_request(prompt)
        
        if not response:
            # Fallback to basic analysis when API fails
            logger.warning("Gemini API failed, using fallback analysis")
            analysis = self._create_fallback_analysis(reviews, restaurant_name)
            
            # Cache the fallback results (shorter duration)
            self.cache[cache_key] = {
                'analysis': analysis,
                'timestamp': time.time(),
                'review_count': len(reviews),
                'restaurant_name': restaurant_name,
                'fallback_used': True
            }
            self._save_cache()
            
            return {
                "success": True,
                "analysis": analysis,
                "from_cache": False,
                "review_count": len(reviews),
                "restaurant_name": restaurant_name,
                "fallback_used": True,
                "message": "Using basic analysis due to API limitations"
            }
        
        # Process the response
        analysis = self._process_gemini_response(response)
        
        if not analysis:
            # Fallback if response processing fails
            logger.warning("Failed to process Gemini response, using fallback")
            analysis = self._create_fallback_analysis(reviews, restaurant_name)
        
        # Cache the results
        self.cache[cache_key] = {
            'analysis': analysis,
            'timestamp': time.time(),
            'review_count': len(reviews),
            'restaurant_name': restaurant_name,
            'fallback_used': analysis.get('fallback_used', False)
        }
        self._save_cache()
        
        return {
            "success": True,
            "analysis": analysis,
            "from_cache": False,
            "review_count": len(reviews),
            "restaurant_name": restaurant_name,
            "fallback_used": analysis.get('fallback_used', False)
        }
    
    def _prepare_reviews_text(self, reviews: List[Dict[str, Any]]) -> str:
        """Prepare review text for analysis."""
        reviews_text = ""
        
        for i, review in enumerate(reviews, 1):
            text = review.get('text', '').strip()
            rating = review.get('rating', 0)
            
            if text and len(text) > 10:  # Only include substantial reviews
                # Clean the text
                text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                text = text.replace('\n', ' ').replace('\r', ' ')
                
                reviews_text += f"Review {i} (Rating: {rating}/5): {text}\n\n"
        
        return reviews_text
    
    def _process_gemini_response(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process and validate Gemini API response."""
        try:
            # Extract the generated text
            candidates = response.get('candidates', [])
            if not candidates:
                logger.error("No candidates in Gemini response")
                return None
            
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])
            if not parts:
                logger.error("No parts in Gemini response")
                return None
            
            generated_text = parts[0].get('text', '')
            if not generated_text:
                logger.error("No text in Gemini response")
                return None
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                try:
                    analysis = json.loads(json_str)
                    return self._validate_and_clean_analysis(analysis)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from Gemini response: {e}")
            
            # If JSON extraction fails, try to parse the entire response
            try:
                analysis = json.loads(generated_text)
                return self._validate_and_clean_analysis(analysis)
            except json.JSONDecodeError:
                # Fallback: create structured response from text
                return self._create_fallback_analysis(generated_text)
        
        except Exception as e:
            logger.error(f"Error processing Gemini response: {e}")
            return None
    
    def _validate_and_clean_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the analysis response."""
        cleaned_analysis = {
            'cuisine_type': str(analysis.get('cuisine_type', 'Not specified')),
            'ambience': str(analysis.get('ambience', 'Not described')),
            'highlights': [],
            'complaints': [],
            'overall_sentiment': str(analysis.get('overall_sentiment', 'Mixed')),
            'price_range': str(analysis.get('price_range', 'Not mentioned')),
            'best_dishes': [],
            'service_quality': str(analysis.get('service_quality', 'Not mentioned'))
        }
        
        # Clean highlights
        highlights = analysis.get('highlights', [])
        if isinstance(highlights, list):
            cleaned_analysis['highlights'] = [str(h).strip() for h in highlights[:5] if h and str(h).strip()]
        
        # Clean complaints
        complaints = analysis.get('complaints', [])
        if isinstance(complaints, list):
            cleaned_analysis['complaints'] = [str(c).strip() for c in complaints[:4] if c and str(c).strip()]
        
        # Clean best dishes
        best_dishes = analysis.get('best_dishes', [])
        if isinstance(best_dishes, list):
            cleaned_analysis['best_dishes'] = [str(d).strip() for d in best_dishes[:3] if d and str(d).strip()]
        
        return cleaned_analysis
    
    def _create_fallback_analysis(self, reviews: List[Dict[str, Any]], restaurant_name: str = "") -> Dict[str, Any]:
        """Create a fallback analysis when Gemini API is unavailable."""
        if not reviews:
            return self._get_empty_analysis()
        
        # Basic keyword analysis
        review_texts = [review.get('text', '').lower() for review in reviews]
        all_text = ' '.join(review_texts)
        
        # Cuisine detection
        cuisine_keywords = {
            'Italian': ['pizza', 'pasta', 'italian', 'marinara', 'parmesan', 'lasagna', 'risotto'],
            'Chinese': ['chinese', 'noodles', 'dim sum', 'wok', 'stir fry', 'kung pao', 'sweet sour'],
            'Mexican': ['mexican', 'tacos', 'burrito', 'salsa', 'guacamole', 'quesadilla', 'nachos'],
            'Japanese': ['sushi', 'ramen', 'japanese', 'tempura', 'miso', 'sashimi', 'teriyaki'],
            'American': ['burger', 'fries', 'bbq', 'steak', 'american', 'wings', 'sandwich'],
            'Indian': ['indian', 'curry', 'tandoor', 'naan', 'biryani', 'masala', 'spicy'],
            'Thai': ['thai', 'pad thai', 'coconut', 'lemongrass', 'curry', 'tom yum'],
            'French': ['french', 'croissant', 'wine', 'cheese', 'baguette', 'escargot']
        }
        
        detected_cuisine = 'Not specified'
        max_matches = 0
        for cuisine, keywords in cuisine_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in all_text)
            if matches > max_matches:
                max_matches = matches
                detected_cuisine = cuisine
        
        # Sentiment analysis - basic
        positive_words = ['great', 'excellent', 'amazing', 'delicious', 'fantastic', 'wonderful', 
                         'love', 'best', 'perfect', 'outstanding', 'incredible', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disgusting', 'worst', 
                         'hate', 'disappointing', 'poor', 'rude', 'slow', 'dirty']
        
        positive_count = sum(1 for word in positive_words if word in all_text)
        negative_count = sum(1 for word in negative_words if word in all_text)
        
        if positive_count > negative_count * 2:
            sentiment = "Very positive"
        elif positive_count > negative_count:
            sentiment = "Positive"
        elif negative_count > positive_count:
            sentiment = "Mixed with concerns"
        else:
            sentiment = "Mixed"
        
        # Extract highlights and complaints
        highlights = []
        complaints = []
        
        # Common positive phrases
        if 'great service' in all_text or 'excellent service' in all_text:
            highlights.append("Excellent customer service")
        if 'delicious food' in all_text or 'amazing food' in all_text:
            highlights.append("Delicious food")
        if 'good atmosphere' in all_text or 'nice ambiance' in all_text:
            highlights.append("Pleasant atmosphere")
        if 'good value' in all_text or 'reasonable price' in all_text:
            highlights.append("Good value for money")
        if 'friendly staff' in all_text:
            highlights.append("Friendly staff")
        
        # Common complaints
        if 'slow service' in all_text:
            complaints.append("Slow service")
        if 'expensive' in all_text or 'overpriced' in all_text:
            complaints.append("High prices")
        if 'noisy' in all_text or 'loud' in all_text:
            complaints.append("Noisy environment")
        if 'rude' in all_text:
            complaints.append("Unfriendly service")
        if 'wait' in all_text and 'long' in all_text:
            complaints.append("Long wait times")
        
        # Default messages if nothing found
        if not highlights:
            highlights = ["Analysis unavailable - please try again later"]
        if not complaints:
            complaints = ["No major complaints identified"]
        
        # Price estimation
        price_range = "Not mentioned"
        if 'expensive' in all_text or 'pricey' in all_text:
            price_range = "$$ - Expensive"
        elif 'cheap' in all_text or 'affordable' in all_text:
            price_range = "$ - Inexpensive"
        elif 'reasonable' in all_text:
            price_range = "$ - Moderate"
        
        return {
            'cuisine_type': detected_cuisine,
            'ambience': 'Analysis temporarily unavailable due to high demand. Please try again later.',
            'highlights': highlights[:5],
            'complaints': complaints[:4],
            'overall_sentiment': sentiment,
            'price_range': price_range,
            'best_dishes': ['Analysis unavailable'],
            'service_quality': 'Basic analysis: Check individual reviews for service details',
            'fallback_used': True
        }
    
    def _get_empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            'cuisine_type': 'Not specified',
            'ambience': 'No reviews available for analysis',
            'highlights': ['No reviews to analyze'],
            'complaints': ['No reviews to analyze'],
            'overall_sentiment': 'No data available',
            'price_range': 'Not available',
            'best_dishes': ['Not available'],
            'service_quality': 'No data available',
            'fallback_used': True
        }
    
    def clear_cache(self, cache_key: str = None) -> bool:
        """Clear analysis cache for specific key or all analyses."""
        try:
            if cache_key:
                if cache_key in self.cache:
                    del self.cache[cache_key]
                    self._save_cache()
                    logger.info(f"Cleared analysis cache for key: {cache_key}")
            else:
                self.cache = {}
                self._save_cache()
                logger.info("Cleared entire analysis cache")
            return True
        except Exception as e:
            logger.error(f"Error clearing analysis cache: {e}")
            return False
    
    def test_gemini_connection(self) -> Dict[str, Any]:
        """Test connection to Gemini API with a simple request."""
        test_prompt = "Say 'Hello, this is a test' in JSON format: {\"message\": \"your response\"}"
        
        try:
            logger.info("Testing Gemini API connection...")
            response = self._make_gemini_request(test_prompt)
            
            if response:
                logger.info("Gemini API test successful!")
                return {
                    "success": True,
                    "message": "Gemini API connection working",
                    "response": response
                }
            else:
                logger.error("Gemini API test failed - no response")
                return {
                    "success": False,
                    "message": "Gemini API connection failed - no response"
                }
        except Exception as e:
            logger.error(f"Gemini API test error: {e}")
            return {
                "success": False,
                "message": f"Gemini API test error: {str(e)}"
            }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached analyses."""
        total_analyses = len(self.cache)
        
        # Check for expired entries
        current_time = time.time()
        expired_count = sum(
            1 for data in self.cache.values()
            if (current_time - data.get('timestamp', 0)) > ANALYSIS_CACHE_DURATION
        )
        
        return {
            'total_analyses_cached': total_analyses,
            'expired_entries': expired_count,
            'cache_file_exists': os.path.exists(self.cache_file)
        }

# Create global instance
analysis_service = AnalysisService()