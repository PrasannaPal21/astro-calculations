# 🌟 Vedic Astrology API

for reference - created a corn-job which requests the api every 10 minutes to make sure it is always awake.

A sophisticated FastAPI-based Vedic astrological calculation service that provides accurate birth chart data using traditional principles with modern computational precision. Features advanced Sripati house system, precise planetary positions, and comprehensive error handling.

## ✨ Features

- **🪐 Planetary Positions**: Calculate sidereal positions of all 9 grahas (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
- **🏠 Sripati House System**: Advanced house calculation with proper quadrant-by-quadrant trisection
- **🧭 Precise Lagna Calculation**: Accurate ascendant calculation using Lahiri Ayanamsha with robust formulas
- **🌙 Lunar Nodes**: Mean Rahu and Ketu positions using astronomical algorithms
- **🔢 Multiple Formats**: DMS (Degrees-Minutes-Seconds) and decimal degree formats
- **🌍 Timezone Support**: Automatic IST handling with timezone-aware calculations  
- **⚠️ Date Validation**: Built-in validation for ephemeris date range (1899-2053)
- **📚 RESTful API**: Clean, documented API with automatic OpenAPI documentation
- **🛡️ Error Handling**: Comprehensive error handling with helpful user messages

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

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
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
   - **API Documentation**: http://localhost:8000/docs
   - **Alternative Docs**: http://localhost:8000/redoc
   - **API Info**: http://localhost:8000/

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### API Information
```http
GET /
```
Returns API status, supported date range, and endpoint information.

**Response:**
```json
{
  "message": "Vedic Astrology API is running",
  "endpoints": {
    "/vedic-chart": "POST - Calculate Vedic astrological chart",
    "/docs": "GET - Interactive API documentation"
  },
  "supported_date_range": {
    "minimum": "1899-07-29",
    "maximum": "2053-10-09",
    "note": "Dates outside this range will return an error due to ephemeris limitations"
  }
}
```

#### Calculate Vedic Chart
```http
POST /vedic-chart
```

**Request Body:**
```json
{
  "name": "John Doe",
  "birthplace": "Mumbai, India",
  "birth_datetime": "1990-05-15T14:30:00",
  "latitude": 19.0760,
  "longitude": 72.8777
}
```

**Successful Response (200):**
```json
{
  "name": "John Doe",
  "birthplace": "Mumbai, India",
  "birth_datetime_input": "1990-05-15T14:30:00",
  "assumed_tz_handling": "assumed_IST",
  "birth_datetime_used_utc": "1990-05-15T09:00:00+00:00",
  "ayanamsa_deg": 23.8025434,
  "lagna_sidereal_deg": 224.156789,
  "lagna_sign": "Scorpio",
  "moon_sign": "Capricorn",
  "houses_sidereal": [
    {
      "house": 1,
      "cusp_deg": 224.156789,
      "sign": "Scorpio"
    },
    // ... all 12 houses
  ],
  "planets_sidereal": [
    {
      "graha": "Sun",
      "tropical_deg": 54.123456,
      "sidereal_deg": 30.320913,
      "sign": "Aries",
      "deg_in_sign": 0.320913,
      "dms": "0°19'15.29\""
    },
    // ... all 9 planets including Rahu/Ketu
  ],
  "debug": {
    "gmst_deg": 123.456789,
    "gmst_hours": 8.230453,
    "lst_deg": 196.334566,
    "lst_hours": 13.088971,
    "eps_deg": 23.437119,
    "primary_tropical_asc_deg": 247.959232,
    "primary_tropical_mc_deg": 336.445781
  }
}
```

**Error Response (400) - Invalid Date:**
```json
{
  "detail": "Birth date must be between 1899-07-29 and 2053-10-09. Provided date: 1800-01-01"
}
```

**Error Response (500) - Calculation Error:**
```json
{
  "detail": "Calculation error: [specific error message]"
}
```

## 🔬 Technical Details

### Astrological Calculations

The API implements authentic Vedic astrology calculations with modern precision:

- **Ayanamsha**: Lahiri/Chitrapaksha system with nutation corrections
- **House System**: Sripati system with proper quadrant-by-quadrant trisection
- **Sidereal Time**: High-precision local sidereal time using Meeus algorithms
- **Planetary Positions**: JPL DE421 ephemeris data for maximum accuracy
- **Lunar Nodes**: Mean node calculations using astronomical formulas
- **Coordinate Systems**: Proper tropical to sidereal conversions

### Date Range Support

- **Minimum Date**: July 29, 1899
- **Maximum Date**: October 9, 2053
- **Ephemeris File**: JPL DE421 (included in repository)
- **Validation**: Automatic date range validation with clear error messages

### Timezone Handling

- **Input**: Accepts naive datetime (assumes IST) or timezone-aware datetime
- **Processing**: All calculations performed in UTC
- **IST Assumption**: For Indian astrology, naive dates are treated as IST (UTC+5:30)

### Dependencies

- **FastAPI**: Modern, fast web framework for building APIs
- **Skyfield**: High-precision astronomy library
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for production deployment
- **Requests**: For HTTP client functionality (development/testing)

### File Structure

```
kundali-backend/
├── main.py              # FastAPI application and endpoints
├── astro_logic.py       # Core astrological calculations
├── requirements.txt     # Python dependencies
├── de421.bsp           # JPL ephemeris data file (1899-2053)
├── readme.md           # This documentation
└── venv/               # Virtual environment (auto-generated)
```

## 🌐 Deployment

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Render/Heroku Deployment

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧮 Mathematical Foundation

### Core Algorithms

1. **Greenwich Mean Sidereal Time (GMST)**
   - Meeus algorithm for high precision
   - UT1-based calculations

2. **Local Sidereal Time (LST)**
   - GMST + longitude correction
   - Robust hours-based computation

3. **Ascendant Calculation**
   - Standard spherical astronomy formulas
   - Proper quadrant handling with atan2

4. **Midheaven (MC) Calculation**
   - Ecliptic longitude of meridian
   - Obliquity corrections

5. **Sripati House System**
   - Quadrant-by-quadrant trisection
   - Proper arc calculations between cardinal points

6. **Ayanamsha (Lahiri)**
   - Mean rate: 50.23885 arcsec/year
   - Epoch: 285.0 CE
   - Nutation corrections included

## 📖 Usage Examples

### Python Client
```python
import requests
from datetime import datetime

# Basic chart calculation
def get_vedic_chart(name, birthplace, birth_datetime, lat, lon):
    data = {
        "name": name,
        "birthplace": birthplace,
        "birth_datetime": birth_datetime,
        "latitude": lat,
        "longitude": lon
    }
    
    response = requests.post("http://localhost:8000/vedic-chart", json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.json()['detail']}")
        return None

# Example usage
chart = get_vedic_chart(
    name="Srinivasa Ramanujan",
    birthplace="Erode, Tamil Nadu",
    birth_datetime="1887-12-22T06:30:00",  # This will cause a date range error
    lat=11.3410,
    lon=77.7172
)

# Valid date example
chart = get_vedic_chart(
    name="Test Person",
    birthplace="New Delhi",
    birth_datetime="1990-05-15T14:30:00",
    lat=28.6139,
    lon=77.2090
)

if chart:
    print(f"Lagna: {chart['lagna_sign']}")
    print(f"Moon Sign: {chart['moon_sign']}")
    print(f"Ayanamsa: {chart['ayanamsa_deg']:.4f}°")
```

### JavaScript/Node.js Client
```javascript
const axios = require('axios');

async function getVedicChart(birthData) {
  try {
    const response = await axios.post('http://localhost:8000/vedic-chart', birthData);
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error('Error:', error.response.data.detail);
    } else {
      console.error('Network error:', error.message);
    }
    return null;
  }
}

// Example usage
const chart = await getVedicChart({
  name: "Test Person",
  birthplace: "Mumbai",
  birth_datetime: "1990-05-15T14:30:00",
  latitude: 19.0760,
  longitude: 72.8777
});

if (chart) {
  console.log(`Lagna: ${chart.lagna_sign}`);
  console.log(`Moon Sign: ${chart.moon_sign}`);
}
```

### cURL Examples
```bash
# Valid date
curl -X POST "http://localhost:8000/vedic-chart" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Person",
    "birthplace": "Chennai",
    "birth_datetime": "1990-05-15T14:30:00",
    "latitude": 13.0827,
    "longitude": 80.2707
  }'

# Invalid date (will return 400 error)
curl -X POST "http://localhost:8000/vedic-chart" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Historical Person",
    "birthplace": "Ancient City",
    "birth_datetime": "1800-01-01T12:00:00",
    "latitude": 25.0,
    "longitude": 75.0
  }'
```

## 🚨 Error Handling

### Date Range Errors
The API validates all input dates against the ephemeris range:
- **Minimum**: July 29, 1899
- **Maximum**: October 9, 2053
- **Response**: 400 Bad Request with helpful error message

### Input Validation Errors
- Invalid latitude (-90 to +90)
- Invalid longitude (-180 to +180)
- Malformed datetime strings
- Missing required fields

### Calculation Errors
- Ephemeris data corruption
- Mathematical computation failures
- Timezone conversion issues

## 🧪 Testing

### Unit Tests
```python
# Example test cases
def test_valid_date():
    response = client.post("/vedic-chart", json={
        "name": "Test",
        "birthplace": "Test City",
        "birth_datetime": "2000-01-01T12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090
    })
    assert response.status_code == 200

def test_invalid_date():
    response = client.post("/vedic-chart", json={
        "name": "Test",
        "birthplace": "Test City", 
        "birth_datetime": "1800-01-01T12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090
    })
    assert response.status_code == 400
```

### Manual Testing Checklist
- [ ] Valid dates within range (1899-2053)
- [ ] Boundary dates (1899-07-29, 2053-10-09)
- [ ] Invalid early dates (before 1899)
- [ ] Invalid late dates (after 2053)
- [ ] Different timezones
- [ ] Edge case coordinates (poles, international date line)

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Add tests for new functionality
   - Update documentation
   - Follow existing code style
4. **Test thoroughly**
   ```bash
   python -m pytest tests/
   ```
5. **Commit with descriptive messages**
   ```bash
   git commit -m 'Add support for additional house systems'
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for public methods
- Write tests for new features
- Update README for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Skyfield](https://rhodesmill.org/skyfield/)**: Brandon Rhodes' excellent astronomy library
- **[JPL](https://www.jpl.nasa.gov/)**: For the DE421 ephemeris data
- **[FastAPI](https://fastapi.tiangolo.com/)**: Sebastian Ramirez's outstanding web framework
- **Traditional Vedic Astrology**: Ancient mathematical foundations and wisdom
- **Jean Meeus**: "Astronomical Algorithms" for precise calculations

## 🔗 Related Resources

- [Vedic Astrology Fundamentals](https://en.wikipedia.org/wiki/Hindu_astrology)
- [Sripati House System](https://en.wikipedia.org/wiki/House_(astrology)#Sripati)
- [Lahiri Ayanamsha](https://en.wikipedia.org/wiki/Ayanamsa)
- [JPL Ephemeris Documentation](https://ssd.jpl.nasa.gov/planets/eph_export.html)

## 📞 Support

- **Issues**: Open an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and community support
- **Documentation**: Check `/docs` endpoint for interactive API documentation

---

**⚠️ Disclaimer**: This API is designed for educational, research, and development purposes. For professional astrological consultations, please consult with qualified astrologers. The calculations are based on astronomical data and traditional algorithms but should not be the sole basis for important life decisions.

**🔒 Privacy**: This API does not store any personal information. All calculations are performed in real-time and no data is retained after the response is sent.
