# 📊 GeoN-DSS — Dataset Schema (UP-Scoped)
## Uttar Pradesh | 4 Districts | Final Year Project Demonstration

> **Scope:** Uttar Pradesh (UP) only — 4 districts: Amethi, Gorakhpur, Lucknow, Kanpur
> **Goal:** ~10,000–15,000 synthetic records (sufficient for FYP demonstration)
> **Total Columns:** 60

---

## 🗺️ District Fingerprints

| District | Lat Range | Lon Range | Agro-Climatic Zone | Dominant Soil | Primary Season |
|---|---|---|---|---|---|
| **Lucknow** | 26.70°–27.00°N | 80.75°–81.15°E | Upper Gangetic Plains | Light Alluvial (Sandy Loam) | Rabi-dominant |
| **Kanpur** | 26.25°–26.65°N | 80.10°–80.55°E | Upper Gangetic Plains | Medium Alluvial (Loam) | Rabi-dominant |
| **Amethi** | 25.90°–26.40°N | 81.55°–82.10°E | Upper Gangetic Plains | Mixed Alluvial | Kharif + Rabi |
| **Gorakhpur** | 26.55°–26.95°N | 83.10°–83.65°E | Middle Gangetic Plains | Heavy Alluvial (Clay Loam) | Kharif-dominant |

> **Key insight:** All 4 districts lie in the **Indo-Gangetic Plain** — soil is predominantly alluvial with variation
> in texture (sand/clay ratio) moving from west (Kanpur → sandier) to east (Gorakhpur → clayey).

---

## Group 0 — 🔑 Record Identifiers (Not Model Features)

| Column | Type | Locked Value / ENUM | Notes |
|---|---|---|---|
| `record_id` | str (UUID) | Auto-generated | Unique row ID |
| `state` | str | `Uttar Pradesh` (constant) | Locked — no variation |
| `district` | str (ENUM) | `LUCKNOW`, `KANPUR`, `AMETHI`, `GORAKHPUR` | 4 values only |
| `data_source` | str (ENUM) | `SYNTHETIC`, `FIELD_TRIAL` | Provenance tag |
| `date_of_record` | date | `YYYY-MM-DD` | Simulated across 2020–2024 |
| `season_year` | str | e.g., `KHARIF_2022`, `RABI_2023` | Temporal grouping |

---

## Group 1 — 📍 Geospatial Features (UP-Bounded)

| Column | Type | Unit | UP Range | Notes |
|---|---|---|---|---|
| `centroid_lat` | float | °N | 25.90 – 27.00 | Raw — stored but not fed to model |
| `centroid_lon` | float | °E | 80.10 – 83.65 | Raw — stored but not fed to model |
| `lat_sin` | float | — | computed | `sin(lat × π/180)` → model input |
| `lat_cos` | float | — | computed | `cos(lat × π/180)` → model input |
| `lon_sin` | float | — | computed | `sin(lon × π/180)` → model input |
| `lon_cos` | float | — | computed | `cos(lon × π/180)` → model input |
| `elevation_m` | float | m | 70 – 130 | Flat IGP terrain; low variance |
| `slope_deg` | float | ° | 0 – 3 | Nearly flat plains |
| `field_area_ha` | float | ha | 0.5 – 20 | Typical smallholder UP field size |

> `aspect_deg` removed — negligible variance on flat IGP terrain.

---

## Group 2 — 🛰️ Spectral Indices (Sentinel-2 via GEE)

| Column | Type | Unit | Realistic Range (crop pixels) | Sentinel-2 Formula |
|---|---|---|---|---|
| `ndvi` | float | — | 0.20 – 0.90 | (B8 − B4) / (B8 + B4) |
| `gndvi` | float | — | 0.25 – 0.80 | (B8 − B3) / (B8 + B3) |
| `ndre` | float | — | 0.10 – 0.60 | (B8 − B5) / (B8 + B5) |
| `evi` | float | — | 0.10 – 0.80 | 2.5×(B8−B4)/(B8+6B4−7.5B2+1) |
| `lai` | float | m²/m² | 0.5 – 6.0 | Derived from NDVI |
| `cloud_coverage_pct` | float | % | 0 – 100 | GEE SCL cloud mask |
| `ndvi_15d_trend` | float | Δ index | −0.30 – +0.30 | NDVI(t) − NDVI(t−15d) |
| `gndvi_15d_trend` | float | Δ index | −0.25 – +0.25 | GNDVI(t) − GNDVI(t−15d) |
| `ndre_15d_trend` | float | Δ index | −0.20 – +0.20 | NDRE(t) − NDRE(t−15d) |

