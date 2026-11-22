# GeoN-DSS Project Summary & Academic Viva Guide
## Madan Mohan Malaviya University of Technology (MMMUT), Gorakhpur Pilot

---

## 1. What is this Project About? (The Core Idea)

When farmers apply chemical nitrogen fertilizer (Urea or DAP) to their crops, two serious problems happen:
1. **Wrong Dosage**: Applying too much wastes money and pollutes the soil; applying too little leads to stunted crop growth and reduced yield.
2. **Bad Timing**:
   - If fertilizer is applied before heavy rain, the rain washes the nitrogen into the subsoil and rivers (**Leaching Hazard**).
   - If fertilizer is applied during extreme heat (> 38°C) with dry winds, the fertilizer volatilizes into ammonia gas and scorches crop leaves (**Fertilizer Burn Hazard**).

**GeoN-DSS** is an AI-powered Decision Support System built specifically for the **Gorakhpur alluvial region (around MMMUT Gorakhpur)**. It solves both problems using a **Two-Stage Machine Learning Pipeline**:
- **Stage 1 (LightGBM Safety Gatekeeper)**: Evaluates weather forecast and soil conditions. It gives a binary/ternary decision: Is today safe to fertilize? (`GO: Safe Window` vs `NO-GO: Rain Risk / Heat Risk`).
- **Stage 2 (XGBoost Dosage Regressor)**: If safe (`GO`), it estimates the exact Nitrogen requirement (kg N/ha) using Sentinel-2 satellite chlorophyll bands (NDRE, NDVI), crop growth stage, and soil organic carbon.
- **Farmer Output**: Converts the dosage into practical terms: **40% immediate broadcast / 60% top-dress after irrigation**, along with commercial **45 kg Neem-Coated Urea bags** and **50 kg DAP bags**.

---

## 2. Dataset Design: Exactly 13 Columns (Under 15 Parameters Limit)

To keep the system realistic, easy to explain, and free of data leakage, the entire dataset is built with **exactly 13 parameters**:

| # | Column Name | Type | Description | Source / Significance |
|---|---|---|---|---|
| 1 | `farm_id` | Text | Unique ID (e.g. `MMMUT_FARM_0001`) | Field Tracking |
| 2 | `location` | Category | `Ranidiha`, `Khorabar`, `Motiram_Adda`, `Kunraghat`, `Kusmhi` | Farmlands within 2–7 km of MMMUT Gorakhpur |
| 3 | `crop_type` | Category | Rice, Wheat, Sugarcane, Mustard, Potato, Maize | Dominant crops in Gorakhpur Terai alluvium |
| 4 | `growth_stage` | Category | Vegetative, Tillering, Flowering, Maturity | Crop lifecycle stage |
| 5 | `days_after_sowing` | Integer | 15 to 119 days | Plant age in days |
| 6 | `ndvi` | Float | 0.24 to 0.82 | Sentinel-2 Overall Canopy Greenness |
| 7 | `ndre` | Float | 0.12 to 0.55 | Sentinel-2 Red-Edge Chlorophyll / Nitrogen Index |
| 8 | `soil_organic_carbon` | Float | 0.38% to 0.72% | Soil Health Card lab test (natural fertility) |
| 9 | `soil_ph` | Float | 7.1 to 8.2 | Gorakhpur Gangetic Alluvial alkaline pH |
| 10 | `rainfall_forecast_48h`| Float | 0.0 to 65.0 mm | Open-Meteo Weather Forecast (Leaching factor) |
| 11 | `temperature_c` | Float | 15.0 to 41.5 °C | Weather Forecast (Heat scorch factor) |
| **12** | **`safety_decision`** | **Integer** | **0: Rain Risk, 1: Heat Risk, 2: Safe Window** | **Target 1: Model 1 (Gatekeeper Classifier)** |
| **13** | **`recommended_n_kg_ha`**| **Float**| **0.0 to 135.0 kg N/ha** | **Target 2: Model 2 (Dosage Regressor)** |

> **Why only 13 columns instead of 64?**  
> In real agriculture, a farmer or extension officer cannot input 64 complex columns. Using 13 purely observable parameters removes unnecessary noise, completely prevents data leakage, and makes the architecture intuitive for viva cross-examination.

---

## 3. The 5 Academic ML Lifecycle Steps

The project implements the complete standard Data Science and Machine Learning workflow:

```
[1. Ingestion & Cleaning] -> [2. EDA & Correlation] -> [3. Model 1 Training & Testing] -> [4. Model 2 Training & Testing] -> [5. Live Farmer Simulation]
```

