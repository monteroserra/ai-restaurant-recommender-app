"""
Restaurant Analyzer - Orchestrates the review fetching and analysis workflow
"""
import logging
import time
from typing import Dict, Any, Optional, Callable
from threading import Thread

from review_service import review_service
from analysis_service import analysis_service
from config import DEFAULT_REVIEW_COUNT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RestaurantAnalyzer:
    def __init__(self):
        self.review_service = review_service
        self.analysis_service = analysis_service
        self.current_analysis = None
        self.is_analyzing = False
    
    def analyze_restaurant(
        self, 
        place_id: str, 
        restaurant_name: str = "",
        max_reviews: int = DEFAULT_REVIEW_COUNT,
        progress_callback: Optional[Callable[[str, float], None]] = None,
        completion_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Complete analysis workflow for a restaurant.
        
        Args:
            place_id: Google Places ID
            restaurant_name: Restaurant name for context
            max_reviews: Maximum number of reviews to analyze
            progress_callback: Callback for progress updates (message, progress_percent)
            completion_callback: Callback when analysis is complete
            
        Returns:
            Analysis result dictionary
        """
        if self.is_analyzing:
            return {"success": False, "error": "Analysis already in progress"}
        
        self.is_analyzing = True
        
        try:
            # Step 1: Fetch reviews
            if progress_callback:
                progress_callback("Fetching restaurant reviews...", 10)
            
            logger.info(f"Starting analysis for place_id: {place_id}")
            
            reviews_result = self.review_service.get_restaurant_reviews(
                place_id=place_id,
                max_reviews=max_reviews
            )
            
            if not reviews_result.get('success', False):
                error_msg = reviews_result.get('error', 'Failed to fetch reviews')
                logger.error(f"Review fetch failed: {error_msg}")
                return {"success": False, "error": error_msg, "stage": "review_fetch"}
            
            reviews = reviews_result.get('reviews', [])
            if not reviews:
                return {"success": False, "error": "No reviews found", "stage": "review_fetch"}
            
            # Update restaurant name if available
            if not restaurant_name:
                restaurant_name = reviews_result.get('restaurant_name', 'Unknown Restaurant')
            
            if progress_callback:
                progress_callback(f"Analyzing {len(reviews)} reviews...", 50)
            
            # Step 2: Analyze reviews
            analysis_result = self.analysis_service.analyze_reviews(
                reviews=reviews,
                restaurant_name=restaurant_name
            )
            
            if not analysis_result.get('success', False):
                error_msg = analysis_result.get('error', 'Failed to analyze reviews')
                logger.error(f"Analysis failed: {error_msg}")
                return {"success": False, "error": error_msg, "stage": "analysis"}
            
            if progress_callback:
                progress_callback("Analysis complete!", 100)
            
            # Step 3: Combine results
            final_result = {
                "success": True,
                "place_id": place_id,
                "restaurant_name": restaurant_name,
                "review_data": {
                    "total_reviews": len(reviews),
                    "overall_rating": reviews_result.get('overall_rating', 0),
                    "total_ratings": reviews_result.get('total_ratings', 0),
                    "from_cache": reviews_result.get('from_cache', False)
                },
                "analysis": analysis_result.get('analysis', {}),
                "analysis_from_cache": analysis_result.get('from_cache', False),
                "timestamp": time.time()
            }
            
            # Store current analysis
            self.current_analysis = final_result
            
            # Call completion callback if provided
            if completion_callback:
                completion_callback(final_result)
            
            logger.info(f"Analysis completed successfully for: {restaurant_name}")
            return final_result
            
        except Exception as e:
            error_msg = f"Unexpected error during analysis: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "stage": "unexpected"}
        
        finally:
            self.is_analyzing = False
    
    def analyze_restaurant_async(
        self,
        place_id: str,
        restaurant_name: str = "",
        max_reviews: int = DEFAULT_REVIEW_COUNT,
        progress_callback: Optional[Callable[[str, float], None]] = None,
        completion_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        Run analysis in a separate thread (for GUI applications).
        
        Args:
            place_id: Google Places ID
            restaurant_name: Restaurant name
            max_reviews: Maximum reviews to analyze
            progress_callback: Progress update callback
            completion_callback: Success callback
            error_callback: Error callback
        """
        def run_analysis():
            try:
                result = self.analyze_restaurant(
                    place_id=place_id,
                    restaurant_name=restaurant_name,
                    max_reviews=max_reviews,
                    progress_callback=progress_callback,
                    completion_callback=completion_callback
                )
                
                if not result.get('success', False) and error_callback:
                    error_callback(result.get('error', 'Analysis failed'))
                    
            except Exception as e:
                if error_callback:
                    error_callback(f"Analysis error: {str(e)}")
                logger.error(f"Async analysis error: {e}")
        
        # Start analysis in background thread
        analysis_thread = Thread(target=run_analysis, daemon=True)
        analysis_thread.start()
    
    def get_analysis_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """
        Get a formatted summary of the analysis for display.
        
        Args:
            analysis_result: Result from analyze_restaurant
            
        Returns:
            Dictionary with formatted summary sections
        """
        if not analysis_result.get('success', False):
            return {
                "title": "Analysis Failed",
                "error": analysis_result.get('error', 'Unknown error'),
                "stage": analysis_result.get('stage', 'unknown')
            }
        
        analysis = analysis_result.get('analysis', {})
        review_data = analysis_result.get('review_data', {})
        
        # Format highlights
        highlights = analysis.get('highlights', [])
        highlights_text = '\n'.join(f"• {h}" for h in highlights[:5]) if highlights else "None mentioned"
        
        # Format complaints
        complaints = analysis.get('complaints', [])
        complaints_text = '\n'.join(f"• {c}" for c in complaints[:4]) if complaints else "None mentioned"
        
        # Format best dishes
        best_dishes = analysis.get('best_dishes', [])
        dishes_text = ', '.join(best_dishes[:3]) if best_dishes else "Not mentioned"
        
        return {
            "restaurant_name": analysis_result.get('restaurant_name', 'Unknown'),
            "total_reviews": f"{review_data.get('total_reviews', 0)} reviews analyzed",
            "overall_rating": f"{review_data.get('overall_rating', 0):.1f}/5.0",
            "cuisine_type": analysis.get('cuisine_type', 'Not specified'),
            "price_range": analysis.get('price_range', 'Not mentioned'),
            "ambience": analysis.get('ambience', 'Not described'),
            "highlights": highlights_text,
            "complaints": complaints_text,
            "best_dishes": dishes_text,
            "service_quality": analysis.get('service_quality', 'Not mentioned'),
            "overall_sentiment": analysis.get('overall_sentiment', 'Mixed'),
            "from_cache": "Yes" if analysis_result.get('analysis_from_cache', False) else "No"
        }
    
    def validate_place_id(self, place_id: str) -> bool:
        """Validate if place_id format is correct."""
        if not place_id or not isinstance(place_id, str):
            return False
        
        # Basic validation - Google Place IDs are typically alphanumeric with some special chars
        if len(place_id) < 10 or len(place_id) > 200:
            return False
        
        return True
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get status of all caches."""
        review_cache = self.review_service.get_cache_info()
        analysis_cache = self.analysis_service.get_cache_info()
        
        return {
            "reviews": review_cache,
            "analysis": analysis_cache,
            "current_analysis_available": self.current_analysis is not None,
            "is_analyzing": self.is_analyzing
        }
    
    def clear_all_caches(self) -> Dict[str, bool]:
        """Clear all caches."""
        results = {
            "reviews_cleared": self.review_service.clear_cache(),
            "analysis_cleared": self.analysis_service.clear_cache()
        }
        
        # Clear current analysis
        self.current_analysis = None
        
        logger.info("All caches cleared")
        return results
    
    def export_analysis(self, analysis_result: Dict[str, Any], format: str = 'json') -> str:
        """
        Export analysis result in specified format.
        
        Args:
            analysis_result: Analysis result to export
            format: Export format ('json', 'text')
            
        Returns:
            Formatted string
        """
        if format.lower() == 'json':
            import json
            return json.dumps(analysis_result, indent=2, ensure_ascii=False)
        
        elif format.lower() == 'text':
            summary = self.get_analysis_summary(analysis_result)
            
            text_export = f"""
Restaurant Analysis Report
==========================

Restaurant: {summary.get('restaurant_name', 'Unknown')}
Overall Rating: {summary.get('overall_rating', 'N/A')}
Reviews Analyzed: {summary.get('total_reviews', 'N/A')}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

Cuisine & Atmosphere
-------------------
Cuisine Type: {summary.get('cuisine_type', 'Not specified')}
Price Range: {summary.get('price_range', 'Not mentioned')}
Ambience: {summary.get('ambience', 'Not described')}

Customer Highlights
------------------
{summary.get('highlights', 'None mentioned')}

Main Complaints
--------------
{summary.get('complaints', 'None mentioned')}

Recommended Dishes
-----------------
{summary.get('best_dishes', 'Not mentioned')}

Service Quality
--------------
{summary.get('service_quality', 'Not mentioned')}

Overall Sentiment
----------------
{summary.get('overall_sentiment', 'Mixed')}
            """.strip()
            
            return text_export
        
        else:
            return "Unsupported export format"

# Create global instance
restaurant_analyzer = RestaurantAnalyzer()