"""
Train & Test GeoN-DSS Models on Any Custom Dataset (e.g. Gorakhpur)
===================================================================

Usage:
    # 1. Train and evaluate on Gorakhpur dataset
    python ml/scripts/train_on_custom_dataset.py --data data/processed/gorakhpur_custom_dataset.csv

    # 2. Train and immediately activate as the live backend models
    python ml/scripts/train_on_custom_dataset.py --data data/processed/gorakhpur_custom_dataset.csv --activate

Outputs:
    - Trained Classifier: ml/saved_models/<prefix>lgbm_classifier.joblib
    - Trained Regressor:  ml/saved_models/<prefix>xgb_regressor.joblib
    - Evaluation Report:  ml/reports/<prefix>evaluation_report.json
    - Performance Charts: ml/reports/figures/<prefix>*.png
"""

import argparse
import json
import os
import warnings
from pathlib import Path

# Silence Loky CPU warning on Windows sandbox
os.environ["LOKY_MAX_CPU_COUNT"] = "4"
os.environ["MPLCONFIGDIR"] = os.environ.get("TEMP", "/tmp") + "/matplotlib"
warnings.filterwarnings("ignore")

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "ml" / "saved_models"
REPORT_DIR = ROOT / "ml" / "reports"
FIG_DIR = REPORT_DIR / "figures"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

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
CLASS_NAMES = ["NO-GO Leach (0)", "NO-GO Burn (1)", "GO Safe (2)"]


