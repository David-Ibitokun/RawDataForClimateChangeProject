# Project Data — Data Inventory

This document summarizes the current raw data available in `project_data/raw_data/`, describes each file purpose and expected schema, and lists notes about units, provenance, and next steps.

Directory: `project_data/raw_data/`

- agriculture/
  - `fao_crop_yield_raw.csv`
    - Description: FAO crop production / yield export (manual). Expected FAOSTAT columns include: Domain Code, Domain, Area Code, Area, Element Code, Element, Item Code, Item, Year Code, Year, Unit, Value, Flag. Contains crop-level annual data (user-downloaded for Nigeria, 1990–2023).
  - `README_FAO_DOWNLOAD.txt` — instructions for manually exporting the FAO data (filters, crops, years).

- climate/
  - `co2_data.csv`
    - Description: Monthly Mauna Loa CO2 records parsed from NOAA GML.
    - Expected columns: `Year`, `Month`, `CO2_ppm`, `CO2_Growth_Rate_ppm_per_year`.
    - Units: ppm (parts per million). Period: 1990–2023.
  - `temperature_data.csv`
    - Description: Monthly temperature records aggregated from NASA POWER (daily → monthly).
    - Expected columns: `Date` (YYYY-MM-01), `Year`, `Month`, `Geopolitical_Zone`, `State`, `Avg_Temp_C`, `Min_Temp_C`, `Max_Temp_C`, plus derived columns such as `Temp_Range_C`, `Heat_Stress_Days`, `Cold_Stress_Days`.
    - Units: °C. Period: 1990–2023.
  - `rainfall_data.csv`
    - Description: Monthly precipitation aggregated from NASA POWER daily PRECTOTCORR.
    - Expected columns: `Date`, `Year`, `Month`, `Geopolitical_Zone`, `State`, `Rainfall_mm`, and derived metrics `Rainy_Days`, `Max_Daily_Rainfall_mm`, `Rainfall_Intensity`, `Drought_Index`, `Flood_Risk_Index`.
    - Units: mm per month. Period: 1990–2023.
  - `humidity_data.csv`
    - Description: Monthly relative humidity aggregated from NASA POWER (RH2M).
    - Expected columns: `Date`, `Year`, `Month`, `Geopolitical_Zone`, `State`, `Avg_Humidity_Percent`, `Min_Humidity_Percent`, `Max_Humidity_Percent`.
    - Units: percent (%). Period: 1990–2023.

- soil/
  - `.env`
    - Description: Local environment file (present in `soil/`). May contain secrets or configuration for the soil download script. Treat as sensitive — do not commit or share publicly.
  - `nigeria_soil_complete.csv`
    - Description: Soil property table produced by `scripts/download_soil_data.py` for representative Nigerian states.
    - Expected columns: `Geopolitical_Zone`, `State`, `Latitude`, `Longitude`, `Elevation_m`, `Soil_Type`, `Soil_Texture`, `Soil_pH`, `Organic_Matter_Percent`, `Nitrogen_ppm`, `Phosphorus_ppm`, `Potassium_ppm`, `Cation_Exchange_Capacity`, `Bulk_Density`, `Water_Holding_Capacity_Percent`.
    - Units: pH (unitless), organic matter (%) , nutrients in ppm, elevation in meters. Period/profile: 0–20 cm (as requested by the script).

Notes and next steps

- Provenance: each file includes the source provider in `project_data/metadata/data_sources.csv` and `project_data/DATASOURCE.md` — consult those for endpoints, parameters and licensing.
- Data period: the project uses 1990–2023 for climate and CO2 data; FAO crop file should be the user-provided export for the same range.
- Quality checks recommended:
  - Verify record counts and date continuity for climate CSVs (no missing months across 1990–2023 per state).
  - Check for NaNs or sentinel values (e.g., -9999) and decide on imputation or removal.
  - Confirm units match expectations (e.g., precipitation aggregated correctly to mm/month).
- Security:
  - Remove or secure any credentials in `soil/.env` and `scripts/download_soil_data.py` (use environment variables).
- Quick commands to inspect files:
  - Show header and first lines (PowerShell):
    ```powershell
    Get-Content project_data/raw_data/climate/temperature_data.csv -TotalCount 10
    ```
  - Show row count (Windows cmd / PowerShell):
    ```powershell
    (Get-Content project_data/raw_data/climate/temperature_data.csv).Length
    ```

If you want, I can also:
- print the first 10 rows of any of these CSVs here,
- run basic validation checks (date continuity, NaN summary), or
- remove sensitive files such as `.env` from the repo and suggest secure configuration.

---

Exact column lists (from current files)

- `project_data/raw_data/climate/co2_data.csv`:
  - `Year, Month, CO2_ppm, CO2_Growth_Rate_ppm_per_year`

- `project_data/raw_data/climate/temperature_data.csv`:
  - `Date, Year, Month, Geopolitical_Zone, State, Avg_Temp_C, Min_Temp_C, Max_Temp_C, Temp_Range_C, Heat_Stress_Days, Cold_Stress_Days`

- `project_data/raw_data/climate/rainfall_data.csv`:
  - `Date, Year, Month, Geopolitical_Zone, State, Rainfall_mm, Rainy_Days, Max_Daily_Rainfall_mm, Rainfall_Intensity, Drought_Index, Flood_Risk_Index`

- `project_data/raw_data/climate/humidity_data.csv`:
  - `Date, Year, Month, Geopolitical_Zone, State, Avg_Humidity_Percent, Min_Humidity_Percent, Max_Humidity_Percent`

- `project_data/raw_data/agriculture/fao_crop_yield_raw.csv`:
  - `Domain Code, Domain, Area Code (M49), Area, Element Code, Element, Item Code (CPC), Item, Year Code, Year, Unit, Value, Flag, Flag Description, Note`

- `project_data/raw_data/soil/nigeria_soil_complete.csv`:
  - `Geopolitical_Zone, State, Latitude, Longitude, Elevation_m, Soil_Type, Soil_Texture, Soil_pH, Organic_Matter_Percent, Nitrogen_ppm, Phosphorus_ppm, Potassium_ppm, Cation_Exchange_Capacity, Bulk_Density, Water_Holding_Capacity_Percent`

