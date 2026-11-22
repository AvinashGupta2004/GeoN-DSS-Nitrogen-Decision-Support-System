"""
Step 2: Model Training, Validation & Testing (Academic ML Lifecycle)
===================================================================
Project: GeoN-DSS Precision Agriculture (MMMUT Gorakhpur)
Models:
  1. LightGBM Safety Classifier (Gatekeeper Decision: Safe vs Rain vs Heat)
  2. XGBoost Dosage Regressor (Recommended N Dosage in kg N/ha)

Target Performance: Realistic 80% – 85% on unseen holdout test fields.
"""

import os
import json
import warnings
from pathlib import Path

# Configure Windows thread and matplotlib limits
os.environ["LOKY_MAX_CPU_COUNT"] = "4"
os.environ["MPLCONFIGDIR"] = os.environ.get("TEMP", "/tmp") + "/matplotlib"
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    r2_score,
    mean_absolute_error,
    mean_squared_error,
)
from lightgbm import LGBMClassifier
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "gorakhpur_mmmut_dataset.csv"
MODEL_DIR = ROOT / "ml" / "saved_models"
REPORT_DIR = ROOT / "ml" / "reports"
FIG_DIR = REPORT_DIR / "figures"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── Feature Sets (Simple, strictly < 15 columns, zero data leakage) ──────────
# Model 1 (Gatekeeper Classifier): Weather & Soil physical risks
CLF_FEATURES = ["rainfall_forecast_48h", "temperature_c", "soil_organic_carbon", "soil_ph"]
CLF_TARGET = "safety_decision"
CLASS_NAMES = {0: "Rain Risk (Leach)", 1: "Heat Risk (Burn)", 2: "Safe Window"}

# Model 2 (Dosage Regressor): Remote sensing, crop phenology & soil chemistry
REG_CATEGORICAL = ["crop_type", "growth_stage"]
REG_NUMERICAL = [
    "days_after_sowing",
    "ndvi",
    "ndre",
    "soil_organic_carbon",
    "soil_ph",
    "temperature_c",
]
REG_FEATURES = REG_CATEGORICAL + REG_NUMERICAL
REG_TARGET = "recommended_n_kg_ha"


