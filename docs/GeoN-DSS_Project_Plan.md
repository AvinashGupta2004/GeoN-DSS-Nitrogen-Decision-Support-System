# 🌱 GeoN-DSS — Nitrogen Decision Support System
## Project Planning Document

---

## 1. System Overview

The **GeoN-DSS** (Geospatial Nitrogen Decision Support System) is a machine-learning-powered agronomic tool that:
- Accepts a **field polygon** (GeoJSON), **crop type**, and **growth stage** from the user
- Fetches **spectral indices** (NDVI, GNDVI, NDRE) from Sentinel-2 via Google Earth Engine (GEE)
- Fetches **meteorological data** (rainfall, temperature, humidity, weather state) from Open-Meteo/ERA5
- Fetches **soil properties** from SoilGrids (ISRIC)
- Runs a **dual-model pipeline**: a safety classifier (LightGBM) + a dosage regressor (XGBoost)
- Outputs a **gated nitrogen recommendation** in kg/ha, converted to Urea and DAP bulk amounts, with a split schedule

---

## 2. Core Dataset Parameters (Feature Set)

### 2.1 🛰️ Spectral Indices (from GEE Sentinel-2)
| Feature | Description | Expected Range | Why It Matters |
|---|---|---|---|
| `ndvi` | Normalized Difference Vegetation Index | −1 to +1 (crop: 0.3–0.9) | Proxy for overall plant biomass and green cover |
| `gndvi` | Green NDVI — (NIR−Green)/(NIR+Green) | −1 to +1 | More sensitive to chlorophyll *concentration* than NDVI |
| `ndre` | Normalized Difference Red-Edge — (NIR−RedEdge)/(NIR+RedEdge) | −1 to +1 | Most direct proxy for canopy nitrogen status |
| `evi` | Enhanced Vegetation Index | −1 to +1 | Reduces atmospheric and soil background noise |
| `lai` | Leaf Area Index (derived) | 0–8 | Biomass; useful for fertilizer uptake capacity |
| `cloud_coverage_pct` | % cloudy pixels in polygon at time of image | 0–100 | Data quality flag; affects index reliability |

> **Why all three NDVI/GNDVI/NDRE?** NDVI reflects canopy structure, GNDVI tracks chlorophyll amount, NDRE is the most N-sensitive index because it uses the red-edge band (B5 in Sentinel-2) where nitrogen absorption is most apparent.

---

### 2.2 🌦️ Meteorological Parameters (from Open-Meteo / ERA5)
| Feature | Description | Unit | Notes |
|---|---|---|---|
| `temperature_max` | Daily maximum air temperature | °C | High temp → faster N uptake, but also volatilization risk |
| `temperature_min` | Daily minimum air temperature | °C | Frost risk; affects root activity |
| `temperature_avg` | Mean daily temperature | °C | Primary thermal parameter |
| `rainfall_24h` | Total rainfall in last 24 hours | mm | Leaching risk trigger |
| `rainfall_48h` | Total rainfall in last 48 hours | mm | Accumulated leaching exposure |
| `rainfall_forecast_48h` | Forecasted rainfall in next 48 hours | mm | Pre-application window safety |
| `humidity` | Relative humidity | % | Affects foliar absorption and fungal risk |
| `wind_speed` | Wind speed at 2m | m/s | Spray drift / volatilization |
| `solar_radiation` | Global horizontal irradiance | W/m² | Drives photosynthesis and N demand |
| `weather_state` | Categorical weather condition | ENUM | See below |
| `et0` | Reference evapotranspiration | mm/day | Water stress indicator — affects N uptake efficiency |

#### Weather State ENUM
```
0 = SUNNY
1 = PARTLY_CLOUDY
2 = OVERCAST
3 = RAINFALL
4 = THUNDERSTORM
5 = FOGGY
```
> **Note:** `weather_state` is a derived categorical. It feeds both the classifier and adds an important safety interlock — fertilizer application during RAINFALL or THUNDERSTORM should always trigger NO-GO.

---

### 2.3 🌍 Soil Properties (from SoilGrids — ISRIC)
| Feature | Description | Unit | Notes |
|---|---|---|---|
| `soil_ph` | Soil pH at 0–30 cm | pH units | N availability drops below pH 5.5 and above pH 8.0 |
| `soil_organic_carbon` | SOC at 0–30 cm | g/kg | Pre-existing N in soil; high SOC reduces external N need |
| `cec` | Cation Exchange Capacity | cmol/kg | Determines soil's ability to retain N |
| `clay_content` | % clay at 0–30 cm | % | High clay → more N retention, less leaching |
| `sand_content` | % sand at 0–30 cm | % | High sand → high leaching risk |
| `bulk_density` | Bulk density at 0–30 cm | kg/dm³ | Affects root penetration and N mobility |
| `nitrogen_soil` | Total nitrogen content of soil | g/kg | Baseline available N — directly reduces requirement |

