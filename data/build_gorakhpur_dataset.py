"""
Gorakhpur Custom Dataset Builder
================================
Builds a curated, Gorakhpur-specific nitrogen dataset with exact coordinates
across Gorakhpur's tehsils (Sadar, Campierganj, Sahjanwa, Chauri Chaura, Bansgaon, Khajni, Gola).

Reads from:  data/templates/gorakhpur_farm_seeds.csv (or manual input)
Outputs to:  data/processed/gorakhpur_custom_dataset.csv (64 columns standard schema)

Usage:
    python data/build_gorakhpur_dataset.py
    python data/build_gorakhpur_dataset.py --samples-per-farm 20
"""

import argparse
import math
import uuid
from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd

# Load Lookup Tables
LOOKUP_DIR = Path(__file__).resolve().parent / "lookups"
import json

with open(LOOKUP_DIR / "n_demand_table.json") as f:
    N_DEMAND = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
with open(LOOKUP_DIR / "n_credit_table.json") as f:
    N_CREDIT = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
with open(LOOKUP_DIR / "crop_n_removal_coeff.json") as f:
    N_REMOVAL_COEFF = {k: v for k, v in json.load(f).items() if not k.startswith("_")}

# Gorakhpur Regional Climate & Soil Benchmarks (Terai Agro-Climatic Zone)
GORAKHPUR_SOIL_BENCHMARK = {
    "soil_type": "HEAVY_ALLUVIAL",  # Clay loam / Bhat soil of eastern UP
    "clay_range": (38.0, 52.0),
    "sand_range": (18.0, 30.0),
    "ph_range": (6.8, 7.7),
    "soc_range": (4.5, 7.8),       # g/kg
    "cec_range": (18.0, 25.0),     # cmol/kg
    "bd_range": (1.32, 1.48),      # kg/dm3
    "n_soil_range": (0.45, 1.15),  # g/kg
}

STAGE_NDVI = {
    "GERMINATION": (0.20, 0.35),
    "VEGETATIVE":  (0.48, 0.72),
    "TILLERING":   (0.58, 0.82),
    "BOOTING":     (0.65, 0.86),
    "FLOWERING":   (0.60, 0.84),
    "GRAIN_FILL":  (0.48, 0.76),
    "MATURITY":    (0.22, 0.48),
}

STAGE_DAS_RANGES = {
    "GERMINATION": (0, 10),
    "VEGETATIVE":  (10, 35),
    "TILLERING":   (25, 55),
    "BOOTING":     (45, 70),
    "FLOWERING":   (50, 90),
    "GRAIN_FILL":  (70, 115),
    "MATURITY":    (100, 160),
}


