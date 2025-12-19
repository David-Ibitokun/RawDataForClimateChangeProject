# Data Sources and Download Procedures

This document describes where the project data come from, how the scripts fetch them, what parameters and endpoints are used, processing steps applied in the repository, expected output file locations and formats, and known caveats.

## Overview

- Project scripts:
  - `scripts/download_climate_data.py` — automated download and aggregation of CO2 (NOAA), climate variables (NASA POWER), and creation of FAO manual instructions.
  - `scripts/download_soil_data.py` — soil properties fetched from ISDA soil API and elevation from Open-Meteo.

- Output directory: `project_data/raw_data/` with subfolders:
  - `climate/` — `co2_data.csv`, `temperature_data.csv`, `rainfall_data.csv`, `humidity_data.csv`
  - `agriculture/` — `README_FAO_DOWNLOAD.txt` (manual instructions); expected manual file: `fao_crop_yield_raw.csv`
  - `soil/` — `nigeria_soil_complete.csv`

## NOAA CO2 (Mauna Loa)

- Source: NOAA Global Monitoring Laboratory (Mauna Loa)
- URL: https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.txt
- Script: `download_co2_data()` in `scripts/download_climate_data.py`
- Period: Config.START_YEAR — Config.END_YEAR (default 1990–2023)
- Procedure:
  1. Script performs an HTTP GET to the text file URL.
  2. Lines starting with `#` are ignored; numerical columns are parsed.
  3. The script extracts Year, Month, and monthly mean CO2 (ppm) for the configured period.
  4. The script computes the 12-month growth for each month as `CO2_Growth_Rate_ppm_per_year`.
  5. Output: CSV `project_data/raw_data/climate/co2_data.csv` with columns `Year, Month, CO2_ppm, CO2_Growth_Rate_ppm_per_year`.

## NASA POWER (Climate: Temperature, Precipitation, Humidity)

