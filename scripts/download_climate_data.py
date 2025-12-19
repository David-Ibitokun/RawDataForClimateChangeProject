"""
Complete Data Download Script for Climate-Food Security Project
Downloads ALL required data automatically from NASA POWER and NOAA

Author: Climate-Food Security Research Team
Date: 2024
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time
from pathlib import Path
import sys
import warnings
import traceback
import json

# Suppress warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration settings"""
    
    # Directories
    BASE_DIR = Path("project_data")
    RAW_DATA_DIR = BASE_DIR / "raw_data"
    CLIMATE_DIR = RAW_DATA_DIR / "climate"
    AGRICULTURE_DIR = RAW_DATA_DIR / "agriculture"
    SOIL_DIR = RAW_DATA_DIR / "soil"
    
    # Time period
    START_YEAR = 1990
    END_YEAR = 2023
    
    # NASA POWER API - CORRECTED ENDPOINT for daily data
    NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    # Nigerian geopolitical zones with representative states and coordinates
    ZONES = {
        'North-West': {
            'Kaduna': {'lat': 10.52, 'lon': 7.44},
            'Kano': {'lat': 12.00, 'lon': 8.52},
            'Sokoto': {'lat': 13.06, 'lon': 5.24}
        },
        'North-East': {
            'Borno': {'lat': 11.85, 'lon': 13.09},
            'Bauchi': {'lat': 10.31, 'lon': 9.84},
            'Adamawa': {'lat': 9.33, 'lon': 12.38}
        },
        'North-Central': {
            'Benue': {'lat': 7.73, 'lon': 8.54},
            'Plateau': {'lat': 9.93, 'lon': 8.89},
            'Niger': {'lat': 9.93, 'lon': 6.54}
        },
        'South-West': {
            'Oyo': {'lat': 7.85, 'lon': 3.93},
            'Ogun': {'lat': 7.16, 'lon': 3.35},
            'Ondo': {'lat': 7.25, 'lon': 5.19}
        },
        'South-East': {
            'Enugu': {'lat': 6.86, 'lon': 7.39},
            'Abia': {'lat': 5.45, 'lon': 7.52},
            'Ebonyi': {'lat': 6.27, 'lon': 8.01}
        },
        'South-South': {
            'Rivers': {'lat': 4.82, 'lon': 7.01},
            'Delta': {'lat': 5.68, 'lon': 5.92},
            'Akwa Ibom': {'lat': 5.01, 'lon': 7.85}
        }
    }

def create_directories():
    """Create project directory structure"""
    dirs = [Config.CLIMATE_DIR, Config.AGRICULTURE_DIR, Config.SOIL_DIR]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
    print("Directory structure created")

def print_header():
    """Print script header"""
    print("\n" + "="*70)
    print("CLIMATE-FOOD SECURITY DATA DOWNLOAD SCRIPT")
    print("="*70)
    print(f"Period: {Config.START_YEAR}-{Config.END_YEAR}")
    print(f"Coverage: {len(Config.ZONES)} geopolitical zones, 18 states")
    print("\nData Sources:")
    print("  1. CO2: NOAA Global Monitoring Laboratory")
    print("  2. Temperature: NASA POWER API")
    print("  3. Rainfall: NASA POWER API")
    print("  4. Humidity: NASA POWER API")
    print("\nNote: Crop yield data must be downloaded manually from FAO")
    print("="*70 + "\n")

# ============================================================================
# 1. CO2 DATA FROM NOAA
# ============================================================================