> **NDRE** is the most direct nitrogen-status index and will carry highest SHAP weight in the regressor.
> Negative 15-day trends signal crop N depletion — strong predictor for higher dosage recommendation.

---

## Group 3 — 🌦️ Meteorological Parameters (UP Climate Profile)

| Column | Type | Unit | UP Realistic Range | Season Notes |
|---|---|---|---|---|
| `temp_max_c` | float | °C | 8 – 45 | Kharif: 30–45°C; Rabi: 8–28°C |
| `temp_min_c` | float | °C | 2 – 32 | Winter (Rabi): can drop to 2–4°C |
| `temp_avg_c` | float | °C | 5 – 38 | — |
| `rainfall_24h_mm` | float | mm | 0 – 150 | Monsoon peaks in Gorakhpur (heavier) |
| `rainfall_48h_mm` | float | mm | 0 – 250 | — |
| `rainfall_forecast_48h_mm` | float | mm | 0 – 200 | Open-Meteo ERA5 forecast |
| `humidity_pct` | float | % | 25 – 98 | Very high in Gorakhpur monsoon (85–98%) |
| `wind_speed_ms` | float | m/s | 0 – 12 | UP: generally calm; peak in May–June |
| `solar_radiation_wm2` | float | W/m² | 100 – 900 | Low in fog season (Dec–Jan) |
| `et0_mm` | float | mm/day | 1.0 – 9.0 | High in summer Zaid season |
| `weather_state` | int (ENUM) | 0–5 | — | See table below |

### Weather State ENUM
| Code | Label | UP Occurrence | Application Rule |
|---|---|---|---|
| 0 | `SUNNY` | Common in Rabi / Zaid | ✅ GO |
| 1 | `PARTLY_CLOUDY` | Transition seasons | ✅ GO |
| 2 | `OVERCAST` | Pre-monsoon / winter | ✅ GO (caution) |
| 3 | `RAINFALL` | Kharif monsoon | ❌ NO-GO (leaching) |
| 4 | `THUNDERSTORM` | Pre-monsoon May–June | ❌ NO-GO (leaching + safety) |
| 5 | `FOGGY` | Rabi Dec–Jan | ❌ NO-GO (foliar block) |

---

## Group 4 — 🌍 Soil Properties (UP / SoilGrids Profile)

| Column | Type | Unit | UP Realistic Range | District Variation |
|---|---|---|---|---|
| `soil_ph` | float | pH | 7.0 – 8.5 | UP soils are calcareous-alkaline |
| `soil_organic_carbon_gkg` | float | g/kg | 2.0 – 8.0 | Low SOC — UP soils are N-deficient |
| `cec_cmolkg` | float | cmol/kg | 8 – 25 | Higher in Gorakhpur (clay) |
| `clay_pct` | float | % | 15 – 55 | Kanpur: ~15–25%; Gorakhpur: ~40–55% |
| `sand_pct` | float | % | 20 – 65 | Kanpur: ~50–65%; Gorakhpur: ~20–30% |
| `silt_pct` | float | % | computed | `100 − clay_pct − sand_pct` |
| `bulk_density_kgdm3` | float | kg/dm³ | 1.35 – 1.65 | Typical alluvial plains range |
| `nitrogen_soil_gkg` | float | g/kg | 0.2 – 1.2 | Very low — reinforces external N need |
| `soil_type` | str (ENUM) | — | See below | Alluvial variants only |

### Soil Type ENUM — UP Only (Simplified)
| Code | Label | Districts |
|---|---|---|
| `LIGHT_ALLUVIAL` | Sandy Loam (Bhangar) | Kanpur, western Lucknow |
| `MEDIUM_ALLUVIAL` | Loam (Khadar) | Lucknow, Amethi |
| `HEAVY_ALLUVIAL` | Clay Loam (Tarai) | Gorakhpur, eastern Amethi |

> Removed all non-alluvial soil types (Black Cotton, Red Laterite, etc.) — irrelevant to UP.

---

## Group 5 — 🌾 Agronomic Parameters (UP-Specific Crops)

