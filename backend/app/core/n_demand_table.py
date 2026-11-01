"""
ICAR N-demand lookup tables loaded from data/lookups/*.json
Used by the feature engineering pipeline and the synthetic dataset generator.
"""

import json
from pathlib import Path

_LOOKUP_DIR = Path(__file__).resolve().parents[3] / "data" / "lookups"


def _load(filename: str) -> dict:
    with open(_LOOKUP_DIR / filename, "r") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


N_DEMAND_TABLE: dict       = _load("n_demand_table.json")
N_CREDIT_TABLE: dict       = _load("n_credit_table.json")
N_REMOVAL_COEFF: dict      = _load("crop_n_removal_coeff.json")


def get_base_n_demand(crop_type: str, growth_stage: str) -> float:
    """Return ICAR baseline N demand (kg/ha) for a crop at a given growth stage."""
    crop_data = N_DEMAND_TABLE.get(crop_type, {})
    return float(crop_data.get(growth_stage, 10))


def get_previous_crop_credit(previous_crop: str) -> float:
    """Return N credit (kg/ha) from previous legume crop."""
    return float(N_CREDIT_TABLE.get(previous_crop, 0))


def get_n_removal_estimate(crop_type: str, target_yield_tha: float) -> float:
    """Estimate total N removed by crop at target yield."""
    coeff = N_REMOVAL_COEFF.get(crop_type, 20.0)
    return round(coeff * target_yield_tha, 2)
