"""
GeoN-DSS — Train XGBoost Dosage Regressor
=========================================
Predicts recommended_N_kg_ha (optimal nitrogen dosage in kg N/ha).

Saves:
  - ml/saved_models/xgb_regressor.joblib
  - ml/reports/regressor_metrics.json
  - ml/reports/figures/regressor_actual_vs_predicted.png
  - ml/reports/figures/regressor_feature_importance.png
  - ml/reports/figures/regressor_residual_distribution.png
"""

import json
import warnings
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "synthetic" / "up_nitrogen_dataset.csv"
MODEL_DIR = ROOT / "ml" / "saved_models"
REPORT_DIR = ROOT / "ml" / "reports"
FIG_DIR = REPORT_DIR / "figures"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── Feature Definition ────────────────────────────────────────────────────────
CATEGORICAL_FEATURES = [
    "district",
    "soil_type",
    "crop_type",
    "crop_season",
    "growth_stage",
    "previous_crop",
    "irrigation_type",
    "fertilizer_history",
]

NUMERICAL_FEATURES = [
    "lat_sin", "lat_cos", "lon_sin", "lon_cos", "elevation_m", "slope_deg", "field_area_ha",
    "ndvi", "gndvi", "ndre", "evi", "lai", "cloud_coverage_pct",
    "ndvi_15d_trend", "gndvi_15d_trend", "ndre_15d_trend",
    "temp_max_c", "temp_min_c", "temp_avg_c",
    "rainfall_24h_mm", "rainfall_48h_mm", "rainfall_forecast_48h_mm",
    "humidity_pct", "wind_speed_ms", "solar_radiation_wm2", "et0_mm", "weather_state",
    "soil_ph", "soil_organic_carbon_gkg", "cec_cmolkg",
    "clay_pct", "sand_pct", "silt_pct", "bulk_density_kgdm3", "nitrogen_soil_gkg",
    "days_after_sowing", "target_yield_tha", "gdd_accumulated",
    "ndvi_ndre_ratio", "rain_leach_score", "burn_risk_score",
    "n_removal_estimate", "soil_n_supply", "base_n_demand", "previous_crop_n_credit",
]

FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
TARGET_COLUMN = "recommended_N_kg_ha"


def main():
    print("=" * 60)
    print("GeoN-DSS: Training XGBoost Dosage Regressor")
    print("=" * 60)

    # 1. Load Data
    print(f"\n[1/5] Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    print(f"Total dataset shape: {df.shape}")

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    # Convert categoricals to category dtype for XGBoost native categorical support
    category_mappings = {}
    for col in CATEGORICAL_FEATURES:
        X[col] = X[col].astype("category")
        category_mappings[col] = X[col].cat.categories.tolist()

    # 2. Train / Validation / Test Split (70 / 15 / 15)
    print("\n[2/5] Train/val/test splitting...")
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.1765, random_state=42
    )

    print(f"Train size: {X_train.shape[0]} ({X_train.shape[0]/len(df):.1%})")
    print(f"Val size:   {X_val.shape[0]} ({X_val.shape[0]/len(df):.1%})")
    print(f"Test size:  {X_test.shape[0]} ({X_test.shape[0]/len(df):.1%})")

    # 3. Model Training
    print("\n[3/5] Fitting XGBoost Regressor...")
    model = XGBRegressor(
        n_estimators=450,
        learning_rate=0.04,
        max_depth=6,
        subsample=0.85,
        colsample_bytree=0.85,
        tree_method="hist",
        enable_categorical=True,
        random_state=42,
        verbosity=0
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )

    # 4. Evaluation on Test Set
    print("\n[4/5] Evaluating on unseen test set...")
    y_pred = model.predict(X_test)

    # Nitrogen cannot be negative
    y_pred = np.clip(y_pred, 0, 150)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    print(f"\nTest MAE:   {mae:.2f} kg N/ha")
    print(f"Test RMSE:  {rmse:.2f} kg N/ha")
    print(f"Test R²:    {r2:.4f}")

    # Save metrics
    metrics_summary = {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2_score": float(r2),
        "test_records_count": len(y_test)
    }
    with open(REPORT_DIR / "regressor_metrics.json", "w") as f:
        json.dump(metrics_summary, f, indent=2)

    # 5. Visualizations
    # A. Actual vs Predicted
    plt.figure(figsize=(7, 7))
    plt.scatter(y_test, y_pred, alpha=0.3, color="#2980b9", s=15, edgecolors="none")
    max_val = max(y_test.max(), y_pred.max())
    plt.plot([0, max_val], [0, max_val], color="#e74c3c", lw=2, linestyle="--", label="Ideal Fit (y = x)")
    plt.title(f"XGBoost Regressor: Actual vs Predicted N (R² = {r2:.3f})", fontsize=12, fontweight="bold")
    plt.xlabel("Actual Recommended N (kg/ha)")
    plt.ylabel("Predicted Recommended N (kg/ha)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "regressor_actual_vs_predicted.png", dpi=150)
    plt.close()

    # B. Feature Importance
    importance = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False).head(20)

    plt.figure(figsize=(10, 7))
    sns.barplot(data=importance, x="importance", y="feature", palette="viridis")
    plt.title("Top 20 Features — XGBoost Dosage Regressor", fontsize=12, fontweight="bold")
    plt.xlabel("Gain / Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "regressor_feature_importance.png", dpi=150)
    plt.close()

    # C. Residual Distribution
    residuals = y_test - y_pred
    plt.figure(figsize=(8, 5))
    sns.histplot(residuals, kde=True, color="#8e44ad", bins=40)
    plt.axvline(0, color="red", linestyle="--", lw=1.5)
    plt.title("Residual Distribution (Actual - Predicted N)", fontsize=12, fontweight="bold")
    plt.xlabel("Error (kg N/ha)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "regressor_residual_distribution.png", dpi=150)
    plt.close()

    # 6. Save Model Bundle
    print("\n[5/5] Saving model and metadata...")
    model_bundle = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "categorical_features": CATEGORICAL_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "category_mappings": category_mappings,
    }
    model_save_path = MODEL_DIR / "xgb_regressor.joblib"
    joblib.dump(model_bundle, model_save_path)
    print(f"Model successfully saved to {model_save_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