- Source: NASA Langley Research Center — POWER API
- API docs / base: https://power.larc.nasa.gov/
- Endpoint(s) used by the project:
  - Monthly or daily point endpoints: e.g. `https://power.larc.nasa.gov/api/temporal/monthly/point` or `.../daily/point` (the repository's active script may use the daily endpoint and aggregate to monthly).
- Parameters requested (example): `T2M`, `T2M_MAX`, `T2M_MIN`, `PRECTOTCORR`, `RH2M` (average temperature, max/min temperature, corrected precipitation, relative humidity).

- Procedure implemented in `download_nasa_power_data()`:
  1. Build HTTP GET requests to the POWER point endpoint with query arguments:
     - `parameters`: comma-separated parameter list
     - `community=AG`
     - `latitude`, `longitude`
     - `start`, `end` (dates; scripts try YYYYMMDD or other accepted formats)
     - `format=JSON`
  2. To avoid server-side errors for long ranges, the script uses chunked requests (e.g., 2–5 year windows). The code retries chunks several times and uses short sleeps between calls.
  3. For daily endpoint usage: the script collects daily values per chunk, converts precipitation from mm/day to monthly totals by summing daily `PRECTOTCORR` (or multiplying daily mean by days in month if the API returns daily mean) and aggregates daily values to monthly statistics:
     - Monthly `Avg_Temp_C`: mean of daily `T2M`
     - Monthly `Max_Temp_C`: max of daily `T2M_MAX`
     - Monthly `Min_Temp_C`: min of daily `T2M_MIN`
     - Monthly `Rainfall_mm`: sum of daily `PRECTOTCORR` (or daily*days_in_month conversion used in some script versions)
     - Monthly `Humidity_Percent`: mean of daily `RH2M`
  4. Rate limiting: the script sleeps (e.g., 1–3 seconds) between API calls to avoid throttling.
  5. Error handling: the script logs request errors and continues; failed states are collected in a `failed_states` list.

- Output: monthly CSVs saved under `project_data/raw_data/climate/`:
  - `temperature_data.csv` — monthly records with metadata columns: `Date, Year, Month, Geopolitical_Zone, State, Avg_Temp_C, Min_Temp_C, Max_Temp_C, Temp_Range_C, Heat_Stress_Days, Cold_Stress_Days`.
  - `rainfall_data.csv` — monthly precipitation, derived metrics: `Rainy_Days, Max_Daily_Rainfall_mm, Rainfall_Intensity, Drought_Index, Flood_Risk_Index`.
  - `humidity_data.csv` — monthly humidity statistics and derived min/max estimates.

- Units and notes:
  - Temperature: degrees Celsius (°C).
  - Precipitation: mm per month (aggregated from daily mm/day).
  - Relative humidity: percent (%).
  - Dates in outputs are stored as `YYYY-MM-01` (month start date string).

## FAO Crop Yield (Manual)

- Source: FAO STAT (FAOSTAT) — Crop production & yield data
- URL: https://www.fao.org/faostat/en/#data/QCL
- Rationale: FAO data export requires interactive selection; the repository provides manual instructions to ensure correct filters and license compliance.
- Instructions are written to `project_data/raw_data/agriculture/README_FAO_DOWNLOAD.txt`. The expected manual CSV filename is `project_data/raw_data/agriculture/fao_crop_yield_raw.csv`.

## ISDA Soil API (Soil properties) and Open-Meteo Elevation

- Script: `scripts/download_soil_data.py`
- ISDA API domain used: `https://api.isda-africa.com` (endpoint `/isdasoil/v2/soilproperty`). Authentication performed via `/login` to obtain an access token.
- For each representative location (state coordinates), the script:
  1. Authenticates and obtains a bearer token.
  2. Calls the soil property endpoint with `lat`, `lon`, and `depth` (e.g., `0-20`).
  3. Extracts returned properties such as `ph`, `carbon_organic`, `sand_content`, `clay_content`, `nitrogen_total`, `phosphorous_extractable`, `potassium_extractable`, `cation_exchange_capacity`, `bulk_density`.
  4. Applies transformations:
     - pH scaling where required (scripts sometimes divide integer pH by 10)
     - `back_transform()` exponential back-transform for modeled concentrations
     - Compute `Organic_Matter_Percent` from organic carbon using factor 1.724
     - Texture class mapping (USDA-like) based on sand/clay percentages
  5. Elevation is retrieved from Open-Meteo: `https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}` and included as `Elevation_m`.

- Output: `project_data/raw_data/soil/nigeria_soil_complete.csv` with columns such as `Geopolitical_Zone, State, Latitude, Longitude, Elevation_m, Soil_Type, Soil_Texture, Soil_pH, Organic_Matter_Percent, Nitrogen_ppm, Phosphorus_ppm, Potassium_ppm, Cation_Exchange_Capacity, Bulk_Density, Water_Holding_Capacity_Percent`.

## Data Quality, Error Handling, and Known Caveats

- NASA POWER:
  - Long-range requests can cause HTTP 422 or timeouts; chunking (2–5 year windows) and retries are used to mitigate this.
  - Parameter names and endpoint paths must match the POWER API docs — verify if any failure occurs.

- NOAA CO2:
  - The plain-text file format may change; parsing currently ignores commented lines beginning with `#`.

- ISDA Soil API:
  - The script includes credentials in the current version — rotate and remove plaintext credentials and prefer environment variables.
  - API response structure can vary; the script uses safe getters and default fallbacks when fields are missing.

- FAO:
  - Manual download is recommended to ensure correct filters and compliance with FAO terms.

## Provenance & Citation

- Cite data providers when publishing results:
  - NOAA GML (Mauna Loa CO2)
  - NASA POWER (Langley Research Center)
  - FAOSTAT (FAO)
  - ISDA / Open-Meteo (soil & elevation sources)

## Quick Commands

To run the main download script (writes `download_log.txt`):
```
python scripts/download_climate_data.py > download_log.txt 2>&1
```

To run the soil fetch script:
```
python scripts/download_soil_data.py
```

## Security & Contact

- Remove or rotate any credentials in `scripts/download_soil_data.py`. Use environment variables for secrets.
- If you need assistance with running or adapting the scripts, open an issue or contact the maintainers.

---
