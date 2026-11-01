"""
GeoN-DSS Synthetic Dataset Generator
=====================================
Generates ~15,000 physics-informed synthetic records for Uttar Pradesh.
Districts: Lucknow, Kanpur, Amethi, Gorakhpur

Output: data/synthetic/up_nitrogen_dataset.csv  (64 columns)

Usage:
    cd data
    python generate_dataset.py

Requirements:
    pip install pandas numpy
"""

import math
import random
import uuid
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# 1. DISTRICT PROFILES
# ─────────────────────────────────────────────────────────────────────────────

DISTRICTS = {
    "LUCKNOW": {
        "lat_range": (26.70, 27.00),
        "lon_range": (80.75, 81.15),
        "elevation_range": (95.0, 120.0),
        "season_weights": [0.40, 0.50, 0.10],   # KHARIF, RABI, ZAID
        "crop_season_map": {
            "KHARIF": ["RICE", "SUGARCANE", "SOYBEAN", "MAIZE"],
            "RABI":   ["WHEAT", "MUSTARD", "POTATO", "ONION", "LENTIL"],
            "ZAID":   ["MOONG", "WATERMELON"],
        },
        "soil_profiles": [
            {   # Khadar — loamy alluvial
                "soil_type": "MEDIUM_ALLUVIAL",
                "clay": (22, 35), "sand": (35, 55),
                "ph": (7.2, 8.0), "soc": (3.0, 7.0),
                "cec": (12, 20), "bd": (1.40, 1.60),
                "n_soil": (0.30, 1.00), "weight": 0.70,
            },
            {   # Bhangar — sandy loam
                "soil_type": "LIGHT_ALLUVIAL",
                "clay": (15, 22), "sand": (50, 65),
                "ph": (7.0, 7.8), "soc": (2.0, 5.0),
                "cec": (8, 14),  "bd": (1.45, 1.65),
                "n_soil": (0.20, 0.70), "weight": 0.30,
            },
        ],
    },
    "KANPUR": {
        "lat_range": (26.25, 26.65),
        "lon_range": (80.10, 80.55),
        "elevation_range": (110.0, 130.0),
        "season_weights": [0.35, 0.55, 0.10],
        "crop_season_map": {
            "KHARIF": ["RICE", "MAIZE", "BAJRA", "SOYBEAN"],
            "RABI":   ["WHEAT", "MUSTARD", "POTATO", "CHICKPEA", "ONION"],
            "ZAID":   ["MOONG", "WATERMELON"],
        },
        "soil_profiles": [
            {   # Sandier western alluvial
                "soil_type": "LIGHT_ALLUVIAL",
                "clay": (15, 25), "sand": (50, 65),
                "ph": (7.3, 8.3), "soc": (2.0, 5.5),
                "cec": (8, 15),  "bd": (1.45, 1.65),
                "n_soil": (0.20, 0.80), "weight": 0.60,
            },
            {   # Medium loamy strip
                "soil_type": "MEDIUM_ALLUVIAL",
                "clay": (22, 35), "sand": (35, 52),
                "ph": (7.2, 8.0), "soc": (3.0, 6.5),
                "cec": (12, 20), "bd": (1.40, 1.60),
                "n_soil": (0.30, 1.00), "weight": 0.40,
            },
        ],
    },
    "AMETHI": {
        "lat_range": (25.90, 26.40),
        "lon_range": (81.55, 82.10),
        "elevation_range": (85.0, 115.0),
        "season_weights": [0.45, 0.45, 0.10],
        "crop_season_map": {
            "KHARIF": ["RICE", "SUGARCANE", "ARHAR", "MAIZE", "SOYBEAN"],
            "RABI":   ["WHEAT", "MUSTARD", "LENTIL", "CHICKPEA", "ONION"],
            "ZAID":   ["MOONG", "WATERMELON", "FODDER_MAIZE"],
        },
        "soil_profiles": [
            {   "soil_type": "MEDIUM_ALLUVIAL",
                "clay": (25, 38), "sand": (30, 50),
                "ph": (7.2, 8.0), "soc": (3.5, 7.5),
                "cec": (13, 22), "bd": (1.38, 1.58),
                "n_soil": (0.40, 1.10), "weight": 0.50 },
            {   "soil_type": "HEAVY_ALLUVIAL",
                "clay": (35, 50), "sand": (20, 35),
                "ph": (7.0, 7.8), "soc": (4.0, 8.0),
                "cec": (18, 25), "bd": (1.35, 1.55),
                "n_soil": (0.50, 1.20), "weight": 0.30 },
            {   "soil_type": "LIGHT_ALLUVIAL",
                "clay": (15, 25), "sand": (50, 62),
                "ph": (7.3, 8.2), "soc": (2.5, 5.5),
                "cec": (9, 16),  "bd": (1.43, 1.63),
                "n_soil": (0.20, 0.80), "weight": 0.20 },
        ],
    },
    "GORAKHPUR": {
        "lat_range": (26.55, 26.95),
        "lon_range": (83.10, 83.65),
        "elevation_range": (70.0, 100.0),
        "season_weights": [0.60, 0.35, 0.05],
        "crop_season_map": {
            "KHARIF": ["RICE", "SUGARCANE", "ARHAR", "MAIZE", "BAJRA"],
            "RABI":   ["WHEAT", "MUSTARD", "LENTIL", "CHICKPEA"],
            "ZAID":   ["MOONG", "FODDER_MAIZE"],
        },
        "soil_profiles": [
            {   "soil_type": "HEAVY_ALLUVIAL",
                "clay": (40, 55), "sand": (18, 30),
                "ph": (6.8, 7.8), "soc": (5.0, 8.0),
                "cec": (18, 25), "bd": (1.33, 1.52),
                "n_soil": (0.50, 1.20), "weight": 0.60 },
            {   "soil_type": "MEDIUM_ALLUVIAL",
                "clay": (28, 42), "sand": (25, 40),
                "ph": (7.0, 7.8), "soc": (4.0, 7.5),
                "cec": (15, 22), "bd": (1.37, 1.55),
                "n_soil": (0.40, 1.00), "weight": 0.40 },
        ],
    },
}

