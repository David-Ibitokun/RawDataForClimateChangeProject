import requests
import pandas as pd
import numpy as np
from pathlib import Path
import time
import os
from dotenv import load_dotenv

# ============================================================================
# 1. CONFIGURATION
# ============================================================================

BASE_DIR = Path("project_data/raw_data/soil")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Load .env from BASE_DIR
load_dotenv(BASE_DIR / ".env")

USERNAME = os.getenv("ISDA_USERNAME")
PASSWORD = os.getenv("ISDA_PASSWORD")

if not USERNAME or not PASSWORD:
    raise RuntimeError(
        "Missing ISDA credentials. Ensure ISDA_USERNAME and ISDA_PASSWORD "
        "are set in project_data/raw_data/soil/.env"
    )

API_DOMAIN = "https://api.isda-africa.com"

LOCATIONS = [
    {"state": "Kaduna", "zone": "North-West", "lat": 10.52, "lon": 7.44},
    {"state": "Kano", "zone": "North-West", "lat": 12.00, "lon": 8.52},
    {"state": "Sokoto", "zone": "North-West", "lat": 13.06, "lon": 5.24},
    {"state": "Borno", "zone": "North-East", "lat": 11.85, "lon": 13.09},
    {"state": "Bauchi", "zone": "North-East", "lat": 10.31, "lon": 9.84},
    {"state": "Adamawa", "zone": "North-East", "lat": 9.33, "lon": 12.38},
    {"state": "Benue", "zone": "North-Central", "lat": 7.73, "lon": 8.54},
    {"state": "Plateau", "zone": "North-Central", "lat": 9.93, "lon": 8.89},
    {"state": "Niger", "zone": "North-Central", "lat": 9.93, "lon": 6.54},
    {"state": "Oyo", "zone": "South-West", "lat": 7.85, "lon": 3.93},
    {"state": "Ogun", "zone": "South-West", "lat": 7.16, "lon": 3.35},
    {"state": "Ondo", "zone": "South-West", "lat": 7.25, "lon": 5.19},
    {"state": "Enugu", "zone": "South-East", "lat": 6.86, "lon": 7.39},
    {"state": "Abia", "zone": "South-East", "lat": 5.45, "lon": 7.52},
    {"state": "Ebonyi", "zone": "South-East", "lat": 6.27, "lon": 8.01},
    {"state": "Rivers", "zone": "South-South", "lat": 4.82, "lon": 7.01},
    {"state": "Delta", "zone": "South-South", "lat": 5.68, "lon": 5.92},
    {"state": "Akwa Ibom", "zone": "South-South", "lat": 5.01, "lon": 7.85},
]

# ============================================================================
# 2. UTILITY FUNCTIONS
# ============================================================================

def get_elevation(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}"
        res = requests.get(url, timeout=10).json()
        return res.get("elevation", [0])[0]
    except:
        return 0


def get_texture_class(sand, clay):
    silt = 100 - (sand + clay)
    if sand >= 85 and silt + 1.5 * clay < 15:
        return "Sand", 10
    if sand >= 70 and silt + 3 * clay < 30:
        return "Loamy Sand", 15
    if 20 <= clay < 35 and silt < 28 and sand > 45:
        return "Sandy Clay Loam", 25
    if clay >= 35 and sand > 45:
        return "Sandy Clay", 35
    if 27 <= clay < 40 and 20 < sand <= 45:
        return "Clay Loam", 40
    if clay >= 40:
        return "Clay", 45
    return "Loam", 30


def get_soil_type(ph):
    if ph < 5.5:
        return "Acidic"
    if ph > 7.5:
        return "Calcareous"
    return "Ferruginous"


def back_transform(value):
    if value is None:
        return 0.0
    return np.exp(value / 10.0) - 1.0


def parse_ph(raw):
    if raw is None:
        return 6.0
    try:
        raw = float(raw)
    except:
        return 6.0

    if 0 < raw <= 14:
        return round(raw, 2)
    if 14 < raw <= 140:
        return round(raw / 10.0, 2)
    if raw > 140:
        return round(raw / 100.0, 2)
    return 6.0

# ============================================================================
# 3. AUTHENTICATION
# ============================================================================

def get_access_token():
    print(f"Authenticating as {USERNAME}...")
    try:
        response = requests.post(
            f"{API_DOMAIN}/login",
            data={
                "username": USERNAME,
                "password": PASSWORD
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=15
        )
        response.raise_for_status()

        token = response.json().get("access_token")
        if not token:
            raise ValueError("No access_token returned")

        return token
    except Exception as e:
        print(f"Login failed: {e}")
        return None

# ============================================================================
# 4. MAIN PROCESSING
# ============================================================================

def main():
    token = get_access_token()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    prop_url = f"{API_DOMAIN}/isdasoil/v2/soilproperty"
    final_data = []

    print("\nProcessing Nigerian State Soil Profiles...\n")

    for loc in LOCATIONS:
        print(f"→ {loc['state']}...", end=" ", flush=True)

        elevation = get_elevation(loc["lat"], loc["lon"])

        try:
            params = {"lat": loc["lat"], "lon": loc["lon"], "depth": "0-20"}
            response = requests.get(
                prop_url, headers=headers, params=params, timeout=20
            )

            if response.status_code != 200:
                print(f"✗ (HTTP {response.status_code})")
                continue

            data = response.json().get("property", {})

            def gv(k):
                try:
                    return data[k][0]["value"]["value"]
                except:
                    return None

            ph_val = parse_ph(gv("ph"))
            soc_g_kg = back_transform(gv("carbon_organic"))
            sand_pct = gv("sand_content") or 50
            clay_pct = gv("clay_content") or 20

            texture, whc = get_texture_class(sand_pct, clay_pct)

            final_data.append({
                "Geopolitical_Zone": loc["zone"],
                "State": loc["state"],
                "Latitude": loc["lat"],
                "Longitude": loc["lon"],
                "Elevation_m": elevation,
                "Soil_Type": get_soil_type(ph_val),
                "Soil_Texture": texture,
                "Soil_pH": ph_val,
                "Organic_Matter_Percent": round((soc_g_kg / 10.0) * 1.724, 2),
                "Nitrogen_ppm": round(back_transform(gv("nitrogen_total")) * 1000, 1),
                "Phosphorus_ppm": round(back_transform(gv("phosphorous_extractable")), 1),
                "Potassium_ppm": round(gv("potassium_extractable") or 0.0, 1),
                "Cation_Exchange_Capacity": round((gv("cation_exchange_capacity") or 100) / 10.0, 1),
                "Bulk_Density": round((gv("bulk_density") or 140) / 100.0, 2),
                "Water_Holding_Capacity_Percent": whc,
            })

            print("✓")
            time.sleep(1)

        except Exception as e:
            print(f"✗ Error: {e}")

    if final_data:
        df = pd.DataFrame(final_data)
        output_file = BASE_DIR / "nigeria_soil_complete.csv"
        df.to_csv(output_file, index=False)
        print(f"\nSUCCESS: Data saved to {output_file}")
    else:
        print("\nNo data collected.")

if __name__ == "__main__":
    main()
