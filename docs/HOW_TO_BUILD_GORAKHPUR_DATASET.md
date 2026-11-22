# 🌾 How to Build Your Custom Dataset for Gorakhpur District
### Step-by-Step Practical Guide for Field Data Collection & Synthesis

---

## 1. Understanding Gorakhpur's Agricultural Profile

Before compiling data, it helps to know Gorakhpur's specific agronomic conditions so your dataset reflects real field reality:

| Parameter | Gorakhpur Reality | Why It Matters for Nitrogen |
|---|---|---|
| **Agro-Climatic Zone** | Middle Gangetic Plain / Terai Zone | High rainfall, humid sub-tropical climate. |
| **Major River Basins** | Rapti, Rohini, Ami, Kuwana | High water tables; flood-prone lowlands (*Khadar*). |
| **Dominant Soil** | Heavy Alluvial (Clay Loam / *Bhat* soil) | Clay is 38–52%, meaning good nutrient retention but waterlogging risks. |
| **Soil pH & Organic Carbon** | pH: 6.8–7.7 (neutral); SOC: 4.5–7.8 g/kg | Generally nitrogen-deficient, requiring mineral top-dressing. |
| **Major Crops** | **Kharif**: Rice (Paddy), Sugarcane, Maize, Arhar<br>**Rabi**: Wheat, Mustard, Potato, Chickpea, Lentil<br>**Zaid**: Moong, Fodder Maize, Watermelon | Sugarcane and Rice dominate eastern tehsils (Pipraich, Chauri Chaura). |

---

## 2. Gorakhpur Tehsils & Representative Coordinates