---

### 2.4 🌾 Agronomic Parameters (User Provided via Frontend)
| Feature | Description | Type | Notes |
|---|---|---|---|
| `crop_type` | Crop being cultivated | ENUM/String | Drives base N demand curve |
| `growth_stage` | Current phenological stage | ENUM | N demand peaks at specific stages |
| `field_area_ha` | Total field area | float (ha) | Scales dosage from kg/ha → total kg |
| `previous_crop` | Crop in last season | ENUM | Legumes fix N — reduces requirement |
| `irrigation_type` | Drip, Sprinkler, Flood, Rainfed | ENUM | Affects N timing and dosage |
| `target_yield` | Farmer's yield target | kg/ha or ton/ha | Higher yield target → higher N demand |

#### Crop Type ENUM — India Specific
```
Kharif:  RICE, MAIZE, COTTON, SOYBEAN, GROUNDNUT, SUGARCANE, JOWAR, BAJRA, TURMERIC
Rabi:    WHEAT, MUSTARD, CHICKPEA, POTATO, ONION, BARLEY, SUNFLOWER, LENTIL
Zaid:    MOONG, WATERMELON, CUCUMBER, FODDER_MAIZE
```

#### Crop Season ENUM
```
KHARIF   (June – November,  SW Monsoon)
RABI     (October – March,  Winter / NE Monsoon)
ZAID     (March – June,     Summer / Pre-Kharif)
```

#### Growth Stage ENUM
```
GERMINATION, VEGETATIVE, TILLERING (cereal), BOOTING (cereal),
FLOWERING, GRAIN_FILL / FRUIT_SET, MATURITY
```

---

### 2.5 📍 Geospatial Context Features
| Feature | Description | Notes |
|---|---|---|
| `latitude` | Centroid latitude of field | Encodes climate zone |
| `longitude` | Centroid longitude of field | Encodes region-specific behavior |
| `elevation` | DEM elevation (SRTM/NASADEM) | Affects temperature lapse and rainfall patterns |
| `slope` | Terrain slope (degrees) | High slope → higher runoff, lower N retention |
| `aspect` | Terrain aspect | Solar exposure proxy |

> **Encoding latitude/longitude:** Do NOT feed raw lat/lon directly into the model. Use cyclic encoding with sin/cos transforms, or derive climate-zone embeddings. Direct lat/lon creates spurious spatial correlations.

---

### 2.6 🎯 Target Variable (Labels)
| Target | Description | Unit | Model |
|---|---|---|---|
| `recommended_N_kg_ha` | Optimal nitrogen dosage | kg N / ha | **XGBoost Regressor** |
| `application_window_class` | Safety class for application | 0/1/2 | **LightGBM Classifier** |

#### Window Classes
```
Class 0 → NO-GO: Leaching Risk  (rainfall_24h + forecast_48h triggers)
Class 1 → NO-GO: Burn Risk      (high temp, low humidity, wind speed > threshold)
Class 2 → GO: Safe Window       (proceed with dosage recommendation)
```

---

## 3. Data Processing Pipeline

### Stage 1 — Data Collection & Integration
```
[GEE Sentinel-2]       → Spectral indices (NDVI, GNDVI, NDRE, EVI, LAI)
[Open-Meteo / ERA5]    → Weather (current + 48h forecast)
[SoilGrids ISRIC]      → Soil texture and chemistry
[Frontend]             → Crop type, growth stage, field boundary, target yield
[SRTM/NASADEM]         → Elevation, slope, aspect
```

### Stage 2 — Spatial Aggregation (FastAPI Engine)
- The **GeoJSON polygon** is used to spatially clip GEE rasters
- Compute **mean, std, and min** of spectral index values across all valid (non-cloud) pixels
- If `cloud_coverage_pct > 30%` → flag for data quality warning, optionally fall back to 15-day composites

### Stage 3 — Feature Engineering
| Derived Feature | Formula / Logic |
|---|---|
| `ndvi_ndre_ratio` | NDVI / (NDRE + ε) — N stress amplifier |
| `gndvi_trend` | Δ GNDVI over 15 days — temporal N depletion indicator |
| `rain_leach_score` | Weighted sum: `0.4×rainfall_24h + 0.6×forecast_48h / clay_content` |
| `burn_risk_score` | `temperature_max × wind_speed / humidity` normalized |
| `gdd` | Growing Degree Days since sowing — phenology tracker |
| `n_soil_balance` | `nitrogen_soil × depth_factor − historical_uptake` |
| `crop_growth_N_demand` | Lookup table: `crop_type × growth_stage → base_N_demand` |

### Stage 4 — Model Inference