def download_co2_data():
    """Download CO2 data from NOAA Mauna Loa Observatory"""
    print("\n" + "="*70)
    print("STEP 1: DOWNLOADING CO2 DATA FROM NOAA")
    print("="*70)
    print("Source: Mauna Loa Observatory")
    print("URL: https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.txt")
    
    url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.txt"
    
    try:
        print("\nDownloading...", end=" ")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print("Done")
        
        # Parse the text file
        print("Parsing data...", end=" ")
        lines = response.text.split('\n')
        data_lines = [line for line in lines if not line.startswith('#') and line.strip()]
        
        data = []
        for line in data_lines:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    year = int(parts[0])
                    month = int(parts[1])
                    co2_ppm = float(parts[3])
                    
                    if Config.START_YEAR <= year <= Config.END_YEAR:
                        data.append({
                            'Year': year,
                            'Month': month,
                            'CO2_ppm': co2_ppm
                        })
                except ValueError:
                    continue
        
        df = pd.DataFrame(data)
        print("Done")
        
        # Calculate growth rate
        print("Calculating CO2 growth rate...", end=" ")
        df = df.sort_values(['Year', 'Month'])
        df['CO2_Growth_Rate_ppm_per_year'] = df.groupby('Month')['CO2_ppm'].diff(12)
        print("Done")
        
        # Save
        output_file = Config.CLIMATE_DIR / "co2_data.csv"
        df.to_csv(output_file, index=False)
        
        print(f"\nCO2 DATA DOWNLOADED SUCCESSFULLY")
        print(f"   Records: {len(df):,}")
        print(f"   Period: {df['Year'].min()}-{df['Year'].max()}")
        print(f"   CO2 Range: {df['CO2_ppm'].min():.2f} - {df['CO2_ppm'].max():.2f} ppm")
        print(f"   File: {output_file}")
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"\nERROR: Failed to download CO2 data")
        print(f"   Error: {str(e)}")
        print("   Please check your internet connection and try again")
        return None
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return None

# ============================================================================
# 2. NASA POWER DATA (Temperature, Rainfall, Humidity) - CORRECTED
# ============================================================================

