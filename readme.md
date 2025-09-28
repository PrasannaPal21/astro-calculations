# 🌟 Kundali API

A FastAPI-based astrological calculation service that provides accurate birth chart data including planetary positions, house cusps, and lagna calculations using traditional Vedic astrology principles.

## ✨ Features

- **Planetary Positions**: Calculate sidereal positions of all 9 grahas (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
- **Lagna Calculation**: Accurate ascendant (lagna) calculation using Lahiri Ayanamsha
- **House System**: Equal house system with 12 house cusps
- **Zodiac Signs**: Automatic zodiac sign determination for all positions
- **DMS Format**: Degrees, minutes, seconds formatting for precise readings
- **RESTful API**: Clean, documented API endpoints with automatic OpenAPI documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd kundali-backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Interactive API: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Health Check
```http
GET /
```
Returns API status and basic information.

#### Calculate Birth Chart
```http
POST /calculate/chart-data
```

**Request Body:**
```json
{
  "name": "John Doe",
  "birth_datetime": "1990-05-15T14:30:00Z",
  "latitude": 28.6139,
  "longitude": 77.2090
}
```

**Response:**
```json
{
  "input_data": {
    "name": "John Doe",
    "birth_datetime": "1990-05-15T14:30:00Z",
    "latitude": 28.6139,
    "longitude": 77.2090
  },
  "calculation_results": {
    "ayanamsa_decimal_degree": 23.8547,
    "lagna": {
      "decimal_degree": 145.2341,
      "dms": "145° 14' 2.76\"",
      "sign": "Leo",
      "house": 1
    },
    "house_cusps_sripathi": {
      "house_1": "145° 14' 2.76\" (Leo)",
      "house_2": "175° 14' 2.76\" (Virgo)",
      // ... all 12 houses
    },
    "planetary_positions": [
      {
        "graha": "Sun",
        "sidereal_longitude_decimal": 31.2341,
        "sidereal_longitude_dms": "31° 14' 2.76\"",
        "sign": "Aries",
        "house": 10
      },
      // ... all planets
    ]
  }
}
```

## 🔬 Technical Details

### Astrological Calculations

The API implements traditional Vedic astrology calculations:

- **Ayanamsha**: Lahiri/Chitrapaksha system
- **Sidereal Time**: Local sidereal time calculation
- **Planetary Positions**: Using JPL ephemeris data (DE421)
- **House System**: Equal house system (30° per house)
- **Lunar Nodes**: True Rahu and Ketu positions

### Dependencies

- **FastAPI**: Modern, fast web framework for building APIs
- **Skyfield**: High-precision astronomy library
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running the application

### File Structure

```
kundali-backend/
├── main.py              # FastAPI application and endpoints
├── astro_logic.py       # Core astrological calculations
├── requirements.txt     # Python dependencies
├── de421.bsp           # JPL ephemeris data file
└── README.md           # This file
```

## 🌐 Deployment

### Render Deployment

1. **Connect your repository** to Render
2. **Configure build settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Deploy**: Render will automatically build and deploy your application

### Environment Variables

No environment variables are required for basic functionality. The API uses the included JPL ephemeris data file.

## 🧮 Mathematical Foundation

The calculations are based on:

- **Julian Day Numbers**: For precise time calculations
- **Sidereal Time**: Local sidereal time for lagna calculation
- **Obliquity of Ecliptic**: For coordinate transformations
- **Lahiri Ayanamsha**: Standard Indian sidereal zodiac
- **JPL Ephemeris**: NASA's high-precision planetary data

## 📖 Usage Examples

### Python Example

```python
import requests

# Calculate birth chart
data = {
    "name": "Sample Person",
    "birth_datetime": "1990-05-15T14:30:00Z",
    "latitude": 28.6139,  # Delhi
    "longitude": 77.2090
}

response = requests.post("http://localhost:8000/calculate/chart-data", json=data)
chart_data = response.json()

print(f"Lagna: {chart_data['calculation_results']['lagna']['sign']}")
print(f"Sun Sign: {chart_data['calculation_results']['planetary_positions'][0]['sign']}")
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/calculate/chart-data" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sample Person",
    "birth_datetime": "1990-05-15T14:30:00Z",
    "latitude": 28.6139,
    "longitude": 77.2090
  }'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Skyfield**: For high-precision astronomical calculations
- **JPL**: For the DE421 ephemeris data
- **FastAPI**: For the excellent web framework
- **Traditional Vedic Astrology**: For the mathematical foundations

## 📞 Support

For questions, issues, or contributions, please open an issue on GitHub or contact the development team.

---

**Note**: This API is for educational and research purposes. For professional astrological consultations, please consult with qualified astrologers.