```
Feature Vector (all above) 
        │
        ├──→ [LightGBM Classifier] → Class 0 / 1 / 2
        │             │
        │        GATEKEEPER
        │             │
        │    ┌────────┴────────┐
        │  NO-GO             GO (Class 2)
        │  (alert)            │
        │                     ↓
        └──→ [XGBoost Regressor] → recommended_N_kg_ha
                                        │
                                        ↓
                              N → Urea (÷0.46) & DAP conversion
                              Split: 40% immediate, 60% post-irrigation
```

### Stage 5 — Output Formatting
- **If GO:** Return `{ urea_kg, dap_kg, immediate_dose, post_irrigation_dose, confidence_interval }`
- **If NO-GO:** Return `{ alert_type, reason, estimated_safe_window_hours }`

---

## 4. Dataset Generation Strategy

> **Challenge:** There is no ready-made labeled dataset for "recommended nitrogen by field condition." We need to synthesize or curate it.

### Option A — Physics-Informed Synthetic Data (Recommended to Start)
1. Define **agronomic N demand curves** per crop/growth stage (from IPNI, FAO guidelines)
2. Apply **adjustment factors**: soil N balance, spectral N-stress signal (NDRE-based), weather corrections
3. Add **Gaussian noise** (±5%) to simulate real variability
4. Label `application_window_class` using **rule-based thresholds** (known agronomy rules)

### Option B — Historical Data Fusion
- Source field trial data from ICAR (India), USDA datasets, or regional Krishi Vigyan Kendras
- Join with GEE-pulled historical Sentinel-2 index time series
- Join with ERA5 historical weather reanalysis

### Option C — Expert-Calibrated Hybrid
- Start with Option A (synthetic) for baseline model training
- Continuously calibrate against Option B as real data flows in from deployed system

---

## 5. Model Selection Rationale

| Model | Role | Why This Choice |
|---|---|---|
| **LightGBM** | Safety Classifier | Fast inference, handles class imbalance well (Class 0/1 are rare), supports SHAP explainability, low memory footprint |
| **XGBoost** | N Dosage Regressor | Robust to outliers, handles mixed feature types, excellent with tabular agronomic data, well-validated in literature |

### Alternative / Ensemble Options to Consider
- **CatBoost** — if crop_type, growth_stage, weather_state categoricals dominate
- **Random Forest** — baseline comparison
- **Gaussian Process Regression** — for uncertainty quantification on dosage (confidence intervals)

---

## 6. Explainability & Trust Layer

Farmers and agronomists **must understand why** a recommendation is made.

- **SHAP values** on XGBoost output → "NDRE is low and soil N is depleted, hence 45 kg/ha recommended"
- **LightGBM feature importance** → highlight leaching or burn risk drivers
- **Dashboard cards** per risk factor with traffic-light colors (Red/Amber/Green)

---

## 7. Technology Stack (Planned)

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI (Python) |
| **ML Models** | XGBoost, LightGBM, scikit-learn |
| **Spatial / Satellite** | Google Earth Engine Python API (`geemap`, `ee`) |
| **Weather API** | Open-Meteo (free, ERA5-backed) |
| **Soil API** | SoilGrids REST API (ISRIC) |
| **Data Processing** | pandas, geopandas, numpy |
| **Feature Engineering** | scikit-learn Pipelines + custom transformers |
| **Frontend** | React / Next.js (or Streamlit for MVP) |
| **Visualization** | Leaflet.js / Folium for map, Chart.js for timeseries |
| **Database** | PostgreSQL + PostGIS (field logs), Redis (cache) |
| **Deployment** | Docker → Cloud Run / Railway |

---

## 8. Immediate Next Steps

- [ ] **Step 1:** Finalize and freeze the complete feature list (this document)
- [ ] **Step 2:** Build the synthetic dataset generator (Python script)
- [ ] **Step 3:** Implement the rule-based N demand lookup table (crop × stage)
- [ ] **Step 4:** Build the feature engineering pipeline (scikit-learn Pipeline)
- [ ] **Step 5:** Train and validate LightGBM classifier + XGBoost regressor
- [ ] **Step 6:** Build FastAPI backend with GEE + Open-Meteo + SoilGrids integrations
- [ ] **Step 7:** Build frontend with field polygon draw tool and dashboard output

---

## 9. Clarifications & Decisions (v1.1)

| # | Question | Decision |
|---|---|---|
| 1 | **Geography** | India-specific crops only; include crop season (Kharif / Rabi / Zaid) as a feature |
| 2 | **Frontend** | React (production-grade), fully decoupled from FastAPI backend via REST API |
| 3 | **Field input** | User draws a GeoJSON polygon on a Leaflet map — centroid derived server-side |
| 4 | **Dataset** | We will BUILD the dataset ourselves — synthetic + field-calibrated; schema defined in Section 10 |

---

## 10. India-Specific Dataset Schema

See `GeoN-DSS_Dataset_Schema.md` for the complete column-by-column specification.

---

*Document version: v1.1 — Scope locked, India-specific, dataset build phase*
*Conversation ID: 1474d961-4a19-40c4-b93f-42bfdef41993*
