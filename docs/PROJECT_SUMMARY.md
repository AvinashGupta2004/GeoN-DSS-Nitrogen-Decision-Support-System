# GeoN-DSS Project Summary & Workflow Guide
## Simple English Guide for Project Presentation, Review & Viva

---

## 1. What is this Project About? (The Core Idea)

When farmers apply chemical nitrogen fertilizer (like Urea or DAP) to their fields, two big problems happen:
1. **Wrong Dosage**: Applying too much wastes money and damages soil; applying too little reduces crop yield.
2. **Bad Timing**: If you apply fertilizer right before heavy rain, the water washes it away into underground water (**Leaching**), wasting the fertilizer and polluting drinking water. If you apply it on very hot, dry, and windy days, the fertilizer burns the plant leaves (**Burn Risk**).

**GeoN-DSS** solves this using Machine Learning and Satellite data for 4 districts in Uttar Pradesh (**Lucknow, Kanpur, Amethi, Gorakhpur**):
- The farmer draws their field boundary on an interactive map.
- The system checks satellite vegetation health (NDVI, NDRE) and 48-hour weather forecasts.
- A **Safety Gatekeeper (LightGBM)** decides if it is safe to apply fertilizer today (`GO` or `NO-GO`).
- If safe (`GO`), a **Dosage Regressor (XGBoost)** calculates the exact kilograms of Nitrogen needed and gives a **40% today / 60% after irrigation** split schedule, also converted into commercial 45 kg Urea bags.

---

## 2. Dataset Creation & Core Parameters

Since no ready-made dataset existed linking satellite images, weather, and fertilizer advice for UP farms, we generated a physics-informed dataset of **15,000 field records** with **64 parameters** based on ICAR (Indian Council of Agricultural Research) standards.

### The 5 Key Groups of Parameters:
1. **Location Features**: District (Lucknow, Kanpur, Amethi, Gorakhpur), field area in hectares, latitude and longitude.
2. **Satellite Spectral Indices (Sentinel-2)**:
   - **NDVI**: Measures overall green plant biomass.
   - **GNDVI**: Measures green chlorophyll pigment.
   - **NDRE (Red-Edge)**: The most important satellite index for nitrogen. When crops lack nitrogen, NDRE drops first.
   - **15-Day Trends**: Whether NDRE is going up (crop is healthy) or going down (crop is starving for nitrogen).
3. **Weather Parameters (Open-Meteo / ERA5)**:
   - Maximum & average temperatures, humidity, wind speed.
   - Rainfall in the last 24–48 hours, and forecasted rain in the next 48 hours.
   - Weather condition (Sunny, Cloudy, Rain, Thunderstorm, Fog).
4. **Soil Properties**:
   - Soil texture (% clay, % sand, % silt). Sandy soil leaches faster; clay soil holds nutrients.
   - Soil pH, Soil Organic Carbon, available native nitrogen.
5. **Crop & Farming Information**:
   - Season: **Kharif** (monsoon), **Rabi** (winter), **Zaid** (summer).
   - 15 popular UP crops: Wheat, Rice, Sugarcane, Maize, Potato, Mustard, Onion, Bajra, and Pulses (Arhar, Soybean, Chickpea, Lentil, Moong).
   - Growth Stage: Germination, Vegetative, Tillering, Booting, Flowering, Grain Fill.
   - Previous Crop Credit: If the farmer previously grew pulses (legumes like Arhar or Moong), the soil already has natural nitrogen, so the system deducts 20 to 35 kg of fertilizer demand!

---

## 3. What Was Done in Exploratory Data Analysis (EDA)?

Before training any AI models, we analyzed the dataset to make sure the data behaves like real agriculture. We generated 10 visual graphs (saved in `ml/reports/figures/`):

1. **Class Distribution (`01_class_distribution.png`)**:
   - 51.6% records were NO-GO Leaching (makes sense because UP gets heavy monsoon rain in Kharif).
   - 13.2% records were NO-GO Burn (hot and dry summer days).
   - 35.2% records were GO Safe Windows.
2. **Nitrogen Spread (`02_n_distribution.png`)**:
   - Average nitrogen recommendation was **24.6 kg N/ha**, with a maximum around 110 kg N/ha for heavy feeders like Sugarcane and Maize.
3. **District & Season Patterns (`03_n_by_district_season.png`)**:
   - Gorakhpur has more clay-heavy soil and higher rainfall, which increases leaching risk.
   - Kanpur has sandier soil where water drains faster.
4. **The NDRE vs Nitrogen Relationship (`04_ndre_vs_n.png`)**:
   - Proved that as NDRE drops or trends downward, the crop shows nitrogen deficiency, and the required nitrogen dosage goes up.
5. **Risk Scores Verification (`05_risk_scores_by_class.png`)**:
   - Checked that our mathematical risk formulas cleanly separate safe days from dangerous days.