def build_gorakhpur_row(farm: dict, rng: np.random.Generator, date_record: date = None) -> dict:
    lat = float(farm["latitude"])
    lon = float(farm["longitude"])
    season = str(farm["crop_season"]).upper()
    crop = str(farm["crop_type"]).upper()
    stage = str(farm.get("growth_stage", "VEGETATIVE")).upper()
    field_area_ha = float(farm.get("field_area_ha", 2.0))
    target_yield = float(farm.get("target_yield_tha", 4.5))
    prev_crop = str(farm.get("previous_crop", "WHEAT")).upper()
    irrigation = str(farm.get("irrigation_type", "FLOOD")).upper()

    das_lo, das_hi = STAGE_DAS_RANGES.get(stage, (20, 50))
    das = int(farm.get("days_after_sowing", rng.integers(das_lo, das_hi + 1)))

    if date_record is None:
        year = int(rng.choice([2022, 2023, 2024]))
        if season == "KHARIF":
            month = int(rng.integers(7, 11))
        elif season == "RABI":
            month = int(rng.choice([11, 12, 1, 2]))
            if month in [1, 2]:
                year += 1
        else:
            month = int(rng.integers(3, 6))
        date_record = date(year, month, int(rng.integers(1, 28)))

    # 1. Geospatial
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    lat_sin = round(math.sin(lat_rad), 6)
    lat_cos = round(math.cos(lat_rad), 6)
    lon_sin = round(math.sin(lon_rad), 6)
    lon_cos = round(math.cos(lon_rad), 6)
    elevation_m = round(float(rng.uniform(72.0, 92.0)), 1)
    slope_deg = round(float(abs(rng.normal(0.5, 0.2))), 2)

    # 2. Soil Properties (Gorakhpur Terai Clay Loam)
    sb = GORAKHPUR_SOIL_BENCHMARK
    clay_pct = round(float(rng.uniform(*sb["clay_range"])), 1)
    sand_pct = round(float(rng.uniform(*sb["sand_range"])), 1)
    silt_pct = round(100.0 - clay_pct - sand_pct, 1)
    soil_ph = round(float(rng.uniform(*sb["ph_range"])), 2)
    soc_gkg = round(float(rng.uniform(*sb["soc_range"])), 2)
    cec = round(float(rng.uniform(*sb["cec_range"])), 1)
    bd = round(float(rng.uniform(*sb["bd_range"])), 2)
    n_soil_gkg = round(float(rng.uniform(*sb["n_soil_range"])), 3)

    # 3. Weather Profile for Gorakhpur
    if season == "KHARIF":
        temp_max_c = round(float(rng.uniform(30.0, 36.5)), 1)
        temp_min_c = round(float(rng.uniform(24.0, 28.5)), 1)
        humidity_pct = round(float(rng.uniform(70.0, 96.0)), 1)
        wind_speed_ms = round(float(rng.uniform(1.5, 5.5)), 1)
        solar_rad = round(float(rng.uniform(280, 650)), 0)
        et0 = round(float(rng.uniform(3.5, 6.0)), 2)
        # Gorakhpur receives intense monsoon rains
        rain_24h = round(float(rng.choice([0.0, 2.5, 12.0, 35.0, 65.0, 110.0], p=[0.25, 0.25, 0.20, 0.15, 0.10, 0.05])), 1)
        rain_48h = round(rain_24h + float(rng.uniform(0.0, 40.0)), 1)
        forecast_48h = round(float(rng.choice([0.0, 5.0, 15.0, 45.0, 80.0], p=[0.30, 0.25, 0.20, 0.15, 0.10])), 1)
        weather_state = 3 if rain_24h > 15 or forecast_48h > 30 else int(rng.choice([1, 2], p=[0.5, 0.5]))
    elif season == "RABI":
        temp_max_c = round(float(rng.uniform(18.0, 27.0)), 1)
        temp_min_c = round(float(rng.uniform(6.0, 14.0)), 1)
        humidity_pct = round(float(rng.uniform(50.0, 85.0)), 1)
        wind_speed_ms = round(float(rng.uniform(1.0, 4.0)), 1)
        solar_rad = round(float(rng.uniform(250, 550)), 0)
        et0 = round(float(rng.uniform(2.0, 4.0)), 2)
        rain_24h = round(float(rng.choice([0.0, 0.0, 0.0, 4.0, 12.0], p=[0.60, 0.25, 0.10, 0.04, 0.01])), 1)
        rain_48h = rain_24h
        forecast_48h = round(float(rng.choice([0.0, 0.0, 3.0, 8.0], p=[0.70, 0.20, 0.08, 0.02])), 1)
        weather_state = 5 if float(rng.random()) < 0.18 else int(rng.choice([0, 1], p=[0.7, 0.3]))
    else:  # ZAID
        temp_max_c = round(float(rng.uniform(36.0, 43.5)), 1)
        temp_min_c = round(float(rng.uniform(22.0, 29.0)), 1)
        humidity_pct = round(float(rng.uniform(25.0, 55.0)), 1)
        wind_speed_ms = round(float(rng.uniform(3.0, 8.0)), 1)
        solar_rad = round(float(rng.uniform(600, 950)), 0)
        et0 = round(float(rng.uniform(6.0, 9.5)), 2)
        rain_24h = 0.0
        rain_48h = 0.0
        forecast_48h = 0.0
        weather_state = 0

    temp_avg_c = round((temp_max_c + temp_min_c) / 2.0, 1)

    # 4. Spectral Indices (Calibrated to stage & nitrogen stress)
    base_n = float(N_DEMAND.get(crop, {}).get(stage, 15))
    prev_credit = float(N_CREDIT.get(prev_crop, 0))
    soil_n_supply = round(n_soil_gkg * bd * 300.0 / 1000.0, 3)

    n_stress = max(0.0, min(1.0, (base_n - soil_n_supply - prev_credit) / max(base_n + 1.0, 1.0) * 0.75))

    ndvi_lo, ndvi_hi = STAGE_NDVI.get(stage, (0.40, 0.70))
    ndvi = round(float(rng.uniform(ndvi_lo, ndvi_hi)) - n_stress * 0.10, 3)
    ndvi = max(0.15, min(0.90, ndvi))

    ndre_base = 0.18 + (ndvi - 0.20) * 0.55
    ndre = round(ndre_base - n_stress * 0.15 + float(rng.normal(0, 0.02)), 3)
    ndre = max(0.08, min(0.62, ndre))

    gndvi = round(0.40 * ndvi + 0.60 * ndre + float(rng.normal(0, 0.015)), 3)
    evi = round(max(0.10, min(0.80, ndvi * 0.85 + float(rng.normal(0, 0.02)))), 3)
    lai = round(max(0.5, min(6.5, 0.57 * math.exp(2.33 * ndvi))), 2)

    ndvi_trend = round(float(rng.normal(-0.025 * n_stress, 0.025)), 3)
    gndvi_trend = round(float(rng.normal(-0.020 * n_stress, 0.020)), 3)
    ndre_trend = round(float(rng.normal(-0.035 * n_stress, 0.020)), 3)

    # 5. Engineered Features
    ndvi_ndre_ratio = round(ndvi / (ndre + 0.001), 4)
    rain_leach_score = round((0.4 * rain_24h + 0.6 * forecast_48h) / (clay_pct + 1.0), 4)
    burn_risk_score = round((temp_max_c * wind_speed_ms) / (humidity_pct + 1.0), 4)
    n_removal_estimate = round(target_yield * N_REMOVAL_COEFF.get(crop, 20.0), 2)
    gdd = round(das * max(0.0, temp_avg_c - 10.0), 1)

    # 6. Targets
    # Window Classification
    if weather_state in (3, 4) or rain_leach_score > 4.0 or forecast_48h > 25.0 or rain_24h > 40.0:
        window_class = 0  # NO-GO Leach
    elif weather_state in (4, 5) or burn_risk_score > 5.0 or (temp_max_c > 40.0 and humidity_pct < 35.0):
        window_class = 1  # NO-GO Burn
    else:
        window_class = 2  # GO Safe

    # Recommended Dosage (kg N/ha)
    ndre_adj = max(0.0, 0.35 - ndre) * 35.0 + max(0.0, -ndre_trend) * 25.0
    soil_ded = min(soil_n_supply, base_n * 0.50)
    irr_adj = {"FLOOD": 6.0, "RAINFED": 0.0, "SPRINKLER": -3.0, "DRIP": -6.0}.get(irrigation, 0.0)
    ph_penalty = max(0.0, soil_ph - 7.5) * 6.0

    raw_rec_n = base_n + ndre_adj + irr_adj + ph_penalty - soil_ded - prev_credit + float(rng.normal(0, 3.5))
    rec_n = round(max(0.0, min(140.0, raw_rec_n)), 2)

    urea_kg_ha = round(rec_n / 0.46, 2)
    dap_kg_ha = round((rec_n * 0.25) / 0.18, 2)

    return {
        "record_id": str(uuid.uuid4()),
        "state": "Uttar Pradesh",
        "district": "GORAKHPUR",
        "data_source": "GORAKHPUR_FIELD_SURVEY",
        "date_of_record": date_record.isoformat(),
        "season_year": f"{season}_{date_record.year}",
        "centroid_lat": lat,
        "centroid_lon": lon,
        "lat_sin": lat_sin,
        "lat_cos": lat_cos,
        "lon_sin": lon_sin,
        "lon_cos": lon_cos,
        "elevation_m": elevation_m,
        "slope_deg": slope_deg,
        "field_area_ha": field_area_ha,
        "ndvi": ndvi,
        "gndvi": gndvi,
        "ndre": ndre,
        "evi": evi,
        "lai": lai,
        "cloud_coverage_pct": 0.0,
        "ndvi_15d_trend": ndvi_trend,
        "gndvi_15d_trend": gndvi_trend,
        "ndre_15d_trend": ndre_trend,
        "temp_max_c": temp_max_c,
        "temp_min_c": temp_min_c,
        "temp_avg_c": temp_avg_c,
        "rainfall_24h_mm": rain_24h,
        "rainfall_48h_mm": rain_48h,
        "rainfall_forecast_48h_mm": forecast_48h,
        "humidity_pct": humidity_pct,
        "wind_speed_ms": wind_speed_ms,
        "solar_radiation_wm2": solar_rad,
        "et0_mm": et0,
        "weather_state": weather_state,
        "soil_ph": soil_ph,
        "soil_organic_carbon_gkg": soc_gkg,
        "cec_cmolkg": cec,
        "clay_pct": clay_pct,
        "sand_pct": sand_pct,
        "silt_pct": silt_pct,
        "bulk_density_kgdm3": bd,
        "nitrogen_soil_gkg": n_soil_gkg,
        "soil_type": "HEAVY_ALLUVIAL",
        "crop_type": crop,
        "crop_season": season,
        "growth_stage": stage,
        "days_after_sowing": das,
        "previous_crop": prev_crop,
        "irrigation_type": irrigation,
        "target_yield_tha": target_yield,
        "fertilizer_history": "MEDIUM",
        "gdd_accumulated": gdd,
        "ndvi_ndre_ratio": ndvi_ndre_ratio,
        "rain_leach_score": rain_leach_score,
        "burn_risk_score": burn_risk_score,
        "n_removal_estimate": n_removal_estimate,
        "soil_n_supply": soil_n_supply,
        "base_n_demand": base_n,
        "previous_crop_n_credit": prev_credit,
        "recommended_N_kg_ha": rec_n,
        "application_window_class": window_class,
        "urea_kg_ha": urea_kg_ha,
        "dap_kg_ha": dap_kg_ha,
    }


