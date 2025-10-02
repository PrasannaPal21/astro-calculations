# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from astro_logic import (
    get_skyfield_time_from_datetime,
    calculate_lahiri_ayanamsa,
    calculate_lagna_and_primaries,
    calculate_sripati_house_cusps,
    get_planetary_positions_sidereal,
    get_zodiac_sign
)

app = FastAPI(
    title="Vedic Astrology API",
    description="An API for calculating Vedic astrological charts with Sripati house system",
    version="1.0.0"
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development and deployment flexibility
    allow_credentials=False,  # Set to False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

IST = timezone(timedelta(hours=5, minutes=30))

class BirthInput(BaseModel):
    name: str
    birthplace: str
    birth_datetime: datetime
    latitude: float
    longitude: float   # East-positive, e.g., Bangalore = 77.5946

@app.get("/")
def read_root():
    return {
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

@app.post("/vedic-chart")
def get_vedic_chart(data: BirthInput):
    dt_in = data.birth_datetime

    # Validate date range for ephemeris (de421.bsp covers 1899-07-29 through 2053-10-09)
    min_date = datetime(1899, 7, 29, tzinfo=timezone.utc)
    max_date = datetime(2053, 10, 9, tzinfo=timezone.utc)
    
    # Convert input date to UTC for validation
    if dt_in.tzinfo is None:
        dt_check = dt_in.replace(tzinfo=IST).astimezone(timezone.utc)
    else:
        dt_check = dt_in.astimezone(timezone.utc)
    
    if dt_check < min_date or dt_check > max_date:
        raise HTTPException(
            status_code=400,
            detail=f"Birth date must be between {min_date.strftime('%Y-%m-%d')} and {max_date.strftime('%Y-%m-%d')}. "
                   f"Provided date: {dt_check.strftime('%Y-%m-%d')}"
        )

    # If naive, assume IST (India-only)
    if dt_in.tzinfo is None:
        dt_local = dt_in.replace(tzinfo=IST)
        assumed_tz = "assumed_IST"
    else:
        dt_local = dt_in
        assumed_tz = "from_input"

    # Create UTC moment used for ephemeris
    dt_utc = dt_local.astimezone(timezone.utc)

    try:
        # Skyfield time
        t = get_skyfield_time_from_datetime(dt_utc)

        # Ayanamsa (Lahiri)
        ayan = calculate_lahiri_ayanamsa(t)

        # Ascendant & primaries
        lagna_info = calculate_lagna_and_primaries(t, data.latitude, data.longitude, ayan)
        lagna_sid = lagna_info["asc_sidereal_deg"]
        lagna_sign = get_zodiac_sign(lagna_sid)

        # Houses (Sripati)
        houses_data = calculate_sripati_house_cusps(t, data.latitude, data.longitude, ayan)
        cusps = houses_data["cusps_sid"]

        # Planets
        planets = get_planetary_positions_sidereal(t, ayan)
        
    except Exception as e:
        if "EphemerisRangeError" in str(type(e)) or "ephemeris segment only covers dates" in str(e):
            raise HTTPException(
                status_code=400,
                detail=f"Date {dt_check.strftime('%Y-%m-%d')} is outside the supported ephemeris range (1899-07-29 to 2053-10-09). "
                       f"Please use a date within this range."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Calculation error: {str(e)}"
            )

    # Moon sign
    moon = next((p for p in planets if p["graha"] == "Moon"), None)
    moon_sign = moon["sign"] if moon else None

    resp = {
        "name": data.name,
        "birthplace": data.birthplace,
        "birth_datetime_input": data.birth_datetime.isoformat(),
        "assumed_tz_handling": assumed_tz,
        "birth_datetime_used_utc": dt_utc.isoformat(),
        "ayanamsa_deg": round(ayan, 9),
        "lagna_sidereal_deg": round(lagna_sid, 6),
        "lagna_sign": lagna_sign,
        "moon_sign": moon_sign,
        "houses_sidereal": [
            {"house": i + 1, "cusp_deg": round(c, 6), "sign": get_zodiac_sign(c)}
            for i, c in enumerate(cusps)
        ],
        "planets_sidereal": planets,
        # debug info: GMST / LST and primary tropical primaries (helpful to verify correctness)
        "debug": {
            "gmst_deg": round(lagna_info["gmst_deg"], 9),
            "gmst_hours": round(lagna_info["gmst_hours"], 9),
            "lst_deg": round(lagna_info["lst_deg"], 9),
            "lst_hours": round(lagna_info["lst_hours"], 9),
            "eps_deg": round(lagna_info["eps_deg"], 9),
            "primary_tropical_asc_deg": round(lagna_info["asc_tropical_deg"], 6),
            "primary_tropical_mc_deg": round(lagna_info["mc_tropical_deg"], 6)
        }
    }
    return resp
