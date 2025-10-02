# astro_logic.py
import math
from datetime import timezone
from skyfield.api import load

ts = load.timescale()
eph = load("de421.bsp")
earth = eph["earth"]
sun = eph["sun"]
moon = eph["moon"]

def get_skyfield_time_from_datetime(dt):
    """Convert a datetime object to a Skyfield time object."""
    return ts.from_datetime(dt)

def _limit360(x):
    return x % 360.0

def get_zodiac_sign(deg):
    signs = [
        "Aries","Taurus","Gemini","Cancer",
        "Leo","Virgo","Libra","Scorpio",
        "Sagittarius","Capricorn","Aquarius","Pisces"
    ]
    return signs[int((deg % 360.0) // 30.0)]

# ------------------------------
# GMST / LST (hours-based, robust)
# ------------------------------
def gmst_in_degrees(time_obj):
    # Meeus formula producing GMST in degrees (uses UT1)
    jd_ut1 = time_obj.ut1
    T_ut1 = (jd_ut1 - 2451545.0) / 36525.0
    gmst_deg = (
        280.46061837
        + 360.98564736629 * (jd_ut1 - 2451545.0)
        + 0.000387933 * (T_ut1 ** 2)
        - (T_ut1 ** 3) / 38710000.0
    ) % 360.0
    return gmst_deg

def local_sidereal_time_degrees(time_obj, longitude_east_deg):
    """
    Compute LST robustly:
      gmst_hours = gmst_deg / 15
      longitude_hours = longitude_deg / 15
      lst_hours = (gmst_hours + longitude_hours) % 24
      lst_deg = lst_hours * 15
    """
    gmst_deg = gmst_in_degrees(time_obj)
    gmst_hours = gmst_deg / 15.0
    longitude_hours = longitude_east_deg / 15.0
    lst_hours = (gmst_hours + longitude_hours) % 24.0
    lst_deg = lst_hours * 15.0
    return lst_deg, gmst_deg, gmst_hours, lst_hours

# ------------------------------
# Lahiri ayanamsa (approx)
# ------------------------------
def calculate_lahiri_ayanamsa(time_obj, epoch_year=285.0, rate_arcsec_per_year=50.23885, add_nutation=True):
    try:
        dt = time_obj.utc_datetime()
    except Exception:
        dt = None

    if dt is not None:
        start_of_year = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        day_of_year = (dt - start_of_year).total_seconds() / 86400.0
        year_decimal = dt.year + day_of_year / 365.2425
    else:
        jd_tt = time_obj.tt
        T_j2000 = (jd_tt - 2451545.0) / 36525.0
        year_decimal = 2000.0 + T_j2000 * 100.0

    years_since = year_decimal - epoch_year
    ayan_arcsec = years_since * rate_arcsec_per_year
    mean_ayan_deg = ayan_arcsec / 3600.0

    if add_nutation:
        jd_tt = time_obj.tt
        T_j2000 = (jd_tt - 2451545.0) / 36525.0
        L_sun = (280.4665 + 36000.7698 * T_j2000) % 360.0
        L_moon = (218.3165 + 481267.8813 * T_j2000) % 360.0
        omega = (125.04452 - 1934.136261 * T_j2000 + 0.0020708 * (T_j2000**2)) % 360.0
        Ls = math.radians(L_sun)
        Lm = math.radians(L_moon)
        om = math.radians(omega)
        delta_psi_arcsec = (
            -17.20 * math.sin(om)
            - 1.32 * math.sin(2 * Ls)
            - 0.23 * math.sin(2 * Lm)
            + 0.21 * math.sin(2 * om)
        )
        delta_psi_deg = delta_psi_arcsec / 3600.0
    else:
        delta_psi_deg = 0.0

    return _limit360(mean_ayan_deg + delta_psi_deg)

# ------------------------------
# Planets (sidereal)
# ------------------------------
def get_planetary_positions_sidereal(time_obj, ayanamsa_deg):
    grahas = {
        "Sun": sun,
        "Moon": moon,
        "Mars": eph["mars"],
        "Mercury": eph["mercury"],
        "Jupiter": eph["jupiter barycenter"],
        "Venus": eph["venus"],
        "Saturn": eph["saturn barycenter"],
    }
    out = []
    for name, body in grahas.items():
        astrom = earth.at(time_obj).observe(body)
        ecl_lat, ecl_lon, _ = astrom.ecliptic_latlon()
        trop = ecl_lon.degrees % 360.0
        sid = _limit360(trop - ayanamsa_deg)
        deg_in_sign = sid % 30.0
        d = int(deg_in_sign)
        m = int((deg_in_sign - d) * 60.0)
        s = round(((deg_in_sign - d) * 60.0 - m) * 60.0, 2)
        out.append({
            "graha": name,
            "tropical_deg": round(trop, 6),
            "sidereal_deg": round(sid, 6),
            "sign": get_zodiac_sign(sid),
            "deg_in_sign": round(deg_in_sign, 6),
            "dms": f"{d}°{m}'{s}\""
        })
    # Rahu/Ketu (mean node)
    jd_tt = time_obj.tt
    T = (jd_tt - 2451545.0) / 36525.0
    omega = (125.04452 - 1934.136261 * T + 0.0020708 * (T**2)) % 360.0
    rahu_trop = omega
    rahu_sid = _limit360(rahu_trop - ayanamsa_deg)
    ketu_sid = _limit360(rahu_sid + 180.0)
    out.append({"graha": "Rahu", "tropical_deg": round(rahu_trop, 6), "sidereal_deg": round(rahu_sid, 6), "sign": get_zodiac_sign(rahu_sid)})
    out.append({"graha": "Ketu", "tropical_deg": round(_limit360(rahu_trop + 180.0), 6), "sidereal_deg": round(ketu_sid, 6), "sign": get_zodiac_sign(ketu_sid)})
    return out

# ------------------------------
# Ascendant/MC and Sripati houses
# ------------------------------
def ascendant_tropical_from_lst_deg(lst_deg, lat_deg, eps_deg):
    ramc = math.radians(lst_deg)
    e = math.radians(eps_deg)
    l = math.radians(lat_deg)
    # Standard formula for Ascendant
    asc = math.atan2(math.cos(ramc), - (math.sin(ramc) * math.cos(e) + math.tan(l) * math.sin(e)))
    return math.degrees(asc) % 360.0

# --- CORRECTED FUNCTION ---
# Replaced the previous MC formula with a more robust version.
def mc_tropical_from_lst_deg(lst_deg, eps_deg):
    ramc_rad = math.radians(lst_deg)
    eps_rad = math.radians(eps_deg)
    
    # Standard formula using atan2 for correct quadrant
    mc_rad = math.atan2(math.sin(ramc_rad) * math.cos(eps_rad), math.cos(ramc_rad))
    
    return math.degrees(mc_rad) % 360.0

def calculate_lagna_and_primaries(time_obj, latitude, longitude_east_deg, ayanamsa_deg):
    """
    Returns dict with asc_tropical, asc_sidereal, mc_trop, ic_trop, desc_trop, lst_deg, gmst_deg, gmst_hours, lst_hours, eps_deg
    """
    lst_deg, gmst_deg, gmst_hours, lst_hours = local_sidereal_time_degrees(time_obj, longitude_east_deg)

    # obliquity TT-based
    T_tt = (time_obj.tt - 2451545.0) / 36525.0
    eps_deg = (23.439291111 - 0.0130041666667 * T_tt - 0.0000001639 * (T_tt**2) + 0.0000005036 * (T_tt**3))

    asc_trop = ascendant_tropical_from_lst_deg(lst_deg, latitude, eps_deg)
    asc_sid = _limit360(asc_trop - ayanamsa_deg)
    mc_trop = mc_tropical_from_lst_deg(lst_deg, eps_deg)
    desc_trop = (asc_trop + 180.0) % 360.0
    ic_trop = (mc_trop + 180.0) % 360.0

    return {
        "asc_tropical_deg": asc_trop,
        "asc_sidereal_deg": asc_sid,
        "mc_tropical_deg": mc_trop,
        "desc_tropical_deg": desc_trop,
        "ic_tropical_deg": ic_trop,
        "lst_deg": lst_deg,
        "lst_hours": lst_hours,
        "gmst_deg": gmst_deg,
        "gmst_hours": gmst_hours,
        "eps_deg": eps_deg
    }

# --- CORRECTED FUNCTION ---
# Replaced the flawed looping logic with explicit, quadrant-by-quadrant calculation.
def calculate_sripati_house_cusps(time_obj, latitude, longitude_east_deg, ayanamsa_deg):
    prim = calculate_lagna_and_primaries(time_obj, latitude, longitude_east_deg, ayanamsa_deg)
    asc_trop = prim["asc_tropical_deg"]
    mc_trop = prim["mc_tropical_deg"]
    desc_trop = prim["desc_tropical_deg"]
    ic_trop = prim["ic_tropical_deg"]

    cusps_trop = [0.0] * 12

    # Set cardinal cusps
    cusps_trop[0] = asc_trop   # 1st House
    cusps_trop[3] = ic_trop    # 4th House
    cusps_trop[6] = desc_trop  # 7th House
    cusps_trop[9] = mc_trop    # 10th House

    # Calculate intermediate cusps by trisecting the arcs in zodiacal order
    # Arc between 1st and 4th houses (for cusps 2, 3)
    arc1_4 = (ic_trop - asc_trop + 360) % 360
    cusps_trop[1] = _limit360(asc_trop + arc1_4 / 3.0)
    cusps_trop[2] = _limit360(asc_trop + 2 * arc1_4 / 3.0)

    # Arc between 4th and 7th houses (for cusps 5, 6)
    arc4_7 = (desc_trop - ic_trop + 360) % 360
    cusps_trop[4] = _limit360(ic_trop + arc4_7 / 3.0)
    cusps_trop[5] = _limit360(ic_trop + 2 * arc4_7 / 3.0)

    # Arc between 7th and 10th houses (for cusps 8, 9)
    arc7_10 = (mc_trop - desc_trop + 360) % 360
    cusps_trop[7] = _limit360(desc_trop + arc7_10 / 3.0)
    cusps_trop[8] = _limit360(desc_trop + 2 * arc7_10 / 3.0)

    # Arc between 10th and 1st houses (for cusps 11, 12)
    arc10_1 = (asc_trop - mc_trop + 360) % 360
    cusps_trop[10] = _limit360(mc_trop + arc10_1 / 3.0)
    cusps_trop[11] = _limit360(mc_trop + 2 * arc10_1 / 3.0)

    # Convert all tropical cusps to sidereal
    cusps_sid = [_limit360(c - ayanamsa_deg) for c in cusps_trop]
    return {"cusps_sid": cusps_sid, "primaries": prim}