# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

# Import all our final calculation functions
from astro_logic import (
    calculate_julian_day,
    calculate_lagna,
    get_zodiac_sign,
    decimal_to_dms,
    get_planetary_positions,
    calculate_house_cusps,
    get_planet_house_placement
)

app = FastAPI(
    title="Kundali API",
    description="An API for calculating astrological chart data.",
    version="1.0.0"
)

# Define the structure of the input data
class BirthData(BaseModel):
    name: str
    birth_datetime: datetime
    latitude: float
    longitude: float

@app.get("/")
def read_root():
    """A simple endpoint to check if the API is running."""
    return {"status": "Kundali API is running. Go to /docs to use the calculator."}

@app.post("/calculate/chart-data")
def get_chart_data(data: BirthData):
    """
    Calculates the Lagna, Planetary Positions, and Houses from birth data.
    """
    julian_day = calculate_julian_day(data.birth_datetime)
    
    # This returns a dictionary with lagna, ayanamsa, etc.
    lagna_data = calculate_lagna(
        julian_day=julian_day,
        latitude=data.latitude,
        longitude=data.longitude
    )
    
    # Extract the values we need
    lagna_degree_decimal = lagna_data['lagna_decimal']
    ayanamsa_degree = lagna_data['ayanamsa']
    
    # Format Lagna details
    lagna_sign = get_zodiac_sign(lagna_degree_decimal)
    lagna_degree_dms = decimal_to_dms(lagna_degree_decimal)
    
    # Calculate all planetary positions
    planets = get_planetary_positions(julian_day)
    
    # Calculate House Cusps
    house_cusps_decimal = calculate_house_cusps(lagna_data, data.latitude)
    
    # Determine which house each planet is in
    planets_with_houses = get_planet_house_placement(planets, house_cusps_decimal)

    # Format house cusps for the response
    formatted_house_cusps = {f"house_{i+1}": f"{decimal_to_dms(cusp)} ({get_zodiac_sign(cusp)})" for i, cusp in enumerate(house_cusps_decimal)}
    
    return {
        "input_data": data,
        "calculation_results": {
            "ayanamsa_decimal_degree": round(ayanamsa_degree, 4),
            "lagna": {
                "decimal_degree": round(lagna_degree_decimal, 4),
                "dms": lagna_degree_dms,
                "sign": lagna_sign,
                "house": 1
            },
            "house_cusps_sripathi": formatted_house_cusps,
            "planetary_positions": planets_with_houses
        }
    }