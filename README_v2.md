# 🍽️ AI Restaurant Recommender with Review Analysis

A sophisticated Python application that finds nearby restaurants and provides AI-powered analysis of customer reviews using Google Maps API and Gemini AI. Available in both desktop (Tkinter) and web (Flask) versions.

## ✨ Features

### Core Functionality
- 🔍 **Smart Restaurant Search**: Find restaurants by coordinates or address
- 📊 **AI Review Analysis**: Deep analysis of customer reviews using Gemini AI
- 🎯 **Flexible Location Input**: Use coordinates or street addresses
- 📈 **Advanced Filtering**: Configurable search radius, minimum reviews, and result limits
- 💾 **Intelligent Caching**: Reduces API calls and improves performance

### AI Analysis Features
- 🍴 **Cuisine Classification**: Automatically identifies cuisine type and style
- 🏮 **Ambience Analysis**: Describes restaurant atmosphere from reviews
- ✨ **Customer Highlights**: Extracts top positive aspects mentioned by customers
- ⚠️ **Common Complaints**: Identifies main issues and concerns
- 🍽️ **Recommended Dishes**: Lists most frequently praised menu items
- 💰 **Price Range Detection**: Estimates pricing based on customer feedback
- 👥 **Service Quality Assessment**: Analyzes service quality mentions

### Interface Options
- 🖥️ **Desktop App**: Full-featured Tkinter GUI application
- 🌐 **Web App**: Modern responsive web interface with real-time progress
- 📊 **Rich Data Display**: Beautiful charts and organized information presentation
- 📄 **Export Functionality**: Save analysis reports in text or JSON format

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd ai-restaurant-recommender-app
pip install -r requirements.txt
```

### 2. Configure API Keys
Edit `config.py` and replace the placeholder values:

```python
# Required API Keys
GOOGLE_MAPS_API_KEY = "your_actual_google_maps_api_key_here"
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
```

**Getting API Keys:**

**Google Maps API:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable these APIs:
   - Places API (Nearby Search)
   - Places API (Details)
   - Distance Matrix API
   - Geocoding API
4. Create credentials (API Key)
5. Restrict the key to specific APIs for security

**Gemini API:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your config file

### 3. Run the Application

**Desktop Version:**
```bash
python main.py
```

**Web Version:**
```bash
python main_web.py
# Open http://127.0.0.1:5000 in your browser
```

## 📁 Project Structure

```
restaurant-recommender/
├── main.py                    # Desktop application entry point
├── main_web.py               # Web application entry point
├── config.py                 # Configuration and API keys
├── ui.py                     # Desktop UI components
├── restaurant_service.py     # Restaurant search and data processing
├── location_service.py       # Address-to-coordinates conversion
├── review_service.py         # Google Places reviews fetching
├── analysis_service.py       # Gemini AI analysis integration
├── restaurant_analyzer.py    # Main analysis orchestrator
├── detail_view.py           # Desktop detail view window
├── templates/
│   └── index.html           # Web interface template
├── cache/                   # Auto-created cache directory
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🖥️ Desktop Application Usage

### Location Input
- **Coordinates**: Enter latitude and longitude directly
- **Address**: Enter any valid address (automatically converted to coordinates)

### Search Parameters
- **Search Radius**: 100m to 5km (adjustable slider)
- **Minimum Reviews**: 10 to 1000 reviews (filters out places with few reviews)
- **Maximum Results**: 1 to 20 restaurants (limits results shown)

### Restaurant Analysis
1. Click "More Info" on any restaurant card
2. Watch real-time progress as reviews are fetched and analyzed
3. View comprehensive analysis in organized sections
4. Export reports or refresh analysis with new data

## 🌐 Web Application Usage

### Modern Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Progress**: Live updates during analysis
- **Interactive Elements**: Smooth animations and modern UI
- **Export Functionality**: Download analysis reports

### API Endpoints
- `POST /search_restaurants` - Search for restaurants
- `POST /analyze_restaurant` - Start restaurant analysis
- `GET /analysis_status/<id>` - Check analysis progress
- `POST /cancel_analysis/<id>` - Cancel ongoing analysis
- `GET /cache_info` - Get cache statistics
- `POST /clear_cache` - Clear all caches

## 🔧 Configuration Options

### Search Defaults (in config.py)
```python
DEFAULT_RADIUS = 1000          # Default search radius in meters
DEFAULT_MIN_REVIEWS = 100      # Default minimum reviews filter
DEFAULT_MAX_RESULTS = 5        # Default maximum results
DEFAULT_REVIEW_COUNT = 200     # Reviews to analyze per restaurant
```

