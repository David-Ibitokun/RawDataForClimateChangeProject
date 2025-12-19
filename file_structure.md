Here is the **updated CSV File Structure Guide** reflecting your actual data inventory:

---

# CSV File Structure Guide for Climate-Food Security Project  
## Updated for Six Geopolitical Zones (1990–2023)  
**Based on Actual Data Inventory**

---

## Overview  
This guide documents the **actual CSV file structures** for analyzing climate change impact on food security across Nigeria’s six geopolitical zones (1990–2023). All datasets are stored under `project_data/raw_data/`.

---

## Nigeria’s Six Geopolitical Zones

| Zone | States | Primary Crops | Climate Pattern |
|------|--------|---------------|-----------------|
| **North-West** | Sokoto, Kebbi, Katsina, Kano, Jigawa, Zamfara, Kaduna | Millet, Sorghum, Groundnut, Cowpea | Sudan Savanna, 400–800mm rainfall |
| **North-East** | Borno, Yobe, Bauchi, Gombe, Adamawa, Taraba | Sorghum, Millet, Maize, Cotton | Sahel/Sudan, 300–900mm rainfall |
| **North-Central** | Niger, Kwara, Kogi, Benue, Plateau, Nasarawa, FCT | Yam, Rice, Cassava, Soybean, Maize | Guinea Savanna, 1000–1500mm rainfall |
| **South-West** | Lagos, Ogun, Oyo, Osun, Ondo, Ekiti | Cassava, Cocoa, Maize, Yam, Plantain | Humid Forest, 1200–2000mm rainfall |
| **South-East** | Abia, Anambra, Ebonyi, Enugu, Imo | Cassava, Yam, Rice, Oil Palm | Humid Forest, 1500–2500mm rainfall |
| **South-South** | Akwa Ibom, Bayelsa, Cross River, Delta, Edo, Rivers | Cassava, Yam, Oil Palm, Plantain | Tropical Rainforest, 2000–4000mm rainfall |

---

## 1. Climate Data Files (`project_data/raw_data/climate/`)

### 1.1 `co2_data.csv`
**Temporal Granularity:** Monthly  
**Period:** 1990–2023

```csv
Year,Month,CO2_ppm,CO2_Growth_Rate_ppm_per_year
1990,1,353.50,1.35
1990,2,354.15,1.35
...
2023,12,420.89,2.48
```

**Columns:**
- `Year` – Year of observation
- `Month` – Month (1–12)
- `CO2_ppm` – Atmospheric CO₂ concentration in parts per million
- `CO2_Growth_Rate_ppm_per_year` – Annual growth rate of CO₂

---

### 1.2 `temperature_data.csv`
**Temporal Granularity:** Monthly  
**Period:** 1990–2023

```csv
Date,Year,Month,Geopolitical_Zone,State,Avg_Temp_C,Min_Temp_C,Max_Temp_C,Temp_Range_C,Heat_Stress_Days,Cold_Stress_Days
1990-01-01,1990,1,North-West,Kaduna,24.5,18.2,31.8,13.6,0,0
...
2023-12-01,2023,12,South-South,Rivers,28.8,24.5,33.1,8.6,0,0
```

**Columns:**
- `Date` – YYYY-MM-DD format
- `Year`, `Month` – Temporal identifiers
- `Geopolitical_Zone`, `State` – Spatial identifiers
- `Avg_Temp_C`, `Min_Temp_C`, `Max_Temp_C` – Temperature metrics
- `Temp_Range_C` – Daily temperature range
- `Heat_Stress_Days` – Days > 35°C
- `Cold_Stress_Days` – Days < 15°C

---

### 1.3 `rainfall_data.csv`
**Temporal Granularity:** Monthly  
**Period:** 1990–2023

```csv
Date,Year,Month,Geopolitical_Zone,State,Rainfall_mm,Rainy_Days,Max_Daily_Rainfall_mm,Rainfall_Intensity,Drought_Index,Flood_Risk_Index
1990-01-01,1990,1,North-West,Kaduna,2.5,1,2.5,2.5,0.95,0.00
...
2023-12-01,2023,12,South-East,Enugu,15.2,4,6.8,3.8,0.30,0.05
```

**Columns:**
- `Rainfall_mm` – Total monthly rainfall
- `Rainy_Days` – Number of rainy days
- `Max_Daily_Rainfall_mm` – Maximum rainfall in a single day
- `Rainfall_Intensity` – Average rainfall per rainy day
- `Drought_Index` – 0–1 (1 = severe drought)
- `Flood_Risk_Index` – 0–1 (1 = high flood risk)

---

### 1.4 `humidity_data.csv`
**Temporal Granularity:** Monthly  
**Period:** 1990–2023

```csv
Date,Year,Month,Geopolitical_Zone,State,Avg_Humidity_Percent,Min_Humidity_Percent,Max_Humidity_Percent
1990-01-01,1990,1,North-West,Kaduna,25,15,40
...
2023-12-01,2023,12,South-East,Enugu,72,60,88
```

**Columns:**
- `Avg_Humidity_Percent` – Average relative humidity
- `Min_Humidity_Percent`, `Max_Humidity_Percent` – Daily extremes

---

## 2. Agricultural Data (`project_data/raw_data/agriculture/`)