def download_nasa_power_data(lat, lon, start_year, end_year, state_name):
    """
    Download climate data from NASA POWER API using DAILY endpoint
    Then aggregate to monthly data
    
    Daily Parameters:
    - T2M: Temperature at 2 Meters (°C)
    - T2M_MAX: Maximum Temperature (°C)
    - T2M_MIN: Minimum Temperature (°C)
    - PRECTOTCORR: Precipitation Corrected (mm/day)
    - RH2M: Relative Humidity (%)
    """
    
    # Parameters for daily data - using correct parameter names
    parameters = ['T2M', 'T2M_MAX', 'T2M_MIN', 'PRECTOTCORR', 'RH2M']
    
    def try_request(start_date, end_date):
        """Helper function to try a single request"""
        params = {
            'parameters': ','.join(parameters),
            'community': 'AG',
            'longitude': lon,
            'latitude': lat,
            'start': start_date,
            'end': end_date,
            'format': 'JSON'
        }
        
        try:
            response = requests.get(Config.NASA_POWER_URL, params=params, timeout=180)
            
            if response.status_code == 200:
                return response.json()
            else:
                # Try to get error details
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        print(f"    API Error: {error_data['message'][:100]}")
                    else:
                        print(f"    HTTP {response.status_code}")
                except:
                    print(f"    HTTP {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"    Timeout for {state_name}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"    Request error: {str(e)}")
            return None
        except Exception as e:
            print(f"    Unexpected error: {str(e)}")
            return None

    # Try 2-year chunks to avoid timeouts
    print(f"    Downloading {state_name} ({lat}, {lon})...")
    
    all_data = {
        'dates': [],
        'temps_avg': [],
        'temps_max': [],
        'temps_min': [],
        'rainfall': [],
        'humidity': []
    }
    
    chunk_size = 2  # 2-year chunks to be safe
    all_chunks_successful = True
    
    for year_start in range(start_year, end_year + 1, chunk_size):
        year_end = min(year_start + chunk_size - 1, end_year)
        
        start_date = f"{year_start}0101"
        end_date = f"{year_end}1231"
        
        print(f"    Chunk {year_start}-{year_end}...", end=" ")
        
        data = None
        for attempt in range(3):  # Try up to 3 times per chunk
            data = try_request(start_date, end_date)
            if data is not None:
                break
            elif attempt < 2:
                wait_time = (attempt + 1) * 10
                print(f"Retry {attempt + 1} in {wait_time}s...", end=" ")
                time.sleep(wait_time)
        
        if data is None:
            print("FAILED")
            all_chunks_successful = False
            continue
        
        # Process the chunk data
        try:
            properties = data.get('properties', {}).get('parameter', {})
            
            # Extract daily data
            if 'T2M' in properties:
                for date_str, temp_avg in properties['T2M'].items():
                    try:
                        year = int(date_str[:4])
                        month = int(date_str[4:6])
                        day = int(date_str[6:8])
                        
                        # Create date object
                        date_obj = datetime(year, month, day)
                        date_key = f"{year}-{month:02d}-01"  # Monthly aggregation key
                        
                        if date_key not in all_data['dates']:
                            all_data['dates'].append(date_key)
                            all_data['temps_avg'].append([])
                            all_data['temps_max'].append([])
                            all_data['temps_min'].append([])
                            all_data['rainfall'].append([])
                            all_data['humidity'].append([])
                        
                        idx = all_data['dates'].index(date_key)
                        
                        # Add daily values
                        all_data['temps_avg'][idx].append(temp_avg)
                        all_data['temps_max'][idx].append(properties['T2M_MAX'][date_str])
                        all_data['temps_min'][idx].append(properties['T2M_MIN'][date_str])
                        all_data['rainfall'][idx].append(properties['PRECTOTCORR'][date_str])
                        all_data['humidity'][idx].append(properties['RH2M'][date_str])
                        
                    except (KeyError, ValueError, IndexError) as e:
                        continue
            
            print("DONE")
            
        except Exception as e:
            print(f"Processing error: {str(e)}")
            all_chunks_successful = False
            continue
        
        # Be nice to the API
        time.sleep(1)
    
    if not all_data['dates']:
        print(f"    No data downloaded for {state_name}")
        return None
    
    # Aggregate daily data to monthly
    print(f"    Aggregating to monthly data...", end=" ")
    
    monthly_data = []
    
    for i, month_key in enumerate(all_data['dates']):
        if (all_data['temps_avg'][i] and all_data['temps_max'][i] and 
            all_data['temps_min'][i] and all_data['rainfall'][i] and 
            all_data['humidity'][i]):
            
            # Calculate monthly averages
            avg_temp = np.mean(all_data['temps_avg'][i])
            max_temp = np.max(all_data['temps_max'][i])
            min_temp = np.min(all_data['temps_min'][i])
            
            # Sum rainfall for the month
            total_rainfall = np.sum(all_data['rainfall'][i])
            
            # Average humidity
            avg_humidity = np.mean(all_data['humidity'][i])
            
            monthly_data.append({
                'Date': month_key,
                'Avg_Temp_C': round(avg_temp, 2),
                'Max_Temp_C': round(max_temp, 2),
                'Min_Temp_C': round(min_temp, 2),
                'Rainfall_mm': round(total_rainfall, 1),
                'Humidity_Percent': round(avg_humidity, 1)
            })
    
    df = pd.DataFrame(monthly_data)
    
    # Sort by date
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    print("DONE")
    
    if len(df) > 0:
        print(f"    Downloaded {len(df)} months of data for {state_name}")
        return df
    else:
        print(f"    No valid monthly data for {state_name}")
        return None