### Cache Settings
```python
REVIEW_CACHE_DURATION = 3600    # 1 hour
ANALYSIS_CACHE_DURATION = 86400 # 24 hours
```

### UI Settings
```python
WINDOW_WIDTH = 800             # Desktop window width
WINDOW_HEIGHT = 600            # Desktop window height
WEB_HOST = "127.0.0.1"        # Web server host
WEB_PORT = 5000               # Web server port
```

## 🤖 AI Analysis Details

### Gemini AI Integration
The application uses Google's Gemini AI to analyze restaurant reviews and extract structured insights:

- **Smart Parsing**: Identifies key themes across hundreds of reviews
- **Sentiment Analysis**: Determines overall customer sentiment
- **Pattern Recognition**: Finds commonly mentioned dishes and experiences
- **Complaint Detection**: Categorizes and prioritizes customer concerns
- **Ambience Description**: Creates atmospheric descriptions from customer feedback

### Analysis Output Structure
```json
{
  "cuisine_type": "Italian Fine Dining",
  "ambience": "Romantic, dimly lit with cozy atmosphere",
  "highlights": [
    "Exceptional pasta dishes",
    "Attentive and knowledgeable staff",
    "Beautiful presentation",
    "Great wine selection",
    "Perfect for special occasions"
  ],
  "complaints": [
    "Can be quite noisy during peak hours",
    "Expensive pricing",
    "Limited vegetarian options"
  ],
  "overall_sentiment": "Very positive with minor concerns about noise and pricing",
  "price_range": "$$$ - Expensive",
  "best_dishes": [
    "Truffle Risotto",
    "Osso Buco",
    "Tiramisu"
  ],
  "service_quality": "Consistently praised for professional and attentive service"
}
```

## 🎯 Advanced Features

### Intelligent Caching
- **Review Caching**: Stores fetched reviews for 1 hour to reduce API calls
- **Analysis Caching**: Saves AI analysis results for 24 hours
- **Automatic Cleanup**: Removes expired cache entries automatically
- **Cache Management**: View cache statistics and clear when needed

### Error Handling
- **Network Resilience**: Automatic retries with exponential backoff
- **API Limit Management**: Graceful handling of API quota limits
- **User Feedback**: Clear error messages and recovery suggestions
- **Logging**: Comprehensive logging for debugging and monitoring

### Performance Optimization
- **Async Operations**: Non-blocking analysis for smooth user experience
- **Connection Pooling**: Reuses HTTP connections for better performance
- **Lazy Loading**: Loads data only when needed
- **Efficient Filtering**: Client-side filtering reduces server load

## 🔍 Troubleshooting

### Common Issues

**"Configuration validation failed"**
- Check that API keys are properly set in `config.py`
- Ensure API keys are valid and have proper permissions
- Verify that required Google APIs are enabled

**"No restaurants found"**
- Try increasing the search radius
- Reduce the minimum number of reviews requirement
- Verify the location coordinates or address are correct

**"Analysis failed"**
- Check Gemini API key and quota
- Ensure the restaurant has sufficient reviews
- Try refreshing the analysis

**"Network errors"**
- Check internet connection
- Verify API keys are not exceeding quotas
- Check for any firewall restrictions

### API Quota Management
- **Google Maps**: 1000 requests per day (free tier)
- **Gemini**: Check current limits in Google AI Studio
- **Rate Limiting**: Built-in delays between requests
- **Caching**: Reduces API usage significantly

## 📊 Performance Tips

### Optimize API Usage
- Use caching effectively (enabled by default)
- Choose appropriate search radius
- Set reasonable minimum review counts
- Monitor API usage in Google Cloud Console

### Desktop vs Web Performance
- **Desktop**: Better for frequent use, persistent caching
- **Web**: Better for sharing, cross-platform compatibility
- **Both**: Support real-time progress and full feature set

## 🛡️ Security Considerations

### API Key Security
- Never commit API keys to version control
- Use environment variables in production
- Restrict API keys to specific APIs and domains (web version)
- Monitor API usage for unusual activity

### Production Deployment (Web Version)
```bash
# Use environment variables
export GOOGLE_MAPS_API_KEY="your_key_here"
export GEMINI_API_KEY="your_key_here"

# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main_web:app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Maps API for restaurant data
- Google Gemini AI for intelligent review analysis
- Flask and Tkinter for the user interfaces
- The open-source community for various Python libraries

---

**Happy restaurant hunting! 🍽️✨**

For support or questions, please open an issue in the repository.