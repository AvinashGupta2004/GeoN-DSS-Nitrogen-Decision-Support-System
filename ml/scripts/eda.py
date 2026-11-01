"""
GeoN-DSS — 01 Exploratory Data Analysis
=========================================
Run:  python ml/scripts/eda.py
Saves all plots to:  ml/reports/figures/
"""

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # non-interactive backend for script mode
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parents[2]
DATA_CSV = ROOT / "data" / "synthetic" / "up_nitrogen_dataset.csv"
FIG_DIR  = ROOT / "ml" / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
PALETTE  = {0: "#e74c3c", 1: "#f39c12", 2: "#27ae60"}
CLASS_LABELS = {0: "NO-GO\nLeach", 1: "NO-GO\nBurn", 2: "GO\nSafe"}

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading dataset ...")
df = pd.read_csv(DATA_CSV)
print(f"  Shape : {df.shape}")
print(f"  Columns : {len(df.columns)}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1  —  Dataset Overview
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- SECTION 1: Dataset Overview ---")
print(df.dtypes.value_counts())
missing = df.isnull().sum()
print(f"Missing values : {missing[missing > 0].to_dict() or 'None'}")
print(df[["recommended_N_kg_ha", "ndre", "rain_leach_score",
          "burn_risk_score", "ndvi", "gndvi"]].describe().round(3))


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1  —  Class Distribution
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Application Window Class Distribution", fontsize=14, fontweight="bold")

counts = df["application_window_class"].value_counts().sort_index()
bars = axes[0].bar(
    [CLASS_LABELS[k] for k in counts.index],
    counts.values,
    color=[PALETTE[k] for k in counts.index],
    edgecolor="white", linewidth=1.5, width=0.55
)
for bar, val in zip(bars, counts.values):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 60,
                 f"{val:,}\n({val/len(df)*100:.1f}%)", ha="center", va="bottom", fontsize=10)
axes[0].set_ylabel("Record Count")
axes[0].set_title("Count per Class")
axes[0].set_ylim(0, counts.max() * 1.18)

wedge_labels = [f"Class {k}\n{v:,}\n({v/len(df)*100:.1f}%)"
                for k, v in zip(counts.index, counts.values)]
axes[1].pie(counts.values, labels=wedge_labels,
            colors=[PALETTE[k] for k in counts.index],
            startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 2})
axes[1].set_title("Proportion")