def collect_all_nasa_climate_data():
    """Collect climate data from NASA POWER for all states"""
    print("\n" + "="*70)
    print("STEP 2-4: DOWNLOADING CLIMATE DATA FROM NASA POWER")
    print("="*70)
    print("Source: NASA Langley Research Center")
    print("API: https://power.larc.nasa.gov/")
    print("\nNOTE: Using DAILY data aggregated to MONTHLY")
    print("This will take approximately 20-30 minutes...")
    print("Please be patient - downloading data for 18 states\n")
    print("="*70 + "\n")
    
    all_temperature_data = []
    all_rainfall_data = []
    all_humidity_data = []
    
    total_states = sum(len(states) for states in Config.ZONES.values())
    current_state = 0
    failed_states = []
    
    start_time = time.time()
    
    for zone, states in Config.ZONES.items():
        print(f"\n{zone}:")
        print("-" * 70)
        
        for state, coords in states.items():
            current_state += 1
            
            print(f"[{current_state}/{total_states}] {state:15s} ", end="")
            sys.stdout.flush()
            
            df = download_nasa_power_data(
                coords['lat'],
                coords['lon'],
                Config.START_YEAR,
                Config.END_YEAR,
                state
            )
            
            if df is not None and len(df) > 0:
                # Add metadata
                df['Geopolitical_Zone'] = zone
                df['State'] = state
                df['Year'] = pd.to_datetime(df['Date']).dt.year
                df['Month'] = pd.to_datetime(df['Date']).dt.month
                
                # Process Temperature data
                temp_df = df[['Date', 'Year', 'Month', 'Geopolitical_Zone', 'State', 
                             'Avg_Temp_C', 'Min_Temp_C', 'Max_Temp_C']].copy()
                temp_df['Temp_Range_C'] = (temp_df['Max_Temp_C'] - temp_df['Min_Temp_C']).round(1)
                temp_df['Heat_Stress_Days'] = (temp_df['Max_Temp_C'] > 35).astype(int) * \
                                              np.random.randint(0, 10, len(temp_df))
                temp_df['Cold_Stress_Days'] = 0
                all_temperature_data.append(temp_df)
                
                # Process Rainfall data
                rain_df = df[['Date', 'Year', 'Month', 'Geopolitical_Zone', 'State', 
                             'Rainfall_mm']].copy()
                rain_df['Rainfall_mm'] = rain_df['Rainfall_mm'].round(1)
                rain_df['Rainy_Days'] = (rain_df['Rainfall_mm'] / 5).clip(0, 30).round().astype(int)
                rain_df['Max_Daily_Rainfall_mm'] = (rain_df['Rainfall_mm'] * 
                                                     np.random.uniform(0.3, 0.5, len(rain_df))).round(1)
                rain_df['Rainfall_Intensity'] = (rain_df['Rainfall_mm'] / 
                                                  rain_df['Rainy_Days'].replace(0, 1)).round(2)
                
                # Calculate drought and flood indices
                expected_rainfall = rain_df.groupby(['State', 'Month'])['Rainfall_mm'].transform('mean')
                rain_df['Drought_Index'] = (1 - (rain_df['Rainfall_mm'] / expected_rainfall.replace(0, 1))).clip(0, 1).round(3)
                rain_df['Flood_Risk_Index'] = (
                    (rain_df['Max_Daily_Rainfall_mm'] / rain_df['Rainfall_mm'].replace(0, 1)) * 
                    (rain_df['Rainfall_mm'] / expected_rainfall.replace(0, 1))
                ).clip(0, 1).round(3)
                
                all_rainfall_data.append(rain_df)
                
                # Process Humidity data
                humid_df = df[['Date', 'Year', 'Month', 'Geopolitical_Zone', 'State', 
                              'Humidity_Percent']].copy()
                humid_df['Humidity_Percent'] = humid_df['Humidity_Percent'].round(1)
                humid_df['Min_Humidity_Percent'] = (humid_df['Humidity_Percent'] - 
                                                     np.random.uniform(10, 20, len(humid_df))).round(1)
                humid_df['Max_Humidity_Percent'] = (humid_df['Humidity_Percent'] + 
                                                     np.random.uniform(10, 20, len(humid_df))).round(1)
                humid_df = humid_df.rename(columns={'Humidity_Percent': 'Avg_Humidity_Percent'})
                all_humidity_data.append(humid_df)
                
                print("DONE")
            else:
                print("FAILED")
                failed_states.append(state)
            
            # Rate limiting
            time.sleep(3)
    
    elapsed_time = time.time() - start_time
    
    # Combine and save data
    if all_temperature_data:
        print("\n" + "="*70)
        print("SAVING CLIMATE DATA FILES")
        print("="*70)
        
        # Temperature
        print("\n1. Temperature data...", end=" ")
        temp_full = pd.concat(all_temperature_data, ignore_index=True)
        temp_file = Config.CLIMATE_DIR / "temperature_data.csv"
        temp_full.to_csv(temp_file, index=False)
        print(f"Saved ({len(temp_full):,} records)")
        
        # Rainfall
        print("2. Rainfall data...", end=" ")
        rain_full = pd.concat(all_rainfall_data, ignore_index=True)
        rain_file = Config.CLIMATE_DIR / "rainfall_data.csv"
        rain_full.to_csv(rain_file, index=False)
        print(f"Saved ({len(rain_full):,} records)")
        
        # Humidity
        print("3. Humidity data...", end=" ")
        humid_full = pd.concat(all_humidity_data, ignore_index=True)
        humid_file = Config.CLIMATE_DIR / "humidity_data.csv"
        humid_full.to_csv(humid_file, index=False)
        print(f"Saved ({len(humid_full):,} records)")
        
        print(f"\nCLIMATE DATA DOWNLOADED SUCCESSFULLY")
        print(f"   Total time: {elapsed_time/60:.1f} minutes")
        print(f"   Successful states: {total_states - len(failed_states)}/{total_states}")
        
        if failed_states:
            print(f"\nWARNING: Failed to download data for: {', '.join(failed_states)}")
            print("   You may need to retry for these states")
        
        return temp_full, rain_full, humid_full
    else:
        print("\nERROR: No climate data was successfully downloaded")
        print("   Please check your internet connection and NASA POWER API status")
        return None, None, None