def train_and_test(data_path: Path, prefix: str, activate_live: bool):
    print("=" * 70)
    print("GeoN-DSS Custom Dataset Training & Testing Pipeline")
    print(f"Dataset:  {data_path}")
    print(f"Prefix:   {prefix}")
    print(f"Activate: {'YES (Will update live backend models)' if activate_live else 'NO (Stored as dedicated model)'}")
    print("=" * 70)

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    # 1. Load Data
    print("\n[1/6] Loading and inspecting dataset...")
    df = pd.read_csv(data_path)
    print(f"Total Rows: {len(df):,} | Features: {len(FEATURE_COLUMNS)}")

    X = df[FEATURE_COLUMNS].copy()
    y_class = df["application_window_class"].copy()
    y_reg = df["recommended_N_kg_ha"].copy()

    # Convert categoricals & record training category mappings
    category_mappings = {}
    for col in CATEGORICAL_FEATURES:
        X[col] = X[col].astype("category")
        category_mappings[col] = X[col].cat.categories.tolist()

    # 2. Train / Validation / Test Splitting (70% / 15% / 15%)
    print("\n[2/6] Splitting into 70% Train, 15% Validation, 15% Unseen Test...")
    (
        X_train_val,
        X_test,
        y_class_train_val,
        y_class_test,
        y_reg_train_val,
        y_reg_test,
    ) = train_test_split(X, y_class, y_reg, test_size=0.15, random_state=42)

    (
        X_train,
        X_val,
        y_class_train,
        y_class_val,
        y_reg_train,
        y_reg_val,
    ) = train_test_split(
        X_train_val, y_class_train_val, y_reg_train_val, test_size=0.1765, random_state=42
    )

    print(f"Train Set:      {len(X_train):>5,} rows ({len(X_train)/len(df):.1%})")
    print(f"Validation Set: {len(X_val):>5,} rows ({len(X_val)/len(df):.1%})")
    print(f"Test Set:       {len(X_test):>5,} rows ({len(X_test)/len(df):.1%})")

    # 3. Model 1: Train LightGBM Safety Classifier
    print("\n[3/6] Training LightGBM Safety Classifier...")
    num_classes = len(y_class.unique())
    clf = LGBMClassifier(
        objective="multiclass" if num_classes > 2 else "binary",
        num_class=num_classes if num_classes > 2 else None,
        class_weight="balanced",
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        num_leaves=25,
        random_state=42,
        verbosity=-1,
    )
    clf.fit(X_train, y_class_train, eval_set=[(X_val, y_class_val)], callbacks=[])

    # 4. Model 1 Testing & Evaluation
    print("\n[4/6] Testing Classifier on unseen test set...")
    y_class_pred = clf.predict(X_test)
    clf_acc = accuracy_score(y_class_test, y_class_pred)
    clf_bal_acc = balanced_accuracy_score(y_class_test, y_class_pred)
    clf_f1 = f1_score(y_class_test, y_class_pred, average="macro")

    present_classes = sorted(list(y_class_test.unique()))
    target_names = [CLASS_NAMES[c] for c in present_classes]

    print(f"  Accuracy:          {clf_acc:.4f} ({clf_acc*100:.2f}%)")
    print(f"  Balanced Accuracy: {clf_bal_acc:.4f}")
    print(f"  Macro F1-Score:    {clf_f1:.4f}")
    print("\nClassification Report (Test Set):")
    print(classification_report(y_class_test, y_class_pred, target_names=target_names))

    # Confusion matrix chart
    cm = confusion_matrix(y_class_test, y_class_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=target_names, yticklabels=target_names)
    plt.title(f"Safety Classifier Confusion Matrix ({prefix})", fontsize=11, fontweight="bold")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    cm_path = FIG_DIR / f"{prefix}classifier_confusion_matrix.png"
    plt.savefig(cm_path, dpi=140)
    plt.close()

    # 5. Model 2: Train XGBoost Dosage Regressor
    print("\n[5/6] Training XGBoost Dosage Regressor...")
    reg = XGBRegressor(
        n_estimators=350,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.85,
        colsample_bytree=0.85,
        tree_method="hist",
        enable_categorical=True,
        random_state=42,
        verbosity=0,
    )
    reg.fit(X_train, y_reg_train, eval_set=[(X_val, y_reg_val)], verbose=False)

    # 6. Model 2 Testing & Evaluation
    print("\n[6/6] Testing Regressor on unseen test set...")
    y_reg_pred = reg.predict(X_test)
    y_reg_pred = np.clip(y_reg_pred, 0, 150)

    mae = mean_absolute_error(y_reg_test, y_reg_pred)
    rmse = np.sqrt(mean_squared_error(y_reg_test, y_reg_pred))
    r2 = r2_score(y_reg_test, y_reg_pred)

    print(f"  R-Squared (R²):           {r2:.4f} ({r2*100:.2f}% variance explained)")
    print(f"  Mean Absolute Error (MAE): {mae:.2f} kg N/ha")
    print(f"  Root Mean Sq Error (RMSE): {rmse:.2f} kg N/ha")

    # Sample Predictions Comparison Table
    print("\nSample Test Predictions (Actual vs Predicted):")
    sample_df = pd.DataFrame({
        "Crop": df.loc[X_test.index[:8], "crop_type"].values,
        "Stage": df.loc[X_test.index[:8], "growth_stage"].values,
        "Actual N": y_reg_test.iloc[:8].round(1).values,
        "Predicted N": y_reg_pred[:8].round(1),
        "Error (kg)": (y_reg_pred[:8] - y_reg_test.iloc[:8].values).round(1),
    })
    print(sample_df.to_string(index=False))

    # Actual vs Predicted Plot
    plt.figure(figsize=(6, 6))
    plt.scatter(y_reg_test, y_reg_pred, alpha=0.5, color="#16a34a", s=25, edgecolors="none")
    max_val = max(y_reg_test.max(), y_reg_pred.max())
    plt.plot([0, max_val], [0, max_val], color="#ef4444", lw=2, linestyle="--", label="Ideal Fit (y=x)")
    plt.title(f"Actual vs Predicted Nitrogen (R² = {r2:.3f})", fontsize=11, fontweight="bold")
    plt.xlabel("Actual N Recommendation (kg N/ha)")
    plt.ylabel("Model Predicted N (kg N/ha)")
    plt.legend()
    plt.tight_layout()
    scatter_path = FIG_DIR / f"{prefix}regressor_actual_vs_predicted.png"
    plt.savefig(scatter_path, dpi=140)
    plt.close()

    # 7. Save Model Bundles
    clf_bundle = {
        "model": clf,
        "feature_columns": FEATURE_COLUMNS,
        "categorical_features": CATEGORICAL_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "class_names": CLASS_NAMES,
        "category_mappings": category_mappings,
    }
    reg_bundle = {
        "model": reg,
        "feature_columns": FEATURE_COLUMNS,
        "categorical_features": CATEGORICAL_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "category_mappings": category_mappings,
    }

    # Save dedicated prefix files
    clf_save_path = MODEL_DIR / f"{prefix}lgbm_classifier.joblib"
    reg_save_path = MODEL_DIR / f"{prefix}xgb_regressor.joblib"
    joblib.dump(clf_bundle, clf_save_path)
    joblib.dump(reg_bundle, reg_save_path)
    print(f"\n[OK] Dedicated models saved:")
    print(f"     Classifier: {clf_save_path}")
    print(f"     Regressor:  {reg_save_path}")

    # If activate requested, overwrite active live models
    if activate_live:
        joblib.dump(clf_bundle, MODEL_DIR / "lgbm_classifier.joblib")
        joblib.dump(reg_bundle, MODEL_DIR / "xgb_regressor.joblib")
        print("\n[ACTIVE] Live backend models updated! The web app will now use this trained model.")

    # Save evaluation metrics JSON
    metrics = {
        "dataset": str(data_path),
        "total_rows": len(df),
        "test_rows": len(X_test),
        "classifier": {
            "accuracy": float(clf_acc),
            "balanced_accuracy": float(clf_bal_acc),
            "macro_f1": float(clf_f1),
        },
        "regressor": {
            "r2_score": float(r2),
            "mae_kg_ha": float(mae),
            "rmse_kg_ha": float(rmse),
        },
    }
    report_file = REPORT_DIR / f"{prefix}evaluation_report.json"
    with open(report_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"     Evaluation Report saved: {report_file}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Train & test models on any dataset")
    parser.add_argument(
        "--data",
        default="data/processed/gorakhpur_custom_dataset.csv",
        help="Path to CSV dataset",
    )
    parser.add_argument(
        "--prefix",
        default="gorakhpur_",
        help="Prefix for saved models and reports (e.g. gorakhpur_)",
    )
    parser.add_argument(
        "--activate",
        action="store_true",
        help="Also overwrite active live backend models (lgbm_classifier.joblib & xgb_regressor.joblib)",
    )
    args = parser.parse_args()

    train_and_test(Path(args.data), args.prefix, args.activate)


if __name__ == "__main__":
    main()