| Column | Type | ENUM / Unit | Notes |
|---|---|---|---|
| `crop_type` | str (ENUM) | See crop list below | UP-relevant crops only |
| `crop_season` | str (ENUM) | `KHARIF`, `RABI`, `ZAID` | Season drives crop list filtering |
| `growth_stage` | str (ENUM) | See stage list | N demand peaks at specific stages |
| `days_after_sowing` | int | days | 0 – 180 (crop-dependent) |
| `previous_crop` | str (ENUM) | Same crop list + `FALLOW`, `LEGUME_GENERIC` | Legume N credit: 20–35 kg/ha |
| `irrigation_type` | str (ENUM) | `FLOOD`, `SPRINKLER`, `DRIP`, `RAINFED` | UP: flood irrigation dominates |
| `target_yield_tha` | float | t/ha | Crop-specific realistic ranges |
| `fertilizer_history` | str (ENUM) | `NONE`, `LOW`, `MEDIUM`, `HIGH` | Past season input intensity |
| `gdd_accumulated` | float | °C·days | Growing Degree Days since sowing |

### UP Crop List by Season

#### 🟩 Kharif (June – November)
| Crop | Districts | Yield Target (t/ha) | Key N Sensitivity |
|---|---|---|---|
| RICE | Gorakhpur, Amethi, Lucknow | 3.0 – 6.5 | High (tillering stage) |
| SUGARCANE | Gorakhpur, Lucknow, Amethi | 60 – 90 | Very High (vegetative) |
| MAIZE | Kanpur, Amethi | 3.0 – 6.0 | High (vegetative/tasseling) |
| ARHAR (Pigeon Pea) | Amethi, Gorakhpur | 1.0 – 2.5 | Low (N-fixing legume) |
| BAJRA | Kanpur | 1.5 – 3.0 | Medium |
| SOYBEAN | Lucknow, Kanpur | 1.5 – 2.5 | Low (N-fixing) |

#### 🟦 Rabi (October – March)
| Crop | Districts | Yield Target (t/ha) | Key N Sensitivity |
|---|---|---|---|
| WHEAT | All 4 districts | 3.5 – 6.0 | Very High (tillering/booting) |
| MUSTARD | Kanpur, Lucknow | 1.0 – 2.0 | Medium-High (flowering) |
| POTATO | Agra-adjacent / Kanpur | 15 – 30 | High (vegetative) |
| CHICKPEA | Kanpur, Amethi | 0.8 – 1.5 | Low (N-fixing) |
| LENTIL (Masoor) | Amethi, Gorakhpur | 0.8 – 1.2 | Low (N-fixing) |
| ONION | Lucknow, Kanpur | 15 – 25 | High (bulbing stage) |

#### 🟡 Zaid (March – June)
| Crop | Districts | Yield Target (t/ha) | Key N Sensitivity |
|---|---|---|---|
| MOONG | Kanpur, Lucknow | 0.8 – 1.5 | Low (N-fixing) |
| WATERMELON | All 4 (limited) | 20 – 35 | Medium |
| FODDER_MAIZE | Gorakhpur | 30 – 50 | High |

**Total: 17 crops** (10 Kharif + 7 Rabi + 3 Zaid) × 4 districts

### Growth Stage ENUM
| Stage | Typical DAS | Applicable Crops |
|---|---|---|
| `GERMINATION` | 0 – 10 | All |
| `VEGETATIVE` | 10 – 40 | All |
| `TILLERING` | 25 – 55 | Wheat, Rice, Maize, Bajra |
| `BOOTING` | 45 – 70 | Wheat, Rice |
| `FLOWERING` | 50 – 90 | All |
| `GRAIN_FILL` | 70 – 110 | Cereals / `FRUIT_SET` for others |
| `MATURITY` | 100 – 180 | All |

---

## Group 6 — ⚙️ Engineered / Derived Features

| Column | Formula | Purpose |
|---|---|---|
| `ndvi_ndre_ratio` | `ndvi / (ndre + 0.001)` | N-stress amplifier |
| `rain_leach_score` | `(0.4×rain_24h + 0.6×forecast_48h) / (clay_pct + 1)` | Composite leaching risk (0–10) |
| `burn_risk_score` | `(temp_max_c × wind_speed_ms) / (humidity_pct + 1)` | Composite burn risk (0–10) |
| `n_removal_estimate` | `target_yield_tha × crop_n_coeff` | N removed by crop (kg/ha) |
| `soil_n_supply` | `nitrogen_soil_gkg × bulk_density_kgdm3 × 300` | Available soil N in top 30cm (kg/ha) |
| `base_n_demand` | Lookup: `crop_type × growth_stage` | ICAR baseline demand (kg/ha) |
| `previous_crop_n_credit` | Lookup: `previous_crop → N credit` | Credit for legume predecessor |

