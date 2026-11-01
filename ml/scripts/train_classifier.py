"""
GeoN-DSS — Train LightGBM Safety Classifier
============================================
Predicts application_window_class:
  0: NO-GO Leaching Risk
  1: NO-GO Fertilizer Burn Risk
  2: GO Safe Application Window

Saves:
  - ml/saved_models/lgbm_classifier.joblib
  - ml/saved_models/feature_pipeline.joblib
  - ml/reports/classifier_metrics.json
  - ml/reports/figures/classifier_confusion_matrix.png
  - ml/reports/figures/classifier_feature_importance.png
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
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    balanced_accuracy_score,
    accuracy_score
)
from sklearn.model_selection import train_test_split

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
TARGET_COLUMN = "application_window_class"
CLASS_NAMES = ["NO-GO Leach (0)", "NO-GO Burn (1)", "GO Safe (2)"]


def main():
    print("=" * 60)
    print("GeoN-DSS: Training LightGBM Safety Classifier")
    print("=" * 60)

    # 1. Load Data
    print(f"\n[1/5] Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    print(f"Total dataset shape: {df.shape}")

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    # Convert categoricals to category dtype for LightGBM native support
    category_mappings = {}
    for col in CATEGORICAL_FEATURES:
        X[col] = X[col].astype("category")
        category_mappings[col] = X[col].cat.categories.tolist()

    # 2. Train / Validation / Test Split (70 / 15 / 15)
    print("\n[2/5] Stratified train/val/test splitting...")
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.1765, random_state=42, stratify=y_train_val
    )  # 0.85 * 0.1765 ≈ 0.15 of total

    print(f"Train size: {X_train.shape[0]} ({X_train.shape[0]/len(df):.1%})")
    print(f"Val size:   {X_val.shape[0]} ({X_val.shape[0]/len(df):.1%})")
    print(f"Test size:  {X_test.shape[0]} ({X_test.shape[0]/len(df):.1%})")

    # 3. Model Training
    print("\n[3/5] Fitting LightGBM Classifier...")
    model = LGBMClassifier(
        objective="multiclass",
        num_class=3,
        class_weight="balanced",
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=-1
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[]
    )

    # 4. Evaluation on Test Set
    print("\n[4/5] Evaluating on unseen test set...")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)

    acc = accuracy_score(y_test, y_pred)
    bal_acc = balanced_accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average="macro")
    f1_weighted = f1_score(y_test, y_pred, average="weighted")
    report = classification_report(y_test, y_pred, target_names=CLASS_NAMES, output_dict=True)

    print(f"\nAccuracy:          {acc:.4f}")
    print(f"Balanced Accuracy: {bal_acc:.4f}")
    print(f"Macro F1-Score:    {f1_macro:.4f}")
    print(f"Weighted F1-Score: {f1_weighted:.4f}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=CLASS_NAMES))

    # Save metrics
    metrics_summary = {
        "accuracy": float(acc),
        "balanced_accuracy": float(bal_acc),
        "macro_f1": float(f1_macro),
        "weighted_f1": float(f1_weighted),
        "classification_report": report,
    }
    with open(REPORT_DIR / "classifier_metrics.json", "w") as f:
        json.dump(metrics_summary, f, indent=2)

    # 5. Visualizations
    # A. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(7, 6))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES
    )
    plt.title("LightGBM Safety Classifier — Confusion Matrix", fontsize=12, fontweight="bold")
    plt.xlabel("Predicted Class")
    plt.ylabel("True Class")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "classifier_confusion_matrix.png", dpi=150)
    plt.close()

    # B. Feature Importance
    importance = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False).head(20)

    plt.figure(figsize=(10, 7))
    sns.barplot(data=importance, x="importance", y="feature", palette="mako")
    plt.title("Top 20 Features — LightGBM Safety Classifier", fontsize=12, fontweight="bold")
    plt.xlabel("Split Feature Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "classifier_feature_importance.png", dpi=150)
    plt.close()

    # 6. Save Model Bundle
    print("\n[5/5] Saving model and metadata...")
    model_bundle = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "categorical_features": CATEGORICAL_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "class_names": CLASS_NAMES,
        "category_mappings": category_mappings,
    }
    model_save_path = MODEL_DIR / "lgbm_classifier.joblib"
    joblib.dump(model_bundle, model_save_path)
    print(f"Model successfully saved to {model_save_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
