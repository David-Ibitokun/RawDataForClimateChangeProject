# Project Data — Data Inventory (with Columns)

This file lists each dataset under `project_data/raw_data/` and the exact column names present in the current CSV files.

- agriculture/
  - `fao_crop_yield_raw.csv`
    - Columns: `Domain Code`, `Domain`, `Area Code (M49)`, `Area`, `Element Code`, `Element`, `Item Code (CPC)`, `Item`, `Year Code`, `Year`, `Unit`, `Value`, `Flag`, `Flag Description`, `Note`.

- climate/
  - `co2_data.csv`
    - Columns: `Year`, `Month`, `CO2_ppm`, `CO2_Growth_Rate_ppm_per_year`.

  - `temperature_data.csv`
    - Columns: `Date`, `Year`, `Month`, `Geopolitical_Zone`, `State`, `Avg_Temp_C`, `Min_Temp_C`, `Max_Temp_C`, `Temp_Range_C`, `Heat_Stress_Days`, `Cold_Stress_Days`.

  - `rainfall_data.csv`
    - Columns: `Date`, `Year`, `Month`, `Geopolitical_Zone`, `State`, `Rainfall_mm`, `Rainy_Days`, `Max_Daily_Rainfall_mm`, `Rainfall_Intensity`, `Drought_Index`, `Flood_Risk_Index`.

  - `humidity_data.csv`
    - Columns: `Date`, `Year`, `Month`, `Geopolitical_Zone`, `State`, `Avg_Humidity_Percent`, `Min_Humidity_Percent`, `Max_Humidity_Percent`.

- soil/
  - `nigeria_soil_complete.csv`
    - Columns: `Geopolitical_Zone`, `State`, `Latitude`, `Longitude`, `Elevation_m`, `Soil_Type`, `Soil_Texture`, `Soil_pH`, `Organic_Matter_Percent`, `Nitrogen_ppm`, `Phosphorus_ppm`, `Potassium_ppm`, `Cation_Exchange_Capacity`, `Bulk_Density`, `Water_Holding_Capacity_Percent`.