---

## Group 7 — 🎯 Target Variables (Labels)

| Column | Type | Range | Description |
|---|---|---|---|
| `recommended_N_kg_ha` | float | 0 – 150 | Optimal N dosage for this observation |
| `application_window_class` | int | 0, 1, 2 | Safety classification (see below) |
| `urea_kg_ha` | float | computed | `recommended_N_kg_ha / 0.46` (Urea is 46% N) |
| `dap_kg_ha` | float | computed | DAP supplies 18% N (secondary supplement) |

### Application Window Classes
```
Class 0 → NO-GO: Leaching Risk
    Triggered when: rain_leach_score > 4.0
                 OR weather_state IN [3, 4]
                 OR rainfall_forecast_48h_mm > 20

Class 1 → NO-GO: Burn Risk
    Triggered when: burn_risk_score > 5.0
                 OR weather_state IN [4, 5]
                 OR (temp_max_c > 40 AND humidity_pct < 35)

Class 2 → GO: Safe Application Window
    All risk checks pass — dosage recommendation unlocked
```

---

## Complete Column Index

| # | Column | Group | Model Input? |
|---|---|---|---|
| 1 | record_id | ID | ❌ |
| 2 | state | ID | ❌ (constant = UP) |
| 3 | district | ID | ✅ (one-hot) |
| 4 | data_source | ID | ❌ |
| 5 | date_of_record | ID | ❌ |
| 6 | season_year | ID | ❌ |
| 7 | centroid_lat | Geo | ❌ (raw) |
| 8 | centroid_lon | Geo | ❌ (raw) |
| 9 | lat_sin | Geo | ✅ |
| 10 | lat_cos | Geo | ✅ |
| 11 | lon_sin | Geo | ✅ |
| 12 | lon_cos | Geo | ✅ |
| 13 | elevation_m | Geo | ✅ |
| 14 | slope_deg | Geo | ✅ |
| 15 | field_area_ha | Geo | ✅ |
| 16 | ndvi | Spectral | ✅ |
| 17 | gndvi | Spectral | ✅ |
| 18 | ndre | Spectral | ✅ |
| 19 | evi | Spectral | ✅ |
| 20 | lai | Spectral | ✅ |
| 21 | cloud_coverage_pct | Spectral | ✅ |
| 22 | ndvi_15d_trend | Spectral | ✅ |
| 23 | gndvi_15d_trend | Spectral | ✅ |
| 24 | ndre_15d_trend | Spectral | ✅ |
| 25 | temp_max_c | Meteo | ✅ |
| 26 | temp_min_c | Meteo | ✅ |
| 27 | temp_avg_c | Meteo | ✅ |
| 28 | rainfall_24h_mm | Meteo | ✅ |
| 29 | rainfall_48h_mm | Meteo | ✅ |
| 30 | rainfall_forecast_48h_mm | Meteo | ✅ |
| 31 | humidity_pct | Meteo | ✅ |
| 32 | wind_speed_ms | Meteo | ✅ |
| 33 | solar_radiation_wm2 | Meteo | ✅ |
| 34 | et0_mm | Meteo | ✅ |
| 35 | weather_state | Meteo | ✅ |
| 36 | soil_ph | Soil | ✅ |
| 37 | soil_organic_carbon_gkg | Soil | ✅ |
| 38 | cec_cmolkg | Soil | ✅ |
| 39 | clay_pct | Soil | ✅ |
| 40 | sand_pct | Soil | ✅ |
| 41 | silt_pct | Soil | ✅ |
| 42 | bulk_density_kgdm3 | Soil | ✅ |
| 43 | nitrogen_soil_gkg | Soil | ✅ |
| 44 | soil_type | Soil | ✅ (encoded) |
| 45 | crop_type | Agro | ✅ (encoded) |
| 46 | crop_season | Agro | ✅ (encoded) |
| 47 | growth_stage | Agro | ✅ (encoded) |
| 48 | days_after_sowing | Agro | ✅ |
| 49 | previous_crop | Agro | ✅ (encoded) |
| 50 | irrigation_type | Agro | ✅ (encoded) |
| 51 | target_yield_tha | Agro | ✅ |
| 52 | fertilizer_history | Agro | ✅ (encoded) |
| 53 | gdd_accumulated | Agro | ✅ |
| 54 | ndvi_ndre_ratio | Engineered | ✅ |
| 55 | rain_leach_score | Engineered | ✅ |
| 56 | burn_risk_score | Engineered | ✅ |
| 57 | n_removal_estimate | Engineered | ✅ |
| 58 | soil_n_supply | Engineered | ✅ |
| 59 | base_n_demand | Engineered | ✅ |
| 60 | previous_crop_n_credit | Engineered | ✅ |
| 61 | recommended_N_kg_ha | **TARGET** | 🎯 Regressor |
| 62 | application_window_class | **TARGET** | 🎯 Classifier |
| 63 | urea_kg_ha | Output | ❌ post-model |
| 64 | dap_kg_ha | Output | ❌ post-model |

