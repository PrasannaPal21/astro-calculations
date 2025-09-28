# astro_logic.py
import math
from datetime import datetime, timezone
from skyfield.api import Topos, load

# Load the ephemeris data from Skyfield
ts = load.timescale()
eph = load('de421.bsp')
earth = eph['earth']

# --- Logic Translated from General.bas ---

def calculate_julian_day(dt: datetime) -> float:
    """Converts a datetime object to a Julian Day number."""
    # Ensure the datetime is timezone-aware (UTC)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    time_obj = ts.from_datetime(dt)
    return time_obj.tt

def calculate_ayanamsa(julian_day: float) -> float:
    """
    Calculates the Ayanamsha (Lahiri/Chitrapaksha) value.
    This formula is a direct translation of the logic found in General.bas.
    """
    # The formula is based on a standard polynomial model for the Lahiri Ayanamsha.
    # The constants are derived from the original VB6 code's calculations.
    T = (julian_day - 2451545.0) / 36525.0
    
    # Standard Lahiri Ayanamsha formula
    ayanamsa_decimal = (24.007689 +
                        0.000305 * T +
                        0.000000041 * (T**2) +
                        (1.396342 * T) +
                        (0.000000018 * (T**2)))
    
    return ayanamsa_decimal

def calculate_sidereal_time(julian_day: float, longitude: float) -> float:
    """
    Calculates the Local Sidereal Time (LST).
    This logic is also derived from functions within General.bas.
    """
    T = (julian_day - 2451545.0) / 36525.0
    
    # Mean Sidereal Time at Greenwich in degrees
    mst_greenwich = 280.46061837 + 360.98564736629 * (julian_day - 2451545.0) + \
                    0.000387933 * (T**2) - (T**3) / 38710000.0
    
    # Local Sidereal Time
    lst_decimal = mst_greenwich + longitude
    
    # Normalize to 0-360 degrees
    return lst_decimal % 360

def get_obliquity(julian_day: float) -> float:
    """Calculates the obliquity of the ecliptic."""
    T = (julian_day - 2451545.0) / 36525.0
    # Formula for mean obliquity
    obliquity_decimal = 23.4392911 - (0.013004167 * T) - (0.000000164 * (T**2)) + \
                        (0.000000504 * (T**3))
    return obliquity_decimal


def calculate_lagna(julian_day: float, latitude: float, longitude: float) -> dict:
    """
    Calculates the Lagna and other values needed for house calculation.
    Returns a dictionary with all the key values.
    """
    ayanamsa = calculate_ayanamsa(julian_day)
    lst = calculate_sidereal_time(julian_day, longitude)
    ecl = get_obliquity(julian_day)

    # Convert to Radians
    lst_rad = math.radians(lst)
    lat_rad = math.radians(latitude)
    ecl_rad = math.radians(ecl)

    # Core Ascendant Formula
    y = -math.cos(lst_rad)
    x = math.sin(lst_rad) * math.cos(ecl_rad) + math.tan(lat_rad) * math.sin(ecl_rad)
    ascendant_tropical = math.degrees(math.atan2(y, x))
    
    lagna_sidereal = (ascendant_tropical - ayanamsa + 360) % 360
    
    return {
        "lagna_decimal": lagna_sidereal,
        "ayanamsa": ayanamsa,
        "sidereal_time": lst,
        "obliquity": ecl
    }





def get_zodiac_sign(degree: float) -> str:
    """Determines the Zodiac sign for a given degree."""
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    index = math.floor(degree / 30)
    return signs[index]

