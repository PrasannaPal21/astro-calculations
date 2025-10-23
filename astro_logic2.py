# astro_logic2.py
from datetime import datetime
import traceback

# Import the correct functions from the library, including the JSON helper
from jyotishganit import calculate_birth_chart, get_birth_chart_json

def get_jyotishganit_chart(birth_dt: datetime, latitude: float, longitude: float, timezone_offset: float) -> dict:
    """
    Calculates a comprehensive Vedic chart using the jyotishganit library
    and returns the complete chart data as a dictionary.
    
    Args:
        birth_dt: The localized NAIVE birth datetime object.
        latitude: Birthplace latitude.
        longitude: Birthplace longitude.
        timezone_offset: The float timezone offset (e.g., 5.5 for IST).

    Returns:
        A dictionary containing the full chart details.
    """
    try:
        # 1. Generate the birth chart using the library
        chart = calculate_birth_chart(
            birth_date=birth_dt,
            latitude=latitude,
            longitude=longitude,
            timezone_offset=timezone_offset
        )
        
        # 2. Use the library's built-in JSON dictionary converter
        # This avoids all manual formatting and attribute errors.
        # The library handles formatting the dashas, panchang,
        # and all divisional charts correctly.
        chart_data_dict = get_birth_chart_json(chart)
        
        # 3. Return the complete, correctly formatted dictionary
        return chart_data_dict

    except Exception as e:
        print(f"Error in astro_logic2.py: {e}")
        print(traceback.format_exc())
        # Re-raise the exception to be caught by the FastAPI endpoint
        raise ValueError(f"Jyotishganit calculation failed: {str(e)}")