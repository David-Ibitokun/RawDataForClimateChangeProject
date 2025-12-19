
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