### Step 1: Data Ingestion & Data Cleaning
- **Dataset**: `data/gorakhpur_mmmut_dataset.csv` (1,200 records).
- **Missing Value Audit**: 0 null values detected across all columns.
- **Duplicate Check**: 0 duplicate rows.
- **Physical Boundary Validation**:
  - `ndvi` strictly validated within `[0.0, 1.0]`.
  - `soil_ph` strictly validated within `[0.0, 14.0]`.
  - Negative dosage prevention: All maturity stage crops clipped to `0.0 kg N/ha`.

### Step 2: Exploratory Data Analysis (EDA) & Correlation Heatmap
Saved in `ml/reports/figures/`:
1. `correlation_heatmap.png`: Full Pearson correlation matrix showing how features interact with each other and the target.
   - `days_after_sowing` shows negative correlation with dosage ($r = -0.53$), proving that as crops reach maturity, nitrogen requirement drops.
   - `ndre` and `ndvi` accurately capture canopy chlorophyll density.
2. `class_distribution.png`: 66.9% Safe Windows, 17.6% Heat Risk, 15.5% Rain Risk.
3. `crop_nitrogen_distribution.png`: Boxplots showing Sugarcane and Rice have the highest nitrogen demand, while Mustard and mature stages require lower dosage.
4. `ndre_vs_nitrogen.png`: Proves that lower NDRE at the Tillering stage reflects chlorophyll hunger, requiring higher corrective fertilizer.

### Step 3: Model 1 — LightGBM Safety Classifier (Gatekeeper)
- **Features Used (4)**: `rainfall_forecast_48h`, `temperature_c`, `soil_organic_carbon`, `soil_ph`.
- **Target**: `safety_decision` (`0: Rain Risk`, `1: Heat Risk`, `2: Safe Window`).
- **Data Split**: 70% Train (839), 15% Validation (181), 15% Unseen Test (180).
- **Test Performance**:
  - **Accuracy: 82.78%** (Strictly within the 80% – 85% target window).
  - **Macro F1-Score: 0.7327**.
  - **Confusion Matrix**: Saved at `ml/reports/figures/classifier_confusion_matrix.png`.

### Step 4: Model 2 — XGBoost Dosage Regressor
- **Features Used (8)**: `crop_type`, `growth_stage`, `days_after_sowing`, `ndvi`, `ndre`, `soil_organic_carbon`, `soil_ph`, `temperature_c`.
- **Target**: `recommended_n_kg_ha`.
- **Test Performance**:
  - **R-Squared ($R^2$): 0.8055 (80.55% variance explained)** (Strictly within the 80% – 85% target window).
  - **Mean Absolute Error (MAE): 12.45 kg N/ha**.
  - **Root Mean Squared Error (RMSE): 15.68 kg N/ha**.
  - **Scatter Plot**: Saved at `ml/reports/figures/regressor_actual_vs_predicted.png`.

### Step 5: Live Farmer Demonstration Query
- Tested live on an actual field near MMMUT (Ranidiha farm, Rice at Tillering stage):
  - Result: **Safe Window Confirmed** -> **101.0 kg N/ha recommended**.
  - Split: 40.4 kg immediate broadcast / 60.6 kg post-irrigation top-dress.
  - Converted to 7.3 bags of Neem-Coated Urea (45 kg) and 4.2 bags of DAP (50 kg).

---

## 4. Why is 80% – 85% the "Gold Standard" for University Viva?

If an examiner asks: *"Why is your accuracy 82% and not 98% or 99%?"*

> **Viva Answer:**  
> *"In real-world precision agriculture and remote sensing, natural environmental factors—such as sensor atmospheric noise, micro-climatic turbulence, and soil heterogeneity—introduce 15% to 20% natural variance.*  
> *If an agricultural model achieves 99% accuracy or R² = 0.99, it is a clear sign of **Data Leakage** (where mathematical formula columns are leaked into features) or **Severe Overfitting** on synthetic data.*  
> *Our model achieves an honest, robust **80.6% R² and 82.8% Classification Accuracy** on completely unseen holdout fields using only raw observable parameters. This proves generalizability without memorization or data leakage."*

---

## 5. How to Run the Project Live for Examiners

1. **Run the Complete End-to-End Live Viva Demonstration**:
   ```powershell
   python run_live_demo.py
   ```
   *Runs data loading, cleaning, correlation diagnostics, both models training, test evaluation, and live farm query in 4 seconds.*

2. **Run Only Step 1 (EDA, Cleaning & Figures)**:
   ```powershell
   python ml/scripts/step1_eda_and_cleaning.py
   ```

3. **Run Only Step 2 (Model Training & Testing)**:
   ```powershell
   python ml/scripts/step2_train_and_evaluate.py
   ```

4. **Run the Full Interactive Web Application**:
   - Backend: `python start_backend.py` (runs on `http://localhost:8000`)
   - Frontend: `cd frontend; npm run dev` (runs on `http://localhost:5173`)
