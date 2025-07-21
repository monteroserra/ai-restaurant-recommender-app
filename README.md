# AI Restaurant Recommender App 🍽️

A sophisticated Python-based application that helps users find the top-rated nearby restaurants using the Google Maps API. The app features a modern graphical interface built with Tkinter and supports both coordinate-based and address-based location input.

---

## 🚀 New Features

- 🎯 **Flexible Location Input**: Use either coordinates or street addresses
- 📍 **Address-to-Coordinates Conversion**: Automatically converts addresses to coordinates
- 🔧 **Modular Architecture**: Clean separation between UI, business logic, and services
- 📊 **Enhanced UI**: Improved interface with better organization and visual feedback
- ⚙️ **Configurable Parameters**: Adjustable search radius, minimum reviews, and maximum results
- 📈 **Better Error Handling**: Comprehensive error handling and user feedback

---

## 📁 Project Structure

```
restaurant-recommender/
├── main.py                 # Main application entry point
├── ui.py                   # User interface components
├── restaurant_service.py   # Restaurant search and data processing
├── location_service.py     # Address-to-coordinates conversion
├── config.py              # Configuration and API keys
└── README.md              # This file
```

### Architecture Overview

- **`main.py`**: Application coordinator that ties together all components
- **`ui.py`**: Pure UI layer with no business logic
- **`restaurant_service.py`**: Handles all restaurant-related API calls and data processing
- **`location_service.py`**: Manages location resolution (address → coordinates)
- **`config.py`**: Configuration settings and API keys

---

## 🛠️ Setup

### Prerequisites
- Python 3.7+
- Google Maps API key with the following APIs enabled:
  - Places API
  - Distance Matrix API
  - Geocoding API

### Installation

1. **Clone or download the project files**

2. **Install required packages:**
   ```bash
   pip install requests tkinter
   ```
   > Note: `tkinter` usually comes pre-installed with Python

3. **Configure your API key:**
   - Edit `config.py`
   - Replace `"YOUR_GOOGLE_MAPS_API_KEY_HERE"` with your actual Google Maps API key

4. **Run the application:**
   ```bash
   python main.py
   ```

---

## 🎯 How to Use

### Location Input Options

**Option 1: Coordinates**
- Select "Use Coordinates" radio button
- Enter latitude and longitude (default values provided)
- Example: `40.7128, -74.0060` (New York City)

**Option 2: Address**
- Select "Use Address" radio button
- Enter any valid address
- Examples:
  - `1600 Amphitheatre Parkway, Mountain View, CA`
  - `Times Square, New York, NY`
  - `Eiffel Tower, Paris, France`

### Search Parameters

- **Search Radius**: 100m to 5km (adjustable slider)
- **Minimum Reviews**: 10 to 1000 reviews (filters out places with too few reviews)
- **Maximum Results**: 1 to 20 restaurants (limits the number of results shown)

### Results

The app displays:
- Restaurant name and rating
- Number of reviews
- Address/vicinity
- Walking distance and estimated time

---

## 🔧 Customization

### Default Location
Edit `ui.py` in the `set_default_coordinates()` method to change default coordinates:

```python
def set_default_coordinates(self):
    # Change these to your preferred defaults
    self.lat_entry.insert(0, "YOUR_DEFAULT_LATITUDE")
    self.lng_entry.insert(0, "YOUR_DEFAULT_LONGITUDE")
```

### Search Parameters
Modify default values in `config.py`:

```python
DEFAULT_RADIUS = 1000  # meters
DEFAULT_MIN_REVIEWS = 100
DEFAULT_MAX_RESULTS = 5
```

### UI Styling
Customize the interface by modifying the UI components in `ui.py`.

---

## 🔗 API Requirements

### Google Maps APIs Used

1. **Places API (Nearby Search)**
   - Finds restaurants near specified location
   - Used in `restaurant_service.py`

2. **Distance Matrix API**
   - Calculates walking distance and time
   - Used in `restaurant_service.py`

3. **Geocoding API**
   - Converts addresses to coordinates
   - Used in `location_service.py`

### Getting API Keys

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the required APIs
4. Create credentials (API key)
5. Restrict the key to the specific APIs for security

---

## 🐛 Troubleshooting

### Common Issues

**"No restaurants found"**
- Try increasing the search radius
- Reduce the minimum number of reviews
- Check if the location is correct

**"Could not find coordinates for address"**
- Verify the address is correct and specific enough
- Try adding city/state/country to the address
- Check your Geocoding API quota

**"API Error"**
- Verify your API key is correct
- Check that all required APIs are enabled
- Ensure you haven't exceeded API quotas

### Error Messages
The app provides detailed error messages in the status bar and popup dialogs to help diagnose issues.

---

## 🚀 Future Enhancements

- 🤖 **AI Integration**: Add GPT/Gemini for intelligent restaurant recommendations
- 🍕 **Cuisine Filtering**: Filter by food type (Italian, Chinese, etc.)
- ⭐ **Price Range**: Add price level filtering
- 📱 **Mobile Support**: Create mobile-responsive version
- 💾 **Favorites**: Save and manage favorite restaurants
- 🗺️ **Map Integration**: Visual map display of restaurants

---

## 📄 License

This project is open source and available under the MIT License.