SEASONS = ["KHARIF", "RABI", "ZAID"]

# ─────────────────────────────────────────────────────────────────────────────
# 2. CROP & STAGE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

CEREAL_STAGES  = ["GERMINATION", "VEGETATIVE", "TILLERING", "BOOTING",
                  "FLOWERING", "GRAIN_FILL", "MATURITY"]
GENERAL_STAGES = ["GERMINATION", "VEGETATIVE", "FLOWERING", "GRAIN_FILL", "MATURITY"]
LEGUME_STAGES  = ["GERMINATION", "VEGETATIVE", "FLOWERING", "MATURITY"]

CROP_STAGES = {
    "WHEAT": CEREAL_STAGES,  "RICE": CEREAL_STAGES,
    "MAIZE": CEREAL_STAGES,  "BAJRA": CEREAL_STAGES,
    "SUGARCANE": GENERAL_STAGES, "POTATO": GENERAL_STAGES,
    "ONION": GENERAL_STAGES, "MUSTARD": GENERAL_STAGES,
    "WATERMELON": GENERAL_STAGES, "FODDER_MAIZE": GENERAL_STAGES,
    "ARHAR": LEGUME_STAGES,  "SOYBEAN": LEGUME_STAGES,
    "CHICKPEA": LEGUME_STAGES, "LENTIL": LEGUME_STAGES,
    "MOONG": LEGUME_STAGES,
}

STAGE_DAS = {
    "GERMINATION": (0,  10), "VEGETATIVE": (10, 35),
    "TILLERING":  (25, 55), "BOOTING":   (45, 70),
    "FLOWERING":  (50, 90), "GRAIN_FILL": (70, 120), "MATURITY": (100, 180),
}