def run_training_and_evaluation():
    print("=" * 72)
    print("STEP 2: MODEL TRAINING, VALIDATION & TESTING")
    print("Project: GeoN-DSS (MMMUT Gorakhpur Pilot)")
    print("=" * 72)

    # 1. Load Data
    print(f"\n[1/6] Ingesting Dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    print(f"      Total records: {len(df):,} | Features: {df.shape[1]}")

    # Prepare categorical types
    category_mappings = {}
    for col in REG_CATEGORICAL:
        df[col] = df[col].astype("category")
        category_mappings[col] = df[col].cat.categories.tolist()

    # 2. Train / Validation / Test Splitting (70% / 15% / 15%)
    print("\n[2/6] Performing Train-Validation-Test Split (70% / 15% / 15%)...")
    X_train_val, X_test, y_clf_trval, y_clf_test, y_reg_trval, y_reg_test = train_test_split(
        df, df[CLF_TARGET], df[REG_TARGET], test_size=0.15, random_state=42
    )

    X_train, X_val, y_clf_train, y_clf_val, y_reg_train, y_reg_val = train_test_split(
        X_train_val, y_clf_trval, y_reg_trval, test_size=0.1765, random_state=42
    )

    print(f"      Training Set:    {len(X_train):>4} samples ({len(X_train)/len(df)*100:.1f}%)")
    print(f"      Validation Set:  {len(X_val):>4} samples ({len(X_val)/len(df)*100:.1f}%)")
    print(f"      Unseen Test Set: {len(X_test):>4} samples ({len(X_test)/len(df)*100:.1f}%)")

    # 3. Train Model 1: LightGBM Safety Gatekeeper
    print("\n[3/6] Training Model 1: LightGBM Safety Classifier...")
    clf = LGBMClassifier(
        n_estimators=70,
        max_depth=3,
        learning_rate=0.08,
        random_state=42,
        verbosity=-1
    )
    clf.fit(
        X_train[CLF_FEATURES],
        y_clf_train,
        eval_set=[(X_val[CLF_FEATURES], y_clf_val)],
        callbacks=[]
    )
    print("      Model 1 training completed.")

    # 4. Evaluate Model 1 on Unseen Holdout Test Data
    print("\n[4/6] Evaluating Model 1 on Unseen Test Fields...")
    y_clf_pred = clf.predict(X_test[CLF_FEATURES])
    clf_acc = accuracy_score(y_clf_test, y_clf_pred)
    clf_bal_acc = balanced_accuracy_score(y_clf_test, y_clf_pred)
    clf_f1 = f1_score(y_clf_test, y_clf_pred, average="macro")

    print(f"      Test Accuracy:     {clf_acc*100:>6.2f}% (Target: 80-85% realistic)")
    print(f"      Balanced Accuracy: {clf_bal_acc*100:>6.2f}%")
    print(f"      Macro F1-Score:    {clf_f1:>6.4f}")
    print("\n      Detailed Classification Report:")
    report_str = classification_report(
        y_clf_test,
        y_clf_pred,
        target_names=[CLASS_NAMES[i] for i in sorted(list(y_clf_test.unique()))],
        digits=3
    )
    for line in report_str.split("\n"):
        print(f"        {line}")

    # Plot Confusion Matrix
    cm = confusion_matrix(y_clf_test, y_clf_pred)
    plt.figure(figsize=(6, 5))
    target_names = [CLASS_NAMES[i] for i in sorted(list(y_clf_test.unique()))]
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=target_names, yticklabels=target_names)
    plt.title(f"Safety Gatekeeper: Confusion Matrix (Acc = {clf_acc*100:.1f}%)", fontsize=11, fontweight="bold")
    plt.xlabel("Predicted Decision")
    plt.ylabel("Actual Condition")
    plt.tight_layout()
    cm_path = FIG_DIR / "classifier_confusion_matrix.png"
    plt.savefig(cm_path, dpi=160)
    plt.close()
    print(f"      [SAVED] {cm_path}")

    # 5. Train Model 2: XGBoost Dosage Regressor
    print("\n[5/6] Training Model 2: XGBoost Dosage Regressor...")
    reg = XGBRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.08,
        enable_categorical=True,
        random_state=42,
        verbosity=0
    )
    reg.fit(
        X_train[REG_FEATURES],
        y_reg_train,
        eval_set=[(X_val[REG_FEATURES], y_reg_val)],
        verbose=False
    )
    print("      Model 2 training completed.")

    # 6. Evaluate Model 2 on Unseen Holdout Test Data
    print("\n[6/6] Evaluating Model 2 on Unseen Test Fields...")
    y_reg_pred = reg.predict(X_test[REG_FEATURES])
    y_reg_pred = np.clip(y_reg_pred, 0.0, 140.0)

    r2 = r2_score(y_reg_test, y_reg_pred)
    mae = mean_absolute_error(y_reg_test, y_reg_pred)
    rmse = np.sqrt(mean_squared_error(y_reg_test, y_reg_pred))

    print(f"      R-Squared Score (R²): {r2:>6.4f} ({r2*100:.2f}% variance explained) (Target: 80-85% realistic)")
    print(f"      Mean Absolute Error:  {mae:>6.2f} kg N/ha")
    print(f"      Root Mean Sq Error:   {rmse:>6.2f} kg N/ha")

    # Plot Actual vs Predicted
    plt.figure(figsize=(6.5, 6))
    plt.scatter(y_reg_test, y_reg_pred, alpha=0.6, color="#16a34a", s=30, edgecolors="none")
    max_val = max(y_reg_test.max(), y_reg_pred.max())
    plt.plot([0, max_val], [0, max_val], color="#ef4444", lw=2, linestyle="--", label="Ideal Fit (y = x)")
    plt.title(f"XGBoost Dosage: Actual vs Predicted (R² = {r2:.3f})", fontsize=11, fontweight="bold")
    plt.xlabel("Actual N Requirement (kg N/ha)")
    plt.ylabel("Model Predicted N (kg N/ha)")
    plt.legend()
    plt.tight_layout()
    scatter_path = FIG_DIR / "regressor_actual_vs_predicted.png"
    plt.savefig(scatter_path, dpi=160)
    plt.close()
    print(f"      [SAVED] {scatter_path}")

    # Sample Predictions Comparison Table
    print("\n      Sample Test Predictions (Actual vs Model Predicted N):")
    print("      " + "-" * 64)
    print(f"      {'Crop':<12} {'Stage':<12} {'Actual':<10} {'Predicted':<12} {'Error':<8}")
    print("      " + "-" * 64)
    sample_sub = X_test.iloc[:6]
    for idx, (_, row) in enumerate(sample_sub.iterrows()):
        crop = row["crop_type"]
        stage = row["growth_stage"]
        act = y_reg_test.loc[row.name]
        pred = y_reg_pred[idx]
        err = pred - act
        sign = "+" if err >= 0 else ""
        print(f"      {crop:<12} {stage:<12} {act:>6.1f} kg   {pred:>7.1f} kg     {sign}{err:>5.1f} kg")
    print("      " + "-" * 64)

    # 7. Save Model Bundles for Production Backend & Live Demo
    clf_bundle = {
        "model": clf,
        "feature_columns": CLF_FEATURES,
        "categorical_features": [],
        "numerical_features": CLF_FEATURES,
        "category_mappings": {},
        "target_col": CLF_TARGET,
        "class_names": CLASS_NAMES,
    }
    joblib.dump(clf_bundle, MODEL_DIR / "lgbm_classifier.joblib")

    reg_bundle = {
        "model": reg,
        "feature_columns": REG_FEATURES,
        "categorical_features": REG_CATEGORICAL,
        "numerical_features": REG_NUMERICAL,
        "category_mappings": category_mappings,
        "target_col": REG_TARGET,
    }
    joblib.dump(reg_bundle, MODEL_DIR / "xgb_regressor.joblib")

    # Save metrics JSON for viva review
    metrics = {
        "classifier": {
            "accuracy": round(float(clf_acc), 4),
            "balanced_accuracy": round(float(clf_bal_acc), 4),
            "macro_f1": round(float(clf_f1), 4),
        },
        "regressor": {
            "r2_score": round(float(r2), 4),
            "mae_kg_n_ha": round(float(mae), 2),
            "rmse_kg_n_ha": round(float(rmse), 2),
        },
        "dataset_rows": len(df),
        "test_rows": len(X_test),
    }
    with open(REPORT_DIR / "evaluation_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n      [OK] Model bundles saved to ml/saved_models/")
    print(f"      [OK] Metrics summary saved to {REPORT_DIR / 'evaluation_metrics.json'}")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    run_training_and_evaluation()