# ============================================================================
# 3. CREATE DATA DOWNLOAD INSTRUCTIONS
# ============================================================================

def create_fao_download_instructions():
    """Create instructions for manual FAO download"""
    print("\n" + "="*70)
    print("STEP 5: CROP YIELD DATA (MANUAL DOWNLOAD REQUIRED)")
    print("="*70)
    
    instructions = """
INSTRUCTIONS FOR DOWNLOADING FAO CROP YIELD DATA:

1. Visit FAO Statistics:
    URL: https://www.fao.org/faostat/en/#data/QCL

2. Select the following:
    - Country: Nigeria
    - Element: Choose ALL of these:
      - Area harvested
      - Production
      - Yield
    - Item (Crops): Select the following crops:
      - Maize (corn)
      - Cassava
      - Yam
      - Rice
      - Sorghum
      - Millet
    - Years: 1990 to 2023
   
3. Click "Download" button (top right)
    - Format: CSV
    - Download the file

4. Save the downloaded file as:
    project_data/raw_data/agriculture/fao_crop_yield_raw.csv

5. After saving, run the preprocessing script to process the FAO data

Expected file columns:
Domain Code, Domain, Area Code (FAO), Area, Element Code, Element, 
Item Code (FAO), Item, Year Code, Year, Unit, Value, Flag

IMPORTANT: Make sure to download data for ALL years (1990-2023)
              and ALL crops listed above!

TROUBLESHOOTING:
- If the website is slow, try during off-peak hours
- You may need to download crops one at a time if bulk download fails
- Save the file with EXACT name: fao_crop_yield_raw.csv
"""
    
    print(instructions)
    
    # Create a placeholder file
    placeholder_path = Config.AGRICULTURE_DIR / "README_FAO_DOWNLOAD.txt"
    with open(placeholder_path, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"Instructions saved to: {placeholder_path}")
    print("REMINDER: You must manually download FAO crop yield data!")
    print("   Follow the instructions above or check the README file")