plt.tight_layout()
fig.savefig(FIG_DIR / "01_class_distribution.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved: 01_class_distribution.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2  —  N Recommendation Distribution
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Recommended Nitrogen Distribution (kg N/ha)", fontsize=14, fontweight="bold")

axes[0].hist(df["recommended_N_kg_ha"], bins=60, color="#3498db", edgecolor="white", alpha=0.85)
axes[0].axvline(df["recommended_N_kg_ha"].mean(), color="#e74c3c", lw=2,
                label=f"Mean: {df['recommended_N_kg_ha'].mean():.1f} kg/ha")
axes[0].axvline(df["recommended_N_kg_ha"].median(), color="#f39c12", lw=2, ls="--",
                label=f"Median: {df['recommended_N_kg_ha'].median():.1f} kg/ha")
axes[0].set_xlabel("Recommended N (kg/ha)")
axes[0].set_ylabel("Frequency")
axes[0].set_title("Overall Distribution")
axes[0].legend()

for cls, color in PALETTE.items():
    subset = df[df["application_window_class"] == cls]["recommended_N_kg_ha"]
    axes[1].hist(subset, bins=50, alpha=0.65, color=color, label=CLASS_LABELS[cls].replace("\n", " "))
axes[1].set_xlabel("Recommended N (kg/ha)")
axes[1].set_ylabel("Frequency")
axes[1].set_title("Distribution by Window Class")
axes[1].legend()

plt.tight_layout()
fig.savefig(FIG_DIR / "02_n_distribution.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved: 02_n_distribution.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3  —  N Recommendation by District & Season
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Nitrogen Recommendation by District & Season", fontsize=14, fontweight="bold")

district_order = df.groupby("district")["recommended_N_kg_ha"].median().sort_values(ascending=False).index
sns.boxplot(data=df, x="district", y="recommended_N_kg_ha",
            order=district_order, palette="Blues_r",
            flierprops={"marker": ".", "markersize": 3}, ax=axes[0])
axes[0].set_xlabel("District")
axes[0].set_ylabel("Recommended N (kg/ha)")
axes[0].set_title("By District")

season_colors = {"KHARIF": "#2ecc71", "RABI": "#3498db", "ZAID": "#e67e22"}
sns.boxplot(data=df, x="crop_season", y="recommended_N_kg_ha",
            palette=season_colors,
            flierprops={"marker": ".", "markersize": 3}, ax=axes[1])
axes[1].set_xlabel("Crop Season")
axes[1].set_ylabel("Recommended N (kg/ha)")
axes[1].set_title("By Season")

plt.tight_layout()
fig.savefig(FIG_DIR / "03_n_by_district_season.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved: 03_n_by_district_season.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 4  —  NDRE vs Recommended N  (the core relationship)
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("NDRE vs Recommended Nitrogen — Core Relationship", fontsize=14, fontweight="bold")

sample = df.sample(n=min(4000, len(df)), random_state=42)
scatter = axes[0].scatter(
    sample["ndre"], sample["recommended_N_kg_ha"],
    c=sample["application_window_class"].map(PALETTE),
    alpha=0.4, s=18, edgecolors="none"
)
for cls, color in PALETTE.items():
    axes[0].scatter([], [], c=color, label=CLASS_LABELS[cls].replace("\n", " "), s=40)
axes[0].legend(title="Window Class", fontsize=9)
axes[0].set_xlabel("NDRE (Red-Edge Index)")
axes[0].set_ylabel("Recommended N (kg/ha)")
axes[0].set_title("NDRE vs N Demand (coloured by class)")

# Pearson correlation per class
for cls, color in PALETTE.items():
    sub = df[df["application_window_class"] == cls]
    corr = sub["ndre"].corr(sub["recommended_N_kg_ha"])
    label = f"Class {cls}: r = {corr:.3f}"
    sns.regplot(data=sub.sample(min(800, len(sub)), random_state=cls),
                x="ndre", y="recommended_N_kg_ha",
                scatter_kws={"alpha": 0.15, "s": 10, "color": color},
                line_kws={"color": color, "linewidth": 2},
                label=label, ax=axes[1])
axes[1].set_xlabel("NDRE")
axes[1].set_ylabel("Recommended N (kg/ha)")
axes[1].set_title("Regression Lines per Class")
axes[1].legend(fontsize=9)

plt.tight_layout()
fig.savefig(FIG_DIR / "04_ndre_vs_n.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved: 04_ndre_vs_n.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 5  —  Risk Scores by Class  (classifier's key features)
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Risk Score Distributions by Application Window Class", fontsize=14, fontweight="bold")

df["class_label"] = df["application_window_class"].map(
    {0: "NO-GO\nLeach (0)", 1: "NO-GO\nBurn (1)", 2: "GO Safe (2)"})
pal = {"NO-GO\nLeach (0)": "#e74c3c", "NO-GO\nBurn (1)": "#f39c12", "GO Safe (2)": "#27ae60"}

sns.violinplot(data=df, x="class_label", y="rain_leach_score",
               palette=pal, inner="quartile", cut=0, ax=axes[0])
axes[0].axhline(y=4.0, color="black", lw=2, ls="--", label="NO-GO threshold (4.0)")
axes[0].set_xlabel("Window Class")
axes[0].set_ylabel("Rain Leach Score")
axes[0].set_title("Rain Leach Score vs Class")
axes[0].legend(fontsize=9)

sns.violinplot(data=df, x="class_label", y="burn_risk_score",
               palette=pal, inner="quartile", cut=0, ax=axes[1])
axes[1].axhline(y=5.0, color="black", lw=2, ls="--", label="NO-GO threshold (5.0)")
axes[1].set_xlabel("Window Class")
axes[1].set_ylabel("Burn Risk Score")
axes[1].set_title("Burn Risk Score vs Class")
axes[1].legend(fontsize=9)

plt.tight_layout()
fig.savefig(FIG_DIR / "05_risk_scores_by_class.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved: 05_risk_scores_by_class.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 6  —  N by Crop Type (Top Crops)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle("Mean Recommended Nitrogen by Crop Type", fontsize=14, fontweight="bold")

crop_n = (df.groupby("crop_type")["recommended_N_kg_ha"]
           .agg(["mean", "std", "count"])
           .sort_values("mean", ascending=True))

bars = ax.barh(crop_n.index, crop_n["mean"],
               xerr=crop_n["std"] / np.sqrt(crop_n["count"]),
               color=sns.color_palette("viridis", len(crop_n)),
               edgecolor="white", linewidth=0.8, capsize=4)
ax.axvline(x=0, color="black", lw=0.8)
for i, (crop, row) in enumerate(crop_n.iterrows()):
    ax.text(row["mean"] + 0.5, i, f"{row['mean']:.1f}", va="center", fontsize=9)
ax.set_xlabel("Mean Recommended N (kg/ha)")
ax.set_title("Crops ordered by mean N demand — Legumes at bottom (N-fixing)")

plt.tight_layout()
fig.savefig(FIG_DIR / "06_n_by_crop.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved: 06_n_by_crop.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 7  —  N by Growth Stage
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
stage_order = ["GERMINATION", "VEGETATIVE", "TILLERING", "BOOTING",
               "FLOWERING", "GRAIN_FILL", "MATURITY"]
stage_in_data = [s for s in stage_order if s in df["growth_stage"].values]
sns.boxplot(data=df, x="growth_stage", y="recommended_N_kg_ha",
            order=stage_in_data, palette="rocket_r",
            flierprops={"marker": ".", "markersize": 3}, ax=ax)
ax.set_xlabel("Growth Stage")
ax.set_ylabel("Recommended N (kg/ha)")
ax.set_title("Nitrogen Demand Across Growth Stages", fontsize=13, fontweight="bold")
plt.tight_layout()
fig.savefig(FIG_DIR / "07_n_by_growth_stage.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved: 07_n_by_growth_stage.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 8  —  Spectral Indices by Growth Stage
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Spectral Indices Across Growth Stages", fontsize=14, fontweight="bold")

for ax, col, color, title in zip(
    axes,
    ["ndvi", "gndvi", "ndre"],
    ["#27ae60", "#2ecc71", "#e67e22"],
    ["NDVI (Biomass)", "GNDVI (Chlorophyll)", "NDRE (Nitrogen Status)"]
):
    sns.boxplot(data=df, x="growth_stage", y=col,
                order=stage_in_data, color=color,
                flierprops={"marker": ".", "markersize": 3}, ax=ax)
    ax.set_xlabel("Growth Stage")
    ax.set_ylabel(col.upper())
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=35)

plt.tight_layout()
fig.savefig(FIG_DIR / "08_spectral_by_stage.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved: 08_spectral_by_stage.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 9  —  Correlation Heatmap (Top Numeric Features)
# ─────────────────────────────────────────────────────────────────────────────
numeric_cols = [
    "recommended_N_kg_ha",
    "ndre", "gndvi", "ndvi", "ndre_15d_trend", "lai",
    "rain_leach_score", "burn_risk_score",
    "rainfall_24h_mm", "rainfall_forecast_48h_mm",
    "temp_max_c", "humidity_pct", "et0_mm", "wind_speed_ms",
    "soil_ph", "nitrogen_soil_gkg", "soil_organic_carbon_gkg", "clay_pct",
    "base_n_demand", "soil_n_supply", "previous_crop_n_credit",
    "target_yield_tha", "gdd_accumulated",
]
corr_df = df[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(16, 13))
mask = np.triu(np.ones_like(corr_df, dtype=bool))
sns.heatmap(corr_df, mask=mask, annot=True, fmt=".2f", linewidths=0.4,
            cmap="RdYlGn", center=0, vmin=-1, vmax=1,
            annot_kws={"size": 8}, ax=ax)
ax.set_title("Feature Correlation Matrix (Pearson r)", fontsize=14, fontweight="bold", pad=12)
plt.tight_layout()
fig.savefig(FIG_DIR / "09_correlation_heatmap.png", dpi=130, bbox_inches="tight")
plt.close(fig)
print("  Saved: 09_correlation_heatmap.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 10  —  Weather State Distribution
# ─────────────────────────────────────────────────────────────────────────────
ws_labels = {0: "SUNNY", 1: "PARTLY\nCLOUDY", 2: "OVERCAST",
             3: "RAINFALL", 4: "THUNDER\nSTORM", 5: "FOGGY"}
ws_colors = ["#f1c40f", "#bdc3c7", "#7f8c8d", "#3498db", "#8e44ad", "#95a5a6"]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Weather State Distribution", fontsize=14, fontweight="bold")

ws_counts = df["weather_state"].value_counts().sort_index()
axes[0].bar([ws_labels.get(k, str(k)) for k in ws_counts.index],
            ws_counts.values,
            color=[ws_colors[k] for k in ws_counts.index],
            edgecolor="white", linewidth=1.5)
axes[0].set_ylabel("Count")
axes[0].set_title("Overall Weather State Frequency")
for i, v in enumerate(ws_counts.values):
    axes[0].text(i, v + 20, f"{v:,}", ha="center", va="bottom", fontsize=9)

# by district
ws_by_dist = df.groupby(["district", "weather_state"]).size().unstack(fill_value=0)
ws_by_dist.plot(kind="bar", ax=axes[1], color=ws_colors[:ws_by_dist.shape[1]],
                edgecolor="white", linewidth=0.8)
axes[1].set_xlabel("District")
axes[1].set_ylabel("Count")
axes[1].set_title("Weather State by District")
axes[1].legend(title="State", labels=[ws_labels.get(c, c) for c in ws_by_dist.columns],
               fontsize=8, loc="upper right")
axes[1].tick_params(axis="x", rotation=0)

plt.tight_layout()
fig.savefig(FIG_DIR / "10_weather_state.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved: 10_weather_state.png")


# ─────────────────────────────────────────────────────────────────────────────
# PRINT SUMMARY STATS
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("KEY CORRELATION WITH recommended_N_kg_ha:")
corrs = df[numeric_cols].corr()["recommended_N_kg_ha"].drop("recommended_N_kg_ha").sort_values()
print(corrs.to_string())

print("\nCLASS DISTRIBUTION BY DISTRICT:")
print(df.groupby(["district", "application_window_class"]).size().unstack(fill_value=0))

print("\nMEAN N RECOMMENDATION BY CROP:")
print(df.groupby("crop_type")["recommended_N_kg_ha"].mean().sort_values(ascending=False).round(1).to_string())
print("="*60)
print(f"\n[OK] EDA complete — all figures saved to: {FIG_DIR}")