Gorakhpur has **7 Tehsils** and **19 Development Blocks**. We have already mapped 25 real field locations across these regions in [`data/templates/gorakhpur_farm_seeds.csv`](file:///d:/My%20Projects/Python%20Projects/Modified%20Nitrogen%20GeoN-DSS/data/templates/gorakhpur_farm_seeds.csv):

| Tehsil | Sample Village / Area | Latitude (°N) | Longitude (°E) | Primary Crops |
|---|---|---|---|---|
| **Gorakhpur Sadar** | Pipraich | 26.8285 | 83.5230 | Sugarcane, Rice |
| **Gorakhpur Sadar** | Bhathat | 26.8920 | 83.4735 | Rice, Wheat |
| **Gorakhpur Sadar** | Chargaon | 26.8115 | 83.3980 | Wheat, Vegetables |
| **Gorakhpur Sadar** | Khorabar | 26.7150 | 83.4250 | Mustard, Wheat |
| **Campierganj** | Peppeganj | 26.9380 | 83.3150 | Sugarcane, Potato |
| **Campierganj** | Campierganj Town | 27.0250 | 83.3480 | Rice, Wheat |
| **Campierganj** | Jungle Kaudia | 26.8550 | 83.3100 | Wheat, Maize |
| **Sahjanwa** | Sahjanwa Town | 26.7720 | 83.1850 | Maize, Wheat |
| **Sahjanwa** | Pali | 26.8050 | 83.1350 | Potato, Mustard |
| **Chauri Chaura** | Sardar Nagar | 26.6850 | 83.5650 | Sugarcane (Sugar mill belt) |
| **Chauri Chaura** | Chauri Chaura | 26.6450 | 83.5950 | Rice, Wheat |
| **Chauri Chaura** | Mundera Bazar | 26.6500 | 83.5800 | Vegetables, Onion |
| **Bansgaon** | Bansgaon Town | 26.5550 | 83.3550 | Wheat, Arhar |
| **Bansgaon** | Kauri Ram | 26.5250 | 83.4150 | Chickpea, Pulses |
| **Bansgaon** | Gagaha | 26.4750 | 83.4750 | Arhar, Mustard |
| **Khajni** | Khajni Town | 26.6450 | 83.2250 | Wheat, Soybean |
| **Khajni** | Piprauli | 26.7050 | 83.2950 | Lentil, Wheat |
| **Khajni** | Belghat | 26.5350 | 83.1950 | Rice, Wheat |
| **Gola** | Gola Gokaran area | 26.4150 | 83.3450 | Sugarcane, Rice |
| **Gola** | Barhalganj | 26.2850 | 83.5050 | Rice, Wheat |

---

## 3. The 3 Methods to Build Your Dataset

### Method A: Automated Dataset Builder (Recommended & Fastest)
We have provided a ready-to-run builder script: [`data/build_gorakhpur_dataset.py`](file:///d:/My%20Projects/Python%20Projects/Modified%20Nitrogen%20GeoN-DSS/data/build_gorakhpur_dataset.py).

#### How it works:
1. Open [`data/templates/gorakhpur_farm_seeds.csv`](file:///d:/My%20Projects/Python%20Projects/Modified%20Nitrogen%20GeoN-DSS/data/templates/gorakhpur_farm_seeds.csv).
2. Add your own GPS coordinates, villages, crops, or field sizes.
3. Run the generator in your terminal:
```bash
python data/build_gorakhpur_dataset.py --samples-per-farm 25 --output data/processed/gorakhpur_custom_dataset.csv
```
This automatically computes all **64 required columns**:
- Mathematical sin/cos geospatial coordinates and elevations.
- Gorakhpur clay-loam soil properties.
- Monsoonal/Winter/Summer weather variables.
- Correlated Sentinel-2 multispectral indices (NDVI, GNDVI, NDRE) matching the crop stage.
- Risk scores (`rain_leach_score`, `burn_risk_score`).
- Ground-truth target labels (`application_window_class` and `recommended_N_kg_ha`).

---

### Method B: Collecting Real Field Ground Truth (Surveys & KVK)
If you want to interview actual farmers or collect real agricultural trial sheets in Gorakhpur:

1. **Where to get real soil data for Gorakhpur**:
   - **Soil Health Card (SHC) Portal** (`https://soilhealth.dac.gov.in`):
     - Select State: *Uttar Pradesh* ➔ District: *Gorakhpur* ➔ Tehsil / Village.
     - You will get real tested values of Soil pH (typically 7.1–7.5), Organic Carbon % (typically 0.45–0.70%), and Available Nitrogen (kg/ha).
   - **Krishi Vigyan Kendra (KVK) Gorakhpur**:
     - *Mahayogi Gorakhnath KVK* (Chaukmaf, Peppeganj, Gorakhpur).
     - *KVK Belipar* (Gorakhpur).
     - They have real trial response curves for Rice (varieties like Sambha Masuri, Sarjoo-52) and Wheat (HD-2967, PBW-502).

2. **What to ask the farmer in your survey**:
   - Location GPS coordinates (using Google Maps / GPS phone pin).
   - Crop name and current growth stage (e.g. Rice at Tillering, ~35 days after sowing).
   - What crop did they harvest in the previous season? (If pulse/legume, note it).
   - What was their actual fertilizer application? (e.g., "1 bag Urea per bigha" ≈ 45 kg per 0.25 ha).

---

### Method C: Fetching Real Historical Weather & Satellite Data via API

For any specific coordinate in Gorakhpur:

1. **Weather Data (Free Open-Meteo Historical API)**:
   You don't need any API key. Make a simple GET request:
   ```
   https://archive-api.open-meteo.com/v1/archive?latitude=26.8285&longitude=83.5230&start_date=2023-08-01&end_date=2023-08-03&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&timezone=auto
   ```
   This gives you real historical daily rainfall and temperatures for that farm.

2. **Satellite Spectral Indices (Sentinel-2 via Google Earth Engine or Copernicus)**:
   - Use Google Earth Engine (GEE) or Copernicus Browser (`https://browser.dataspace.copernicus.eu/`).
   - Draw a polygon over your Gorakhpur coordinates.
   - Select Sentinel-2 L2A (10m resolution).
   - Formulas:
     $$\text{NDVI} = \frac{B8 - B4}{B8 + B4}$$
     $$\text{GNDVI} = \frac{B8 - B3}{B8 + B3}$$
     $$\text{NDRE} = \frac{B8 - B5}{B8 + B5} \quad (\text{Band 5 is the Red-Edge band})$$

---

## 4. How to Train / Fine-tune the Models on Your Gorakhpur Dataset

Once your Gorakhpur dataset is saved to `data/processed/gorakhpur_custom_dataset.csv`, you can train or evaluate models on Gorakhpur alone:

### Step 1: Train the LightGBM Safety Classifier
```bash
python -c "
import pandas as pd
from lightgbm import LGBMClassifier
import joblib

df = pd.read_csv('data/processed/gorakhpur_custom_dataset.csv')
features = [col for col in df.columns if col not in ['record_id', 'state', 'district', 'data_source', 'date_of_record', 'season_year', 'centroid_lat', 'centroid_lon', 'recommended_N_kg_ha', 'application_window_class', 'urea_kg_ha', 'dap_kg_ha']]

for cat in ['soil_type', 'crop_type', 'crop_season', 'growth_stage', 'previous_crop', 'irrigation_type', 'fertilizer_history']:
    df[cat] = df[cat].astype('category')

X = df[features]
y = df['application_window_class']

clf = LGBMClassifier(class_weight='balanced', random_state=42)
clf.fit(X, y)
joblib.dump({'model': clf, 'feature_columns': features}, 'ml/saved_models/gorakhpur_lgbm.joblib')
print('[OK] Gorakhpur Safety Classifier trained successfully!')
"
```

### Step 2: Train the XGBoost Dosage Regressor
```bash
python -c "
import pandas as pd
from xgboost import XGBRegressor
import joblib

df = pd.read_csv('data/processed/gorakhpur_custom_dataset.csv')
features = [col for col in df.columns if col not in ['record_id', 'state', 'district', 'data_source', 'date_of_record', 'season_year', 'centroid_lat', 'centroid_lon', 'recommended_N_kg_ha', 'application_window_class', 'urea_kg_ha', 'dap_kg_ha']]

for cat in ['soil_type', 'crop_type', 'crop_season', 'growth_stage', 'previous_crop', 'irrigation_type', 'fertilizer_history']:
    df[cat] = df[cat].astype('category')

X = df[features]
y = df['recommended_N_kg_ha']

reg = XGBRegressor(enable_categorical=True, random_state=42)
reg.fit(X, y)
joblib.dump({'model': reg, 'feature_columns': features}, 'ml/saved_models/gorakhpur_xgb.joblib')
print('[OK] Gorakhpur Dosage Regressor trained successfully!')
"
```

---

## 5. Summary Checklist

- [x] **25 Farm Seeds**: Configured in `data/templates/gorakhpur_farm_seeds.csv`.
- [x] **Builder Script**: Created at `data/build_gorakhpur_dataset.py`.
- [x] **Sample Gorakhpur Dataset**: Generated at `data/processed/gorakhpur_custom_dataset.csv` (500 rows × 64 columns).
- [ ] **Custom Field Additions**: Add your own farmer GPS points or survey rows to `gorakhpur_farm_seeds.csv`.
- [ ] **Re-run Builder**: Run `python data/build_gorakhpur_dataset.py --samples-per-farm 30` to scale your dataset to 750–1,500 rows.