6. **Crop Comparison (`06_n_by_crop.png`)**:
   - Highest nitrogen needed: Sugarcane (50.5 kg/ha avg), Maize (41.6 kg/ha), Wheat (35.8 kg/ha).
   - Lowest nitrogen needed: Legumes like Chickpea (7.4 kg/ha) and Lentil (7.0 kg/ha) because they make their own nitrogen.
7. **Growth Stage Changes (`07_n_by_growth_stage.png`)**:
   - Nitrogen need peaks during **Tillering** and **Booting** (when the plant grows stems and grains), and drops to zero at maturity.
8. **Spectral Bands across Stages (`08_spectral_by_stage.png`)**:
   - Shows NDVI and NDRE rising as the crop grows green and falling as it turns golden for harvest.
9. **Correlation Matrix (`09_correlation_heatmap.png`)**:
   - Base crop demand has a strong positive correlation (+0.87) with recommendation.
   - Previous legume crop has a strong negative correlation (-0.38), proving natural nitrogen saves chemical fertilizer.
10. **Weather States (`10_weather_state.png`)**:
    - Checked distribution of sunny, cloudy, rainy, and foggy conditions across all districts.

---

## 4. How Were the Machine Learning Models Trained?

We used a **Two-Stage (Dual-Model) Architecture**:

### Model 1: The Safety Classifier (LightGBM)
- **Goal**: Decide whether today is safe to apply fertilizer.
- **Classes**:
  - Class 0 = `NO-GO: Leaching Hazard` (Rain is coming, soil is too wet).
  - Class 1 = `NO-GO: Burn Hazard` (Too hot, dry, and windy; fertilizer will scorch leaves).
  - Class 2 = `GO: Safe Window` (Weather and soil conditions are good).
- **Algorithm**: LightGBM (Light Gradient Boosting Machine).
- **Handling Imbalance**: We used balanced class weights so that rare burn-risk days are not missed.
- **Test Results**:
  - **99.91% Accuracy**
  - **0.9985 Macro F1-Score**
  - The confusion matrix (`classifier_confusion_matrix.png`) shows virtually zero misclassifications.

### Model 2: The Dosage Regressor (XGBoost)
- **Goal**: Calculate the exact amount of Nitrogen (kg/ha) needed for the crop.
- **Algorithm**: XGBoost Regressor (Extreme Gradient Boosting).
- **Features Used**: Satellite indices (NDVI, NDRE), crop type, growth stage, soil organic carbon, days after sowing, target yield, and previous crop credits.
- **Test Results**:
  - **R² Score = 0.9719** (Explains over 97% of the variance).
  - **MAE (Mean Absolute Error) = 3.10 kg N/ha** (On average, the prediction is within 3 kg of the ideal agricultural science recommendation).
  - **RMSE = 4.25 kg N/ha**.

---

## 5. Other Crucial Operations in the Project

1. **The Gatekeeper Logic**:
   - If Model 1 says `NO-GO`, the system **locks** the dosage and issues an alert (e.g., "Heavy rain forecast in 48 hours; wait 3 days").
   - If Model 1 says `GO`, the dosage is **unlocked** and shown to the farmer.
2. **Commercial Bag Conversion**:
   - Farmers buy Urea bags, not raw Nitrogen atoms.
   - Neem-coated Urea contains **46% Nitrogen**.
   - The system automatically converts pure Nitrogen into total Urea kilograms and calculates the number of **45 kg bags** needed for their specific field size.
3. **40% / 60% Split Schedule**:
   - Agronomists advise against applying all fertilizer in one go.
   - The system recommends **40% immediately** and **60% post-irrigation** (after 3–5 days).
4. **Interactive Map (React + Leaflet)**:
   - Farmers don't know latitudes and longitudes. They can simply click corners on the satellite map around their farm. The system automatically measures the area in hectares and finds the district.
5. **Decoupled Architecture**:
   - The React frontend runs on Port 5173.
   - The FastAPI backend runs on Port 8000.
   - They talk through clean REST API endpoints (`/api/v1/predict` and `/api/v1/field/info`).

---

## 6. Quick Cheat-Sheet for Viva & Presentations

| Question | Short, Direct Answer |
|---|---|
| **What is the main problem solved?** | Prevents nitrogen wastage, groundwater pollution from rain leaching, and leaf burning by timing and dosing fertilizer accurately. |
| **Why UP? Which districts?** | UP is India's largest fertilizer consumer. We focused on Lucknow, Kanpur, Amethi, and Gorakhpur. |
| **Why not just use NDVI?** | NDVI saturates at high green cover. We use **NDRE (Red-Edge)** because it directly detects leaf chlorophyll and nitrogen levels before visible yellowing occurs. |
| **Why two models instead of one?** | Separation of concerns: First classify safety (Gatekeeper), then calculate dosage only when safe. Recommending fertilizer when rain is coming is harmful. |
| **Which algorithms are used?** | **LightGBM** for fast 3-class safety classification, and **XGBoost** for continuous dosage regression. |
| **What is the accuracy?** | 99.9% classification accuracy; Regression has $R^2 = 0.97$ and an error of only $3.1$ kg N/ha. |
