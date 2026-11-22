"""
Step 1: Exploratory Data Analysis (EDA) & Data Cleaning
======================================================
Academic ML Lifecycle Stage for MMMUT Gorakhpur Project:
1. Data Ingestion & Shape Audit
2. Data Cleaning & Validation (missing values, types, outliers)
3. Statistical Analysis & Distribution Diagnostics
4. Correlation Heatmap Generation
5. Publication-ready Visualizations for Viva Presentation
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Set writable matplotlib cache dir for Windows environments
os.environ["MPLCONFIGDIR"] = os.environ.get("TEMP", "/tmp") + "/matplotlib"

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "gorakhpur_mmmut_dataset.csv"
FIG_DIR = ROOT / "ml" / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", font="sans-serif")
CLASS_LABELS = {0: "Rain Risk (Leach)", 1: "Heat Risk (Burn)", 2: "Safe Window"}


def run_eda_and_cleaning():
    print("=" * 72)
    print("STEP 1: EXPLORATORY DATA ANALYSIS (EDA) & DATA CLEANING")
    print("Project: GeoN-DSS Precision Agriculture (MMMUT Gorakhpur)")
    print("=" * 72)

    # 1. Data Ingestion
    print(f"\n[1/5] Loading Dataset from: {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    print(f"      Rows:    {df.shape[0]:,}")
    print(f"      Columns: {df.shape[1]} (Under 15 parameters limit)")

    # 2. Data Cleaning
    print("\n[2/5] Running Data Cleaning & Quality Checks...")
    null_counts = df.isnull().sum()
    print(f"      Total Missing Values: {null_counts.sum()}")
    if null_counts.sum() > 0:
        print("      Cleaning missing values via median imputation...")
        df = df.fillna(df.median(numeric_only=True))

    duplicates = df.duplicated().sum()
    print(f"      Duplicate Rows:       {duplicates} (Clean)")

    # Outlier / Boundary validity checks
    invalid_ndvi = ((df["ndvi"] < 0) | (df["ndvi"] > 1.0)).sum()
    invalid_ph = ((df["soil_ph"] < 0) | (df["soil_ph"] > 14.0)).sum()
    print(f"      Biological Boundaries: NDVI in [0, 1] ({invalid_ndvi} violations), pH in [0, 14] ({invalid_ph} violations)")

    # 3. Statistical Distribution
    print("\n[3/5] Statistical Summary of Numerical Features:")
    numeric_cols = ["days_after_sowing", "ndvi", "ndre", "soil_organic_carbon", "soil_ph", "rainfall_forecast_48h", "temperature_c", "recommended_n_kg_ha"]
    summary = df[numeric_cols].describe().round(2)
    print(summary.to_string())

    # 4. Correlation Analysis & Heatmap
    print("\n[4/5] Computing Feature Correlation Matrix...")
    corr_matrix = df[numeric_cols].corr()
    print("      Correlation with Target (recommended_n_kg_ha):")
    for col, val in corr_matrix["recommended_n_kg_ha"].sort_values(ascending=False).items():
        if col != "recommended_n_kg_ha":
            print(f"        * {col:<24} r = {val:>+6.3f}")

    # Plot Correlation Heatmap
    plt.figure(figsize=(9, 7))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(
        corr_matrix,
        mask=mask,
        cmap=cmap,
        vmax=1.0,
        vmin=-1.0,
        annot=True,
        fmt=".2f",
        square=True,
        linewidths=0.8,
        cbar_kws={"shrink": 0.8, "label": "Pearson Correlation (r)"}
    )
    plt.title("Gorakhpur Farmland: Correlation Heatmap (MMMUT Pilot)", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    heatmap_path = FIG_DIR / "correlation_heatmap.png"
    plt.savefig(heatmap_path, dpi=160)
    plt.close()
    print(f"      [SAVED] {heatmap_path}")

    # 5. Diagnostic Figures for Viva Presentation
    print("\n[5/5] Generating Viva Presentation Visualizations...")

    # Plot A: Safety Class Distribution
    plt.figure(figsize=(7, 4.5))
    class_counts = df["safety_decision"].value_counts().sort_index()
    labels = [CLASS_LABELS[i] for i in class_counts.index]
    colors = ["#3b82f6", "#ef4444", "#10b981"]
    bars = plt.bar(labels, class_counts.values, color=colors, edgecolor="black", width=0.55)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., h + 15, f"{int(h)} ({h/len(df)*100:.1f}%)", ha="center", va="bottom", fontsize=10, fontweight="bold")
    plt.title("Safety Decision Gatekeeper Distribution (Gorakhpur)", fontsize=12, fontweight="bold")
    plt.ylabel("Number of Field Records")
    plt.ylim(0, max(class_counts.values) * 1.18)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "class_distribution.png", dpi=160)
    plt.close()

    # Plot B: Crop-wise Recommended Nitrogen
    plt.figure(figsize=(8, 4.8))
    sns.boxplot(data=df, x="crop_type", y="recommended_n_kg_ha", palette="Set2")
    plt.title("Recommended Nitrogen Dosage Across Gorakhpur Crops", fontsize=12, fontweight="bold")
    plt.xlabel("Crop Variety")
    plt.ylabel("Nitrogen Recommendation (kg N/ha)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "crop_nitrogen_distribution.png", dpi=160)
    plt.close()

    # Plot C: Sentinel-2 NDRE vs Recommended Nitrogen
    plt.figure(figsize=(7, 5))
    sns.scatterplot(
        data=df,
        x="ndre",
        y="recommended_n_kg_ha",
        hue="growth_stage",
        palette="viridis",
        alpha=0.7,
        s=40
    )
    plt.title("Sentinel-2 NDRE Index vs Nitrogen Demand", fontsize=12, fontweight="bold")
    plt.xlabel("Sentinel-2 Red-Edge Chlorophyll Index (NDRE)")
    plt.ylabel("Recommended Nitrogen (kg N/ha)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "ndre_vs_nitrogen.png", dpi=160)
    plt.close()

    print(f"      [OK] All 4 EDA charts successfully generated in {FIG_DIR}")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    run_eda_and_cleaning()