# NDVI typical range per growth stage (for crop pixels)
STAGE_NDVI = {
    "GERMINATION": (0.20, 0.35), "VEGETATIVE":  (0.45, 0.75),
    "TILLERING":   (0.55, 0.80), "BOOTING":     (0.60, 0.85),
    "FLOWERING":   (0.55, 0.82), "GRAIN_FILL":  (0.45, 0.78),
    "MATURITY":    (0.20, 0.50),
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. AGRONOMIC LOOKUP TABLES
# ─────────────────────────────────────────────────────────────────────────────

N_DEMAND = {
    "WHEAT":       {"GERMINATION": 20, "VEGETATIVE": 50, "TILLERING": 70,
                    "BOOTING": 80, "FLOWERING": 25, "GRAIN_FILL":  5, "MATURITY": 0},
    "RICE":        {"GERMINATION": 10, "VEGETATIVE": 30, "TILLERING": 55,
                    "BOOTING": 65, "FLOWERING": 25, "GRAIN_FILL": 10, "MATURITY": 0},
    "MAIZE":       {"GERMINATION": 20, "VEGETATIVE": 55, "TILLERING": 75,
                    "BOOTING": 85, "FLOWERING": 35, "GRAIN_FILL": 15, "MATURITY": 0},
    "BAJRA":       {"GERMINATION": 15, "VEGETATIVE": 40, "TILLERING": 55,
                    "BOOTING": 60, "FLOWERING": 25, "GRAIN_FILL": 10, "MATURITY": 0},
    "SUGARCANE":   {"GERMINATION": 25, "VEGETATIVE": 70, "FLOWERING": 80,
                    "GRAIN_FILL": 55, "MATURITY": 15},
    "POTATO":      {"GERMINATION": 15, "VEGETATIVE": 60, "FLOWERING": 55,
                    "GRAIN_FILL": 25, "MATURITY":  0},
    "ONION":       {"GERMINATION":  5, "VEGETATIVE": 30, "FLOWERING": 40,
                    "GRAIN_FILL": 20, "MATURITY":  0},
    "MUSTARD":     {"GERMINATION": 10, "VEGETATIVE": 35, "FLOWERING": 45,
                    "GRAIN_FILL": 20, "MATURITY":  0},
    "WATERMELON":  {"GERMINATION":  5, "VEGETATIVE": 20, "FLOWERING": 25,
                    "GRAIN_FILL": 15, "MATURITY":  0},
    "FODDER_MAIZE":{"GERMINATION": 15, "VEGETATIVE": 50, "FLOWERING": 35,
                    "GRAIN_FILL": 30, "MATURITY":  0},
    "ARHAR":       {"GERMINATION":  0, "VEGETATIVE":  5, "FLOWERING": 10, "MATURITY": 0},
    "SOYBEAN":     {"GERMINATION":  0, "VEGETATIVE":  5, "FLOWERING": 10, "MATURITY": 0},
    "CHICKPEA":    {"GERMINATION":  0, "VEGETATIVE":  5, "FLOWERING": 10, "MATURITY": 0},
    "LENTIL":      {"GERMINATION":  0, "VEGETATIVE":  5, "FLOWERING":  8, "MATURITY": 0},
    "MOONG":       {"GERMINATION":  0, "VEGETATIVE":  5, "FLOWERING":  8, "MATURITY": 0},
}

N_CREDIT = {
    "ARHAR": 35, "SOYBEAN": 30, "CHICKPEA": 25, "LENTIL": 20, "MOONG": 20,
    "LEGUME_GENERIC": 25, "FALLOW": 10,
    "WHEAT": 0, "RICE": 0, "MAIZE": 0, "BAJRA": 0, "SUGARCANE": 0,
    "POTATO": 0, "ONION": 0, "MUSTARD": 0, "WATERMELON": 0, "FODDER_MAIZE": 0,
}

N_REMOVAL_COEFF = {
    "WHEAT": 25.0, "RICE": 18.0, "MAIZE": 22.0, "BAJRA": 18.0,
    "SUGARCANE": 1.2, "POTATO": 3.5, "ONION": 2.8, "MUSTARD": 30.0,
    "WATERMELON": 1.5, "FODDER_MAIZE": 4.0,
    "ARHAR": 35.0, "SOYBEAN": 40.0, "CHICKPEA": 35.0, "LENTIL": 30.0, "MOONG": 30.0,
}

YIELD_RANGES = {
    "WHEAT": (3.5, 6.0), "RICE": (3.0, 6.5), "MAIZE": (3.0, 6.0),
    "BAJRA": (1.5, 3.0), "SUGARCANE": (60, 90), "POTATO": (15, 30),
    "ONION": (15, 25),  "MUSTARD": (1.0, 2.0), "WATERMELON": (20, 35),
    "FODDER_MAIZE": (30, 50), "ARHAR": (1.0, 2.5), "SOYBEAN": (1.5, 2.5),
    "CHICKPEA": (0.8, 1.5), "LENTIL": (0.8, 1.2), "MOONG": (0.8, 1.5),
}

IRRIGATION_TYPES   = ["FLOOD", "SPRINKLER", "DRIP", "RAINFED"]
IRRIGATION_WEIGHTS = [0.55, 0.20, 0.10, 0.15]   # UP: flood dominant
FERTILIZER_HISTORY = ["NONE", "LOW", "MEDIUM", "HIGH"]
FERTILIZER_WEIGHTS = [0.10, 0.25, 0.40, 0.25]
PREVIOUS_CROPS     = list(N_CREDIT.keys())

# ─────────────────────────────────────────────────────────────────────────────
# 4. SEASON-WISE WEATHER PROFILES (UP climate)
# ─────────────────────────────────────────────────────────────────────────────

# Rain bin edges (mm) — index i → rain in [RAIN_BINS[i], RAIN_BINS[i+1]]
RAIN_BINS = [0, 2, 10, 30, 80, 120, 160]

SEASON_WEATHER = {
    "KHARIF": {
        "temp_max": (28, 42), "temp_min": (22, 32),
        "humidity": (60, 98), "wind_speed": (0, 8),
        "solar_rad": (200, 800), "et0": (3.0, 7.0),
        # probability of landing in each rain bin
        "rain_bin_probs": [0.30, 0.25, 0.20, 0.12, 0.08, 0.05],
        # P(weather_state) for SUNNY→PARTLY_CLOUDY→OVERCAST→RAIN→THUNDER→FOG
        "ws_probs": [0.20, 0.20, 0.15, 0.25, 0.15, 0.05],
    },
    "RABI": {
        "temp_max": (12, 28), "temp_min": (2, 18),
        "humidity": (40, 85), "wind_speed": (0, 10),
        "solar_rad": (100, 700), "et0": (1.5, 5.5),
        "rain_bin_probs": [0.55, 0.20, 0.12, 0.07, 0.04, 0.02],
        "ws_probs": [0.35, 0.20, 0.20, 0.10, 0.05, 0.10],
    },
    "ZAID": {
        "temp_max": (35, 46), "temp_min": (20, 32),
        "humidity": (20, 55), "wind_speed": (2, 14),
        "solar_rad": (500, 1000), "et0": (5.0, 10.0),
        "rain_bin_probs": [0.65, 0.15, 0.10, 0.05, 0.03, 0.02],
        "ws_probs": [0.50, 0.20, 0.10, 0.08, 0.10, 0.02],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 5. HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _sample_rainfall(rng: np.random.Generator, season: str) -> float:
    probs = SEASON_WEATHER[season]["rain_bin_probs"]
    bin_i = rng.choice(len(probs), p=probs)
    return round(float(rng.uniform(RAIN_BINS[bin_i], RAIN_BINS[bin_i + 1])), 1)


def _sample_weather_state(rng: np.random.Generator, season: str,
                           rain_24h: float, forecast_48h: float) -> int:
    """Override weather state if rainfall is high."""
    if rain_24h > 30 or forecast_48h > 40:
        return int(rng.choice([3, 4], p=[0.70, 0.30]))
    probs = SEASON_WEATHER[season]["ws_probs"]
    return int(rng.choice(6, p=probs))


def _generate_spectral_indices(rng: np.random.Generator,
                                growth_stage: str, n_stress: float):
    """
    Generate correlated spectral indices.
    n_stress ∈ [0, 1] — higher stress → lower NDRE/GNDVI, negative trends.
    """
    ndvi_lo, ndvi_hi = STAGE_NDVI.get(growth_stage, (0.30, 0.65))
    ndvi = float(rng.uniform(ndvi_lo, ndvi_hi)) - n_stress * 0.12
    ndvi = round(max(0.15, min(0.92, ndvi)), 3)

    # NDRE is most N-sensitive
    ndre_base = 0.18 + (ndvi - 0.20) * 0.55
    ndre = ndre_base - n_stress * 0.16 + float(rng.normal(0, 0.02))
    ndre = round(max(0.05, min(0.65, ndre)), 3)

    # GNDVI — intermediate sensitivity
    gndvi = 0.40 * ndvi + 0.60 * ndre + float(rng.normal(0, 0.015))
    gndvi = round(max(0.10, min(0.85, gndvi)), 3)

    evi  = round(max(0.05, min(0.85, ndvi * 0.85 + float(rng.normal(0, 0.02)))), 3)
    lai  = round(max(0.30, min(7.50, 0.57 * math.exp(2.33 * ndvi) + float(rng.normal(0, 0.1)))), 2)

    cloud_choices  = [0, 5, 10, 20, 35, 50, 75]
    cloud_p        = [0.45, 0.20, 0.15, 0.10, 0.05, 0.03, 0.02]
    cloud_pct      = float(rng.choice(cloud_choices, p=cloud_p))

    ndvi_trend  = round(float(rng.normal(-0.030 * n_stress, 0.030)), 3)
    gndvi_trend = round(float(rng.normal(-0.025 * n_stress, 0.025)), 3)
    ndre_trend  = round(float(rng.normal(-0.040 * n_stress, 0.020)), 3)

    return ndvi, gndvi, ndre, evi, lai, cloud_pct, ndvi_trend, gndvi_trend, ndre_trend


def _compute_n_recommendation(base_n: float, ndre: float, ndre_trend: float,
                               soil_n_supply: float, prev_credit: float,
                               target_yield: float, crop: str,
                               irrigation: str, soil_ph: float,
                               et0: float, rng: np.random.Generator) -> float:
    """
    Physics-informed N recommendation formula (kg N/ha).

    Components:
      + base ICAR demand (crop × stage)
      + NDRE stress correction (low/declining NDRE → more N)
      + yield demand adjustment
      + irrigation efficiency correction
      + soil pH penalty (alkaline soils reduce N availability)
      + ET₀ driven uptake demand
      − soil N supply (top 30 cm)
      − previous crop N credit
      ± Gaussian noise (±4.5 kg/ha)
    """
    # NDRE stress: deficit below 0.35 optimal threshold
    ndre_adj = max(0.0, 0.35 - ndre) * 35.0 + max(0.0, -ndre_trend) * 25.0

    # Deduct available soil N (capped at 50% of base demand to avoid negatives)
    soil_ded = min(soil_n_supply, base_n * 0.50)

    # Yield adjustment: ±12 kg/ha per unit above/below average yield
    ymin, ymax = YIELD_RANGES.get(crop, (1.0, 5.0))
    yield_avg  = (ymin + ymax) / 2.0
    yield_adj  = (target_yield - yield_avg) / max(yield_avg, 1.0) * 12.0

    # Irrigation efficiency (flood wastes N via runoff; drip is efficient)
    irr_adj = {"FLOOD": 8.0, "RAINFED": 2.0, "SPRINKLER": -3.0, "DRIP": -6.0}
    irr_correction = irr_adj.get(irrigation, 0.0)

    # pH penalty: UP soils are 7.0–8.5; above 7.5 locks up N
    ph_penalty = max(0.0, soil_ph - 7.5) * 7.0

    # High ET₀ → higher crop N uptake demand
    et0_adj = max(0.0, et0 - 4.0) * 1.5

    total = (base_n + ndre_adj + yield_adj + irr_correction
             + ph_penalty + et0_adj - soil_ded - prev_credit)

    noise = float(rng.normal(0, 4.5))
    return round(max(0.0, min(150.0, total + noise)), 2)


def _classify_window(weather_state: int, rain_24h: float, forecast_48h: float,
                     temp_max: float, humidity: float,
                     rain_leach_score: float, burn_risk_score: float) -> int:
    """
    Rule-based application window classification.
    0 = NO-GO Leaching | 1 = NO-GO Burn | 2 = GO Safe
    """
    if (weather_state in (3, 4) or rain_leach_score > 4.0
            or forecast_48h > 25.0 or rain_24h > 40.0):
        return 0
    if (weather_state in (4, 5) or burn_risk_score > 5.0
            or (temp_max > 40.0 and humidity < 35.0)):
        return 1
    return 2


def _random_date(rng: np.random.Generator, season: str) -> date:
    year = int(rng.choice(range(2020, 2025)))
    if season == "KHARIF":
        month = int(rng.integers(6, 12))
    elif season == "RABI":
        month = int(rng.choice([10, 11, 12, 1, 2, 3]))
        if month in (1, 2, 3):
            year += 1
    else:  # ZAID
        month = int(rng.integers(3, 7))
    day = int(rng.integers(1, 29))
    try:
        return date(year, month, day)
    except ValueError:
        return date(year, month, 15)


# ─────────────────────────────────────────────────────────────────────────────
# 6. SINGLE-RECORD GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_record(district: str, d_info: dict, rng: np.random.Generator) -> dict:

    # ── Season & Crop ─────────────────────────────────────────────────────
    season = str(rng.choice(SEASONS, p=d_info["season_weights"]))
    crop   = str(rng.choice(d_info["crop_season_map"][season]))

    stages         = CROP_STAGES[crop]
    growth_stage   = str(rng.choice(stages))
    das_lo, das_hi = STAGE_DAS[growth_stage]
    days_after_sowing = int(rng.integers(das_lo, das_hi + 1))

    previous_crop     = str(rng.choice(PREVIOUS_CROPS))
    irrigation_type   = str(rng.choice(IRRIGATION_TYPES, p=IRRIGATION_WEIGHTS))
    fertilizer_history = str(rng.choice(FERTILIZER_HISTORY, p=FERTILIZER_WEIGHTS))
    ymin, ymax        = YIELD_RANGES[crop]
    target_yield_tha  = round(float(rng.uniform(ymin, ymax)), 2)

    # ── Geospatial ────────────────────────────────────────────────────────
    lat          = round(float(rng.uniform(*d_info["lat_range"])), 5)
    lon          = round(float(rng.uniform(*d_info["lon_range"])), 5)
    elevation_m  = round(float(rng.uniform(*d_info["elevation_range"])), 1)
    slope_deg    = round(min(float(abs(rng.normal(0.8, 0.5))), 3.0), 2)
    field_area_ha = round(float(rng.uniform(0.5, 18.0)), 2)

    lat_sin = round(math.sin(math.radians(lat)), 6)
    lat_cos = round(math.cos(math.radians(lat)), 6)
    lon_sin = round(math.sin(math.radians(lon)), 6)
    lon_cos = round(math.cos(math.radians(lon)), 6)

    # ── Soil ──────────────────────────────────────────────────────────────
    profiles = d_info["soil_profiles"]
    weights  = [p["weight"] for p in profiles]
    total_w  = sum(weights)
    weights  = [w / total_w for w in weights]
    sp       = profiles[int(rng.choice(len(profiles), p=weights))]

    soil_type               = sp["soil_type"]
    clay_pct                = round(float(rng.uniform(*sp["clay"])), 1)
    sand_raw                = float(rng.uniform(*sp["sand"]))
    sand_pct                = round(min(sand_raw, 98.0 - clay_pct), 1)
    silt_pct                = round(100.0 - clay_pct - sand_pct, 1)
    soil_ph                 = round(float(rng.uniform(*sp["ph"])), 2)
    soil_organic_carbon_gkg = round(float(rng.uniform(*sp["soc"])), 2)
    cec_cmolkg              = round(float(rng.uniform(*sp["cec"])), 1)
    bulk_density_kgdm3      = round(float(rng.uniform(*sp["bd"])), 2)
    nitrogen_soil_gkg       = round(float(rng.uniform(*sp["n_soil"])), 3)

    # ── Weather ───────────────────────────────────────────────────────────
    sw          = SEASON_WEATHER[season]
    temp_max_c  = round(float(rng.uniform(*sw["temp_max"])), 1)
    temp_min_c  = round(float(rng.uniform(*sw["temp_min"])), 1)
    if temp_min_c >= temp_max_c:
        temp_min_c = round(temp_max_c - 3.0, 1)
    temp_avg_c       = round((temp_max_c + temp_min_c) / 2.0 + float(rng.normal(0, 0.5)), 1)
    humidity_pct     = round(float(rng.uniform(*sw["humidity"])), 1)
    wind_speed_ms    = round(float(rng.uniform(*sw["wind_speed"])), 1)
    solar_radiation_wm2 = round(float(rng.uniform(*sw["solar_rad"])), 0)
    et0_mm           = round(float(rng.uniform(*sw["et0"])), 2)

    rain_24h_mm       = _sample_rainfall(rng, season)
    rain_48h_mm       = round(rain_24h_mm + _sample_rainfall(rng, season) * float(rng.uniform(0, 1)), 1)
    forecast_48h_mm   = _sample_rainfall(rng, season)

    # Gorakhpur receives 40–80% more rain in Kharif (Terai climate influence)
    if district == "GORAKHPUR" and season == "KHARIF":
        multiplier      = float(rng.uniform(1.4, 1.8))
        rain_24h_mm     = round(rain_24h_mm * multiplier, 1)
        rain_48h_mm     = round(rain_48h_mm * multiplier, 1)
        forecast_48h_mm = round(forecast_48h_mm * float(rng.uniform(1.3, 1.6)), 1)

    weather_state = _sample_weather_state(rng, season, rain_24h_mm, forecast_48h_mm)
    # Dense fog in Rabi (Dec–Jan) — ~12% chance
    if season == "RABI" and float(rng.random()) < 0.12:
        weather_state = 5

    # ── GDD ──────────────────────────────────────────────────────────────
    gdd_accumulated = round(max(0.0, days_after_sowing * max(0.0, temp_avg_c - 10.0)), 1)

    # ── N Stress Level → drives spectral index values ─────────────────────
    base_n       = float(N_DEMAND.get(crop, {}).get(growth_stage, 10))
    soil_n_supply = round(nitrogen_soil_gkg * bulk_density_kgdm3 * 300.0 / 1000.0, 2)
    prev_credit  = float(N_CREDIT.get(previous_crop, 0))

    n_stress = max(0.0, min(1.0,
        (base_n - soil_n_supply - prev_credit) / max(base_n + 1.0, 1.0) * 0.8
    ))
    fh_discount = {"NONE": 0.0, "LOW": -0.05, "MEDIUM": -0.15, "HIGH": -0.25}
    n_stress = max(0.0, n_stress + fh_discount[fertilizer_history])

    # ── Spectral Indices ──────────────────────────────────────────────────
    (ndvi, gndvi, ndre, evi, lai, cloud_pct,
     ndvi_trend, gndvi_trend, ndre_trend) = _generate_spectral_indices(rng, growth_stage, n_stress)

    # ── Engineered Features ───────────────────────────────────────────────
    ndvi_ndre_ratio    = round(ndvi / (ndre + 0.001), 4)
    rain_leach_score   = round((0.4 * rain_24h_mm + 0.6 * forecast_48h_mm) / (clay_pct + 1.0), 4)
    burn_risk_score    = round((temp_max_c * wind_speed_ms) / (humidity_pct + 1.0), 4)
    n_removal_estimate = round(target_yield_tha * N_REMOVAL_COEFF.get(crop, 20.0), 2)

    # ── Target: Recommended N ─────────────────────────────────────────────
    recommended_N = _compute_n_recommendation(
        base_n, ndre, ndre_trend, soil_n_supply, prev_credit,
        target_yield_tha, crop, irrigation_type, soil_ph, et0_mm, rng
    )

    # ── Target: Application Window Class ─────────────────────────────────
    window_class = _classify_window(
        weather_state, rain_24h_mm, forecast_48h_mm,
        temp_max_c, humidity_pct, rain_leach_score, burn_risk_score
    )

    # ── Output Conversions ────────────────────────────────────────────────
    urea_kg_ha = round(recommended_N / 0.46, 2)     # Urea = 46% N
    dap_kg_ha  = round(recommended_N * 0.25 / 0.18, 2)  # 25% N from DAP @ 18% N

    # ── Date & Season Year ────────────────────────────────────────────────
    record_date = _random_date(rng, season)
    season_year = f"{season}_{record_date.year}"

    return {
        # ── Identifiers
        "record_id":            str(uuid.uuid4()),
        "state":                "Uttar Pradesh",
        "district":             district,
        "data_source":          "SYNTHETIC",
        "date_of_record":       record_date.isoformat(),
        "season_year":          season_year,
        # ── Geospatial
        "centroid_lat":         lat,
        "centroid_lon":         lon,
        "lat_sin":              lat_sin,
        "lat_cos":              lat_cos,
        "lon_sin":              lon_sin,
        "lon_cos":              lon_cos,
        "elevation_m":          elevation_m,
        "slope_deg":            slope_deg,
        "field_area_ha":        field_area_ha,
        # ── Spectral
        "ndvi":                 ndvi,
        "gndvi":                gndvi,
        "ndre":                 ndre,
        "evi":                  evi,
        "lai":                  lai,
        "cloud_coverage_pct":   cloud_pct,
        "ndvi_15d_trend":       ndvi_trend,
        "gndvi_15d_trend":      gndvi_trend,
        "ndre_15d_trend":       ndre_trend,
        # ── Meteorological
        "temp_max_c":           temp_max_c,
        "temp_min_c":           temp_min_c,
        "temp_avg_c":           temp_avg_c,
        "rainfall_24h_mm":      rain_24h_mm,
        "rainfall_48h_mm":      rain_48h_mm,
        "rainfall_forecast_48h_mm": forecast_48h_mm,
        "humidity_pct":         humidity_pct,
        "wind_speed_ms":        wind_speed_ms,
        "solar_radiation_wm2":  solar_radiation_wm2,
        "et0_mm":               et0_mm,
        "weather_state":        weather_state,
        # ── Soil
        "soil_ph":              soil_ph,
        "soil_organic_carbon_gkg": soil_organic_carbon_gkg,
        "cec_cmolkg":           cec_cmolkg,
        "clay_pct":             clay_pct,
        "sand_pct":             sand_pct,
        "silt_pct":             silt_pct,
        "bulk_density_kgdm3":   bulk_density_kgdm3,
        "nitrogen_soil_gkg":    nitrogen_soil_gkg,
        "soil_type":            soil_type,
        # ── Agronomic
        "crop_type":            crop,
        "crop_season":          season,
        "growth_stage":         growth_stage,
        "days_after_sowing":    days_after_sowing,
        "previous_crop":        previous_crop,
        "irrigation_type":      irrigation_type,
        "target_yield_tha":     target_yield_tha,
        "fertilizer_history":   fertilizer_history,
        "gdd_accumulated":      gdd_accumulated,
        # ── Engineered
        "ndvi_ndre_ratio":         ndvi_ndre_ratio,
        "rain_leach_score":        rain_leach_score,
        "burn_risk_score":         burn_risk_score,
        "n_removal_estimate":      n_removal_estimate,
        "soil_n_supply":           soil_n_supply,
        "base_n_demand":           base_n,
        "previous_crop_n_credit":  prev_credit,
        # ── Targets
        "recommended_N_kg_ha":         recommended_N,
        "application_window_class":    window_class,
        # ── Outputs (post-model)
        "urea_kg_ha":  urea_kg_ha,
        "dap_kg_ha":   dap_kg_ha,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 7. MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    TOTAL   = 15_000
    PER_DIS = TOTAL // len(DISTRICTS)
    SEED    = 42
    rng     = np.random.default_rng(SEED)

    records = []
    for district, info in DISTRICTS.items():
        print(f"  [{district}]  generating {PER_DIS} records ...")
        for _ in range(PER_DIS):
            records.append(generate_record(district, info, rng))

    df = pd.DataFrame(records).sample(frac=1, random_state=SEED).reset_index(drop=True)

    out_dir  = Path(__file__).parent / "synthetic"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "up_nitrogen_dataset.csv"
    df.to_csv(out_path, index=False)

    # ── Summary ───────────────────────────────────────────────────────────
    cls_map  = {0: "NO-GO Leach", 1: "NO-GO Burn", 2: "GO Safe"}
    print(f"\n{'='*60}")
    print(f"[OK] Dataset saved -> {out_path}")
    print(f"     Rows: {len(df):,}   Columns: {len(df.columns)}")
    print(f"\n[CLASS DISTRIBUTION]")
    for k, label in cls_map.items():
        n = (df["application_window_class"] == k).sum()
        print(f"  {label:<16} {n:>5,}  ({n/len(df)*100:.1f}%)")
    print(f"\n[TOP CROPS]")
    print(df["crop_type"].value_counts().head(8).to_string())
    print(f"\n[DISTRICT DISTRIBUTION]")
    print(df["district"].value_counts().to_string())
    print(f"\n[N RECOMMENDATION STATS kg/ha]")
    print(df["recommended_N_kg_ha"].describe().round(2).to_string())
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("  GeoN-DSS Synthetic Dataset Generator")
    print("  State: Uttar Pradesh | 4 Districts")
    print("  Target: 15,000 records x 64 columns")
    print("=" * 60 + "\n")
    main()