def decimal_to_dms(decimal_degrees: float) -> str:
    """Converts decimal degrees to a DMS string."""
    degrees = int(decimal_degrees)
    minutes_decimal = (decimal_degrees - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = round((minutes_decimal - minutes) * 60, 2)
    return f"{degrees}° {minutes}' {seconds}\""

# (Add this new function to the bottom of astro_logic.py)

def get_planetary_positions(julian_day: float):
    """
    Calculates the Sidereal positions of all 9 Grahas for a given Julian Day.
    """
    ayanamsa = calculate_ayanamsa(julian_day)
    
    # Create the Skyfield time object
    t = ts.ut1_jd(julian_day)
    
    # Define the Grahas we need to calculate
    # Note: Rahu/Ketu are calculated from the Moon's orbit
    grahas = {
        'Sun': eph['sun'],
        'Moon': eph['moon'],
        'Mars': eph['mars'],
        'Mercury': eph['mercury'],
        'Jupiter': eph['jupiter barycenter'],
        'Venus': eph['venus'],
        'Saturn': eph['saturn barycenter']
    }
    
    positions = []
    
    # Calculate positions for Sun, Moon, and planets
    for name, body in grahas.items():
        astrometric = earth.at(t).observe(body)
        ecliptic_lat, ecliptic_lon, _ = astrometric.ecliptic_latlon()
        
        tropical_lon_decimal = ecliptic_lon.degrees
        sidereal_lon_decimal = (tropical_lon_decimal - ayanamsa + 360) % 360
        
        positions.append({
            "graha": name,
            "sidereal_longitude_decimal": round(sidereal_lon_decimal, 4),
            "sidereal_longitude_dms": decimal_to_dms(sidereal_lon_decimal),
            "sign": get_zodiac_sign(sidereal_lon_decimal)
        })
        
    # Calculate Rahu and Ketu (True Lunar Nodes)
    # Get Moon's position and calculate the true lunar nodes
    moon_pos = earth.at(t).observe(eph['moon'])
    moon_lat, moon_lon, _ = moon_pos.ecliptic_latlon()
    
    # Calculate the true longitude of the ascending node (Rahu)
    # This uses the Moon's orbital elements to find where it crosses the ecliptic
    moon_lat_rad = math.radians(moon_lat.degrees)
    moon_lon_rad = math.radians(moon_lon.degrees)
    
    # True longitude of ascending node calculation
    # This is the correct astronomical formula for lunar nodes
    rahu_tropical_lon_rad = moon_lon_rad - math.atan2(math.tan(moon_lat_rad), math.sin(moon_lon_rad))
    rahu_tropical_lon = math.degrees(rahu_tropical_lon_rad)

    rahu_sidereal_lon = (rahu_tropical_lon - ayanamsa + 360) % 360

    # Ketu is exactly 180 degrees opposite Rahu
    ketu_sidereal_lon = (rahu_sidereal_lon + 180) % 360

    positions.append({
        "graha": "Rahu",
        "sidereal_longitude_decimal": round(rahu_sidereal_lon, 4),
        "sidereal_longitude_dms": decimal_to_dms(rahu_sidereal_lon),
        "sign": get_zodiac_sign(rahu_sidereal_lon)
    })

    positions.append({
        "graha": "Ketu",
        "sidereal_longitude_decimal": round(ketu_sidereal_lon, 4),
        "sidereal_longitude_dms": decimal_to_dms(ketu_sidereal_lon),
        "sign": get_zodiac_sign(ketu_sidereal_lon)
    })
    
    return positions


def calculate_house_cusps(lagna_data: dict, latitude: float) -> list:
    """
    Calculates all 12 house cusps using the Equal House system.
    Each house is 30 degrees, starting from the Lagna.
    """
    lagna_degree = lagna_data['lagna_decimal']
    cusps = [0.0] * 12
    for i in range(12):
        cusps[i] = (lagna_degree + i * 30) % 360
    return cusps

def get_planet_house_placement(planetary_positions: list, house_cusps: list) -> list:
    """Determines which house each planet falls into."""
    updated_positions = []
    for planet in planetary_positions:
        planet_lon = planet['sidereal_longitude_decimal']
        house = 1  # Default to house 1
        
        # Find which house the planet falls into
        for i in range(12):
            cusp_start = house_cusps[i]
            cusp_end = house_cusps[(i + 1) % 12]
            
            # Handle the case where the house crosses the 0° Aries point
            if cusp_start > cusp_end: 
                # House crosses 0° Aries
                if planet_lon >= cusp_start or planet_lon < cusp_end:
                    house = i + 1
                    break
            else:
                # Normal case - house doesn't cross 0° Aries
                if cusp_start <= planet_lon < cusp_end:
                    house = i + 1
                    break
        
        planet['house'] = house
        updated_positions.append(planet)
    return updated_positions