### 2.1 `fao_crop_yield_raw.csv`
**Source:** FAOSTAT manual download  
**Temporal Granularity:** Annual  
**Period:** 1990–2023

```csv
Domain Code,Domain,Area Code (M49),Area,Element Code,Element,Item Code (CPC),Item,Year Code,Year,Unit,Value,Flag,Flag Description,Note
QCL,Crops and livestock products,159,Nigeria,5510,Yield,56,Maize,1990,1990,hg/ha,15000,A,Official,...
...
```

**Columns:**
- `Domain Code`, `Domain` – Data category
- `Area Code (M49)`, `Area` – Country code and name
- `Element Code`, `Element` – Metric type (Yield, Production, Area)
- `Item Code (CPC)`, `Item` – Crop identifier
- `Year Code`, `Year` – Temporal reference
- `Unit` – Unit of measurement
- `Value` – Numerical value
- `Flag`, `Flag Description` – Data quality flags
- `Note` – Additional notes

---

## 3. Soil Data (`project_data/raw_data/soil/`)

### 3.1 `nigeria_soil_complete.csv`
**Spatial Granularity:** Per location (static)  
**Coverage:** All geopolitical zones

```csv
Geopolitical_Zone,State,Latitude,Longitude,Elevation_m,Soil_Type,Soil_Texture,Soil_pH,Organic_Matter_Percent,Nitrogen_ppm,Phosphorus_ppm,Potassium_ppm,Cation_Exchange_Capacity,Bulk_Density,Water_Holding_Capacity_Percent
North-West,Kaduna,11.11,7.70,650,Ferruginous,Sandy-Loam,6.2,2.1,45,12,95,8.5,1.45,28
...
```

**Columns:**
- `Geopolitical_Zone`, `State` – Location identifiers
- `Latitude`, `Longitude`, `Elevation_m` – Geographic coordinates
- `Soil_Type`, `Soil_Texture` – Soil classification
- `Soil_pH` – Acidity/alkalinity
- `Organic_Matter_Percent` – Soil organic content
- `Nitrogen_ppm`, `Phosphorus_ppm`, `Potassium_ppm` – NPK levels
- `Cation_Exchange_Capacity` – Nutrient retention capacity
- `Bulk_Density` – Soil compaction
- `Water_Holding_Capacity_Percent` – Moisture retention ability

---

## 4. Master Datasets for Model Training (`project_data/processed_data/`)

*These files will be created during preprocessing by merging raw data.*

### 4.1 `master_data_fnn.csv` (Annual aggregated)
**Features:**
- Climate variables averaged over growing season
- Soil properties (static)
- Crop yield as target variable

### 4.2 `master_data_lstm.csv` (Monthly time-series)
**Features:**
- Monthly climate data
- Crop growth stage indicators
- Cumulative rainfall during growing season

### 4.3 `master_data_hybrid.csv` (Monthly + Static)
**Features:**
- Temporal climate variables
- Static soil and farm characteristics
- Pest/disease risk indices

---

## 5. Data Organization Structure (Actual)

```
project_data/
│
├── raw_data/
│   ├── climate/
│   │   ├── co2_data.csv
│   │   ├── temperature_data.csv
│   │   ├── rainfall_data.csv
│   │   └── humidity_data.csv
│   │
│   ├── agriculture/
│   │   └── fao_crop_yield_raw.csv
│   │
│   └── soil/
│       └── nigeria_soil_complete.csv
│
├── processed_data/
│   ├── master_data_fnn.csv
│   ├── master_data_lstm.csv
│   └── master_data_hybrid.csv
│
├── train_test_split/
│   ├── fnn/
│   ├── lstm/
│   └── hybrid/
│
└── metadata/
    ├── geopolitical_zones.csv
    ├── crop_growing_calendar.csv
    └── data_sources.csv
```

---

## 6. Preprocessing Steps Required

1. **Clean and format `fao_crop_yield_raw.csv`:**
   - Filter for Nigeria and relevant crops
   - Convert units (e.g., hg/ha → tonnes/ha)
   - Map FAO crop codes to local crop names

2. **Merge climate data with soil data:**
   - Join by `Geopolitical_Zone` and `State`

3. **Aggregate data for FNN model:**
   - Calculate growing season averages for climate variables

4. **Create time-series for LSTM model:**
   - Align monthly climate data with crop growth stages

5. **Split data:**
   - Training (1990–2016)
   - Validation (2017–2019)
   - Testing (2020–2023)

---

## 7. Data Quality Notes

✅ **Complete datasets:**
- Climate data (CO₂, Temperature, Rainfall, Humidity) – monthly, 1990–2023
- Soil data – static, comprehensive coverage

🔄 **Requires processing:**
- FAO crop yield data – needs cleaning and disaggregation to state level

📊 **Derived indices already calculated:**
- Drought Index
- Flood Risk Index
- Rainfall Intensity
- Heat/Cold Stress Days

---

## 8. Next Steps

1. **Write preprocessing scripts** to:
   - Clean and merge raw datasets
   - Create master datasets for FNN, LSTM, and Hybrid models

2. **Generate train/validation/test splits** respecting temporal ordering

3. **Perform exploratory data analysis** to:
   - Visualize climate trends per zone
   - Correlate climate variables with crop yields

4. **Begin model development** using the processed datasets

---

*Document updated based on actual data inventory as of 2024.*