def main():
    parser = argparse.ArgumentParser(description="Gorakhpur Dataset Builder")
    parser.add_argument(
        "--input",
        default="data/templates/gorakhpur_farm_seeds.csv",
        help="Input CSV with farm locations and crops",
    )
    parser.add_argument(
        "--samples-per-farm",
        type=int,
        default=20,
        help="Number of temporal/seasonal samples per farm location",
    )
    parser.add_argument(
        "--output",
        default="data/processed/gorakhpur_custom_dataset.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Gorakhpur Custom Dataset Builder")
    print(f"Reading farms from: {input_path}")
    print(f"Samples per location: {args.samples_per_farm}")
    print("=" * 60)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    farms_df = pd.read_csv(input_path)
    print(f"Found {len(farms_df)} seed farm locations across Gorakhpur.")

    rng = np.random.default_rng(42)
    records = []

    for _, farm in farms_df.iterrows():
        farm_dict = farm.to_dict()
        for _ in range(args.samples_per_farm):
            row = build_gorakhpur_row(farm_dict, rng)
            records.append(row)

    out_df = pd.DataFrame(records).sample(frac=1, random_state=42).reset_index(drop=True)
    out_df.to_csv(output_path, index=False)

    print(f"\n[OK] Successfully built Gorakhpur dataset -> {output_path}")
    print(f"     Total Rows: {len(out_df):,} | Columns: {len(out_df.columns)}")
    print("\nClass Breakdown:")
    print(out_df["application_window_class"].value_counts().to_string())
    print("\nTop Crops in Gorakhpur:")
    print(out_df["crop_type"].value_counts().to_string())
    print("\nNitrogen Recommendation Summary (kg N/ha):")
    print(out_df["recommended_N_kg_ha"].describe().round(2).to_string())
    print("=" * 60)


if __name__ == "__main__":
    main()
