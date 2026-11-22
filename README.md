# 🌱 GeoN-DSS — Nitrogen Decision Support System
## Final Year Project | Uttar Pradesh Precision Agriculture Pilot

GeoN-DSS is a Machine Learning Decision Support System that recommends precision nitrogen dosage for agricultural fields across Uttar Pradesh (**Lucknow, Kanpur, Amethi, Gorakhpur**). 

The system couples **Sentinel-2 multispectral indices** (NDVI, GNDVI, NDRE) and **meteorological forecasts** with a **dual-model architecture** guarded by a Gatekeeper Decision system.

---

## 🏛️ System Architecture

```
User Frontend (React + Leaflet Map)
  │ GeoJSON Polygon + Crop Type + Phenology Stage
  ▼
FastAPI Processing & Risk Engine
  │ Spatial aggregation, Environmental Risk Scoring
  ▼
LightGBM Safety Classifier (Model 1) ───► Gatekeeper Decision
  │ Screens Leaching Risk & Fertilizer Burn Risk
  ├── [NO-GO: Class 0/1] ──► Locks application; issues rain/burn advisory
  └── [GO: Class 2]       ──► Unlocks XGBoost Dosage Regressor (Model 2)
                                │ Exact kg N/ha demand
                                ▼
                       Split Schedule Dashboard (40% immediate, 60% post-irrigation)
                       Commercial Conversion: Neem-Coated Urea & DAP Bags
```

---

## 🚀 Quick Start Guide

### 🎬 Live Viva / Demonstration Runner (All-in-One Simulation)
Run this single command to perform live EDA, train both models, test on unseen data, simulate Gatekeeper decisions, and display the final performance scorecard ($R^2$, MAE, Accuracy, F1):
```bash
# 1. Run live demonstration on complete UP dataset (15,000 records)
python run_live_demo.py

# 2. Or run live demonstration on Gorakhpur-specific dataset
python run_live_demo.py --dataset gorakhpur
```

---

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ (tested on v24.15)
- npm 10+

### 2. Backend Setup & Run
```bash
# Navigate to backend directory
cd backend

# (Optional) Install Python packages
pip install -r requirements.txt

# Run the FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger API docs: **http://localhost:8000/docs**
- Health check: **http://localhost:8000/api/v1/health**

Alternatively, run from root:
```bash
python start_backend.py
```

### 3. Frontend Setup & Run
```bash
# Navigate to frontend directory
cd frontend

# Run development server
npm run dev
```
- Open application in browser: **http://localhost:5173**

---

## 📊 Dataset & Model Performance

### Dataset (`data/synthetic/up_nitrogen_dataset.csv`)
- **15,000 records × 64 columns** calibrated with ICAR nitrogen response guidelines for UP agro-climatic zones.
- Covers 15 UP crops across **Kharif, Rabi, and Zaid** seasons.
- 4 UP districts with regional soil profiles: Lucknow, Kanpur, Amethi, Gorakhpur.

### LightGBM Safety Classifier
- **Accuracy**: **99.91%**
- **Macro F1-Score**: **0.9985**
- **Balanced Accuracy**: **99.78%**
- Saved artifact: `ml/saved_models/lgbm_classifier.joblib`

### XGBoost Dosage Regressor
- **R² Score**: **0.9719**
- **Mean Absolute Error (MAE)**: **3.10 kg N/ha**
- **RMSE**: **4.25 kg N/ha**
- Saved artifact: `ml/saved_models/xgb_regressor.joblib`

### EDA Figures & Reports
Generated plots located in `ml/reports/figures/`:
1. `01_class_distribution.png` — Window safety class proportions
2. `02_n_distribution.png` — Nitrogen recommendation distribution
3. `03_n_by_district_season.png` — Regional & seasonal variance
4. `04_ndre_vs_n.png` — NDRE red-edge index vs N demand
5. `05_risk_scores_by_class.png` — Leaching and burn risk distributions
6. `06_n_by_crop.png` — Crop-wise baseline nitrogen requirements
7. `07_n_by_growth_stage.png` — Phenological stage demand curves
8. `08_spectral_by_stage.png` — NDVI, GNDVI, NDRE canopy curves
9. `09_correlation_heatmap.png` — Feature correlation matrix
10. `10_weather_state.png` — District-level weather distributions
11. `classifier_confusion_matrix.png` & `classifier_feature_importance.png`
12. `regressor_actual_vs_predicted.png` & `regressor_feature_importance.png`