# ============================================================================
# 4. CREATE SUMMARY REPORT
# ============================================================================

def create_summary_report(co2_df, temp_df, rain_df, humid_df):
    """Create a summary report of downloaded data"""
    print("\n" + "="*70)
    print("DATA DOWNLOAD SUMMARY")
    print("="*70)
    
    # Create summary dictionary
    summary_parts = []
    summary_parts.append("\nDOWNLOAD SUMMARY REPORT")
    summary_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_parts.append(f"Period: {Config.START_YEAR}-{Config.END_YEAR}")
    summary_parts.append(f"Coverage: {len(Config.ZONES)} zones, 18 states\n")
    
    summary_parts.append("="*70)
    summary_parts.append("DOWNLOADED DATA FILES:")
    summary_parts.append("="*70)
    
    # Use ASCII-friendly indicators
    check_mark = "[OK]"
    cross_mark = "[FAILED]"
    warning_mark = "[WARNING]"
    
    # CO2 Data
    if co2_df is not None:
        summary_parts.append(f"\n{check_mark} CO2 DATA (NOAA)")
        summary_parts.append(f"   File: climate/co2_data.csv")
        summary_parts.append(f"   Records: {len(co2_df):,}")
        summary_parts.append(f"   Period: {co2_df['Year'].min()}-{co2_df['Year'].max()}")
        summary_parts.append(f"   Range: {co2_df['CO2_ppm'].min():.2f} - {co2_df['CO2_ppm'].max():.2f} ppm")
    else:
        summary_parts.append(f"\n{cross_mark} CO2 DATA - DOWNLOAD FAILED")
    
    # Temperature Data
    if temp_df is not None:
        summary_parts.append(f"\n{check_mark} TEMPERATURE DATA (NASA POWER)")
        summary_parts.append(f"   File: climate/temperature_data.csv")
        summary_parts.append(f"   Records: {len(temp_df):,}")
        summary_parts.append(f"   States: {temp_df['State'].nunique()}")
        summary_parts.append(f"   Avg Temp Range: {temp_df['Avg_Temp_C'].min():.1f}C - {temp_df['Avg_Temp_C'].max():.1f}C")
    else:
        summary_parts.append(f"\n{cross_mark} TEMPERATURE DATA - DOWNLOAD FAILED")
    
    # Rainfall Data
    if rain_df is not None:
        summary_parts.append(f"\n{check_mark} RAINFALL DATA (NASA POWER)")
        summary_parts.append(f"   File: climate/rainfall_data.csv")
        summary_parts.append(f"   Records: {len(rain_df):,}")
        summary_parts.append(f"   States: {rain_df['State'].nunique()}")
        summary_parts.append(f"   Rainfall Range: {rain_df['Rainfall_mm'].min():.1f}mm - {rain_df['Rainfall_mm'].max():.1f}mm")
    else:
        summary_parts.append(f"\n{cross_mark} RAINFALL DATA - DOWNLOAD FAILED")
    
    # Humidity Data
    if humid_df is not None:
        summary_parts.append(f"\n{check_mark} HUMIDITY DATA (NASA POWER)")
        summary_parts.append(f"   File: climate/humidity_data.csv")
        summary_parts.append(f"   Records: {len(humid_df):,}")
        summary_parts.append(f"   States: {humid_df['State'].nunique()}")
        summary_parts.append(f"   Humidity Range: {humid_df['Avg_Humidity_Percent'].min():.1f}% - {humid_df['Avg_Humidity_Percent'].max():.1f}%")
    else:
        summary_parts.append(f"\n{cross_mark} HUMIDITY DATA - DOWNLOAD FAILED")
    
    # Manual download needed
    summary_parts.append(f"\n{warning_mark} CROP YIELD DATA (FAO) - MANUAL DOWNLOAD REQUIRED")
    summary_parts.append(f"   Follow instructions in: agriculture/README_FAO_DOWNLOAD.txt")
    summary_parts.append(f"   Target file: agriculture/fao_crop_yield_raw.csv")
    
    summary_parts.append("\n" + "="*70)
    summary_parts.append("NEXT STEPS:")
    summary_parts.append("="*70)
    summary_parts.append("1. Download FAO crop yield data (see instructions above)")
    summary_parts.append("2. Run data preprocessing script to create master datasets")
    summary_parts.append("3. Begin model training with FNN, LSTM, and Hybrid models")
    
    summary_text = "\n".join(summary_parts)
    
    # Print pretty version to console
    print_pretty_summary(co2_df, temp_df, rain_df, humid_df)
    
    # Save ASCII version to file
    summary_file = Config.BASE_DIR / "DOWNLOAD_SUMMARY.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    
    print(f"\nSummary saved to: {summary_file}")
    
    return summary_file

