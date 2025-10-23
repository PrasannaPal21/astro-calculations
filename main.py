# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

# --- Original Imports (for V1) ---
from astro_logic import (
    get_skyfield_time_from_datetime,
    calculate_lahiri_ayanamsa,
    calculate_lagna_and_primaries,
    calculate_sripati_house_cusps,
    get_planetary_positions_sidereal,
    get_zodiac_sign
)

# --- New Import (for V2) ---
from astro_logic2 import get_jyotishganit_chart


app = FastAPI(
    title="Vedic Astrology API",
    description="An API for calculating Vedic astrological charts",
    version="1.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

IST = timezone(timedelta(hours=5, minutes=30))

class BirthInput(BaseModel):
    name: str
    birthplace: str
    birth_datetime: datetime
    latitude: float
    longitude: float    # East-positive, e.g., Bangalore = 77.5946

@app.get("/")
def read_root():
    return {
        "message": "Vedic Astrology API is running.",
        "endpoints": {
            "/vedic-chart": "POST - (V1) Calculate chart using Skyfield/Sripati",
            "/v2/vedic-chart": "POST - (V2) Calculate chart using Jyotishganit",
            "/docs": "GET - Interactive API documentation"
        }
    }

# --- Original Endpoint (V1) ---
# This endpoint remains unchanged and uses astro_logic.py
@app.post("/vedic-chart")
def get_vedic_chart(data: BirthInput):
    dt_in = data.birth_datetime

    # Validate date range for ephemeris (de421.bsp)
    min_date = datetime(1899, 7, 29, tzinfo=timezone.utc)
    max_date = datetime(2053, 10, 9, tzinfo=timezone.utc)
    
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
        t = get_skyfield_time_from_datetime(dt_utc)
        ayan = calculate_lahiri_ayanamsa(t)
        lagna_info = calculate_lagna_and_primaries(t, data.latitude, data.longitude, ayan)
        lagna_sid = lagna_info["asc_sidereal_deg"]
        lagna_sign = get_zodiac_sign(lagna_sid)
        houses_data = calculate_sripati_house_cusps(t, data.latitude, data.longitude, ayan)
        cusps = houses_data["cusps_sid"]
        planets = get_planetary_positions_sidereal(t, ayan)
        
    except Exception as e:
        if "EphemerisRangeError" in str(type(e)) or "ephemeris segment only covers dates" in str(e):
            raise HTTPException(
                status_code=400,
                detail=f"Date {dt_check.strftime('%Y-%m-%d')} is outside the supported ephemeris range (1899-07-29 to 2053-10-09). "
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Calculation error: {str(e)}"
            )

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

# --- New Endpoint (V2) ---
# This new endpoint uses astro_logic2.py (Jyotishganit)
@app.post("/v2/vedic-chart")
def get_vedic_chart_v2(data: BirthInput):
    """
    Calculate a comprehensive Vedic chart using the Jyotishganit library.
    This provides Panchanga, Divisional Charts (D1, D9, D10), and Vimshottari Dasha.
    """
    dt_in = data.birth_datetime
    
    # 1. Determine Timezone Offset
    # Jyotishganit requires a float offset (e.g., 5.5)
    if dt_in.tzinfo is None:
        # If naive, assume IST (as per original logic)
        timezone_offset = 5.5
        dt_local = dt_in.replace(tzinfo=IST)
        assumed_tz = "assumed_IST (UTC+05:30)"
    else:
        # If aware, calculate the offset in hours
        offset_seconds = dt_in.utcoffset().total_seconds()
        timezone_offset = offset_seconds / 3600.0
        dt_local = dt_in
        assumed_tz = f"from_input (UTC{timezone_offset:+.2f})"

    # 2. Create NAIVE datetime for the library
    # The jyotishganit library expects a naive datetime object
    # representing the LOCAL time, and a separate float offset.
    dt_local_naive = dt_local.replace(tzinfo=None)

    # 3. Call the Jyotishganit logic
    try:
        chart_data = get_jyotishganit_chart(
            birth_dt=dt_local_naive,  # Pass the NAIVE object
            latitude=data.latitude,
            longitude=data.longitude,
            timezone_offset=timezone_offset
        )
        
    except Exception as e:
        # Catch errors from the calculation library
        raise HTTPException(
            status_code=400, # 400 for bad input (e.g., out-of-range date)
            detail=f"Jyotishganit calculation error: {str(e)}"
        )

    # 4. Format the final response
    return {
        "input_data": {
            "name": data.name,
            "birthplace": data.birthplace,
            "birth_datetime": data.birth_datetime.isoformat(),
            "latitude": data.latitude,
            "longitude": data.longitude,
        },
        "timezone_handling": {
            "status": assumed_tz,
            "offset_used_hours": timezone_offset,
            "localized_datetime_used": dt_local.isoformat(),
            "naive_datetime_passed_to_lib": dt_local_naive.isoformat()
        },
        "chart_results": chart_data
    }