**Total: 64 columns — 51 model features + 2 targets + 6 identifiers + 5 raw/outputs**

---

## Dataset Size Estimate

| Combination | Count |
|---|---|
| Districts | 4 |
| Crops per district (avg) | ~10 |
| Growth stages per crop | 5–7 |
| Weather state variants | 6 |
| Soil type variants | 3 |
| Season year range | 2020–2024 (5 years) |
| Records per combo | ~5 (randomized) |
| **Estimated Total** | **~12,000–15,000 rows** |

✅ Sufficient for FYP demonstration, train/val/test split, and SHAP explainability showcase.

---

## ICAR Baseline N Demand (kg N/ha) — UP Crops

| Crop | Germination | Vegetative | Tillering | Booting | Flowering | Grain Fill | Maturity |
|---|---|---|---|---|---|---|---|
| **Wheat** | 20 | 50 | 70 | 80 | 25 | 5 | 0 |
| **Rice** | 10 | 30 | 55 | 65 | 25 | 10 | 0 |
| **Sugarcane** | 25 | 70 | — | — | 80 | 55 | 15 |
| **Maize** | 20 | 55 | 75 | 85 | 35 | 15 | 0 |
| **Potato** | 15 | 60 | — | — | 55 | 25 | 0 |
| **Mustard** | 10 | 35 | — | — | 45 | 20 | 0 |
| **Onion** | 5 | 30 | — | — | 40 | 20 | 0 |
| **Bajra** | 15 | 40 | 55 | — | 25 | 10 | 0 |
| **Arhar** | 0 | 5 | — | — | 10 | 5 | 0 |
| **Soybean** | 0 | 5 | — | — | 10 | 5 | 0 |
| **Chickpea** | 0 | 5 | — | — | 10 | 5 | 0 |
| **Lentil** | 0 | 5 | — | — | 8 | 5 | 0 |
| **Moong** | 0 | 5 | — | — | 8 | 5 | 0 |
| **Watermelon** | 5 | 20 | — | — | 25 | 15 | 0 |
| **Fodder Maize** | 15 | 50 | 60 | — | 30 | 10 | 0 |

> Source: ICAR Fertiliser Use Recommendations for UP region. Values = cumulative stage application guidance.
> Legume crops (Arhar, Soybean, Chickpea, Lentil, Moong) have very low N demand — they fix atmospheric N.

---

## Previous Crop N Credit Table

| Previous Crop | N Credit (kg/ha) | Reason |
|---|---|---|
| ARHAR | 35 | Deep-rooted legume, high N fixation |
| SOYBEAN | 30 | Efficient N-fixer |
| CHICKPEA | 25 | Moderate N-fixer |
| LENTIL | 20 | Moderate N-fixer |
| MOONG | 20 | Short-season legume |
| LEGUME_GENERIC | 25 | Default for unspecified legumes |
| FALLOW | 10 | Some mineralization from organic matter |
| Non-legume crops | 0 | No N credit |

---

## Next Steps

- [x] ✅ Feature set locked
- [x] ✅ Scope: UP only (Amethi, Gorakhpur, Lucknow, Kanpur)
- [x] ✅ Dataset schema finalized (64 columns)
- [ ] 🔜 **Step 3:** Build the synthetic dataset generator (`data/generate_dataset.py`)
- [ ] **Step 4:** Setup project folder structure (backend / frontend / ml / data)
- [ ] **Step 5:** Train LightGBM + XGBoost baseline models
- [ ] **Step 6:** FastAPI backend with GEE + Open-Meteo + SoilGrids
- [ ] **Step 7:** React frontend with polygon draw + dashboard

---

*Document version: v2.0 — UP-scoped, 4 districts, FYP demonstration scale*
*Conversation ID: 1474d961-4a19-40c4-b93f-42bfdef41993*