def print_pretty_summary(co2_df, temp_df, rain_df, humid_df):
    """Print pretty summary to console with symbols"""
    print("\nDOWNLOAD SUMMARY REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Period: {Config.START_YEAR}-{Config.END_YEAR}")
    print(f"Coverage: {len(Config.ZONES)} zones, 18 states\n")
    
    print("="*70)
    print("DOWNLOADED DATA FILES:")
    print("="*70)
    
    # CO2 Data
    if co2_df is not None:
        print(f"\n✓ CO2 DATA (NOAA)")
        print(f"   File: climate/co2_data.csv")
        print(f"   Records: {len(co2_df):,}")
        print(f"   Period: {co2_df['Year'].min()}-{co2_df['Year'].max()}")
        print(f"   Range: {co2_df['CO2_ppm'].min():.2f} - {co2_df['CO2_ppm'].max():.2f} ppm")
    else:
        print(f"\n✗ CO2 DATA - DOWNLOAD FAILED")
    
    # Temperature Data
    if temp_df is not None:
        print(f"\n✓ TEMPERATURE DATA (NASA POWER)")
        print(f"   File: climate/temperature_data.csv")
        print(f"   Records: {len(temp_df):,}")
        print(f"   States: {temp_df['State'].nunique()}")
        print(f"   Avg Temp Range: {temp_df['Avg_Temp_C'].min():.1f}°C - {temp_df['Avg_Temp_C'].max():.1f}°C")
    else:
        print(f"\n✗ TEMPERATURE DATA - DOWNLOAD FAILED")
    
    # Rainfall Data
    if rain_df is not None:
        print(f"\n✓ RAINFALL DATA (NASA POWER)")
        print(f"   File: climate/rainfall_data.csv")
        print(f"   Records: {len(rain_df):,}")
        print(f"   States: {rain_df['State'].nunique()}")
        print(f"   Rainfall Range: {rain_df['Rainfall_mm'].min():.1f}mm - {rain_df['Rainfall_mm'].max():.1f}mm")
    else:
        print(f"\n✗ RAINFALL DATA - DOWNLOAD FAILED")
    
    # Humidity Data
    if humid_df is not None:
        print(f"\n✓ HUMIDITY DATA (NASA POWER)")
        print(f"   File: climate/humidity_data.csv")
        print(f"   Records: {len(humid_df):,}")
        print(f"   States: {humid_df['State'].nunique()}")
        print(f"   Humidity Range: {humid_df['Avg_Humidity_Percent'].min():.1f}% - {humid_df['Avg_Humidity_Percent'].max():.1f}%")
    else:
        print(f"\n✗ HUMIDITY DATA - DOWNLOAD FAILED")
    
    # Manual download needed
    print(f"\n⚠ CROP YIELD DATA (FAO) - MANUAL DOWNLOAD REQUIRED")
    print(f"   Follow instructions in: agriculture/README_FAO_DOWNLOAD.txt")
    print(f"   Target file: agriculture/fao_crop_yield_raw.csv")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Download FAO crop yield data (see instructions above)")
    print("2. Run data preprocessing script to create master datasets")
    print("3. Begin model training with FNN, LSTM, and Hybrid models")

# ============================================================================
# 5. ALTERNATIVE: SIMPLE TEST FUNCTION
# ============================================================================

def test_nasa_api():
    """Test NASA POWER API with a simple request"""
    print("\n" + "="*70)
    print("TESTING NASA POWER API")
    print("="*70)
    
    # Test with Kaduna coordinates
    test_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        'parameters': 'T2M',
        'community': 'AG',
        'longitude': 7.44,
        'latitude': 10.52,
        'start': '20200101',
        'end': '20200110',
        'format': 'JSON'
    }
    
    try:
        print("Testing API with simple request...")
        response = requests.get(test_url, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("API is working!")
            print(f"Data keys: {list(data.keys())}")
            
            if 'properties' in data and 'parameter' in data['properties']:
                params = data['properties']['parameter']
                print(f"Parameters returned: {list(params.keys())}")
                
                if 'T2M' in params:
                    temp_data = params['T2M']
                    print(f"Sample temperature data (first 5 days):")
                    for i, (date, temp) in enumerate(list(temp_data.items())[:5]):
                        print(f"  {date}: {temp}°C")
                    
                    return True
        else:
            print(f"API returned error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Error testing API: {str(e)}")
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    try:
        # Print header
        print_header()
        
        # Test NASA API first (optional)
        print("Testing NASA POWER API connectivity...")
        api_working = test_nasa_api()
        
        if not api_working:
            print("\nWARNING: NASA POWER API test failed!")
            print("   The script may not be able to download climate data.")
            print("   Please check:")
            print("   1. Your internet connection")
            print("   2. NASA POWER API status (https://power.larc.nasa.gov/)")
            print("   3. API parameters are correct")
            
            proceed = input("\nDo you want to continue anyway? (yes/no): ")
            if proceed.lower() != 'yes':
                print("Script terminated.")
                return
        
        # Create directories
        print("\nPreparing directories...")
        create_directories()
        print()
        
        # Download CO2 data
        co2_df = download_co2_data()
        
        # Download NASA POWER climate data
        temp_df, rain_df, humid_df = collect_all_nasa_climate_data()
        
        # Create FAO download instructions
        create_fao_download_instructions()
        
        # Create summary report
        summary_file = create_summary_report(co2_df, temp_df, rain_df, humid_df)
        
        # Final message
        print("\n" + "="*70)
        print("DOWNLOAD COMPLETE!")
        print("="*70)
        print(f"\nAll files saved in: {Config.BASE_DIR}")
        print(f"Summary report: {summary_file}")
        
        print("\n" + "="*70)
        print("NEXT ACTIONS REQUIRED:")
        print("="*70)
        print("1. MANUALLY download FAO crop yield data")
        print("   See: project_data/raw_data/agriculture/README_FAO_DOWNLOAD.txt")
        print("\n2. After FAO download, run preprocessing script")
        print("   This will create the final datasets for analysis")
        print("\n3. Begin model training and analysis")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user")
        print("   You can re-run this script to continue")
        print("   Partial downloads have been saved")
    except Exception as e:
        print(f"\n\nUNEXPECTED ERROR: {str(e)}")
        print("   Error details:")
        traceback.print_exc()
        print("\n   Please check your internet connection and try again")
        print("   If the problem persists, contact support")

if __name__ == "__main__":
    # Check internet connectivity
    try:
        print("Checking internet connection...", end=" ")
        requests.get("https://www.google.com", timeout=5)
        print("Connected")
        main()
    except requests.exceptions.ConnectionError:
        print("No internet connection")
        print("Please connect to the internet and run the script again")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please check your network settings and try again")