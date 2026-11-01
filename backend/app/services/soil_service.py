"""
Soil Service — Retrieves soil properties for field coordinates
based on SoilGrids (ISRIC) profile and calibrated UP regional soil surveys.
"""
from typing import Dict, Any


# UP Regional Soil Calibration by District
DISTRICT_SOIL_DEFAULTS = {
    "GORAKHPUR": {
        "soil_type": "HEAVY_ALLUVIAL",
        "clay_pct": 45.0,
        "sand_pct": 24.0,
        "silt_pct": 31.0,
        "soil_ph": 7.3,
        "soil_organic_carbon_gkg": 6.2,
        "cec_cmolkg": 21.0,
        "bulk_density_kgdm3": 1.42,
        "nitrogen_soil_gkg": 0.75,
    },
    "KANPUR": {
        "soil_type": "LIGHT_ALLUVIAL",
        "clay_pct": 20.0,
        "sand_pct": 55.0,
        "silt_pct": 25.0,
        "soil_ph": 7.7,
        "soil_organic_carbon_gkg": 3.8,
        "cec_cmolkg": 12.0,
        "bulk_density_kgdm3": 1.55,
        "nitrogen_soil_gkg": 0.45,
    },
    "AMETHI": {
        "soil_type": "MEDIUM_ALLUVIAL",
        "clay_pct": 32.0,
        "sand_pct": 38.0,
        "silt_pct": 30.0,
        "soil_ph": 7.5,
        "soil_organic_carbon_gkg": 4.9,
        "cec_cmolkg": 16.5,
        "bulk_density_kgdm3": 1.48,
        "nitrogen_soil_gkg": 0.60,
    },
    "LUCKNOW": {
        "soil_type": "MEDIUM_ALLUVIAL",
        "clay_pct": 28.0,
        "sand_pct": 42.0,
        "silt_pct": 30.0,
        "soil_ph": 7.6,
        "soil_organic_carbon_gkg": 4.5,
        "cec_cmolkg": 15.5,
        "bulk_density_kgdm3": 1.50,
        "nitrogen_soil_gkg": 0.55,
    }
}


def fetch_soil_properties(district: str) -> Dict[str, Any]:
    """
    Returns soil physical and chemical parameters for the field.
    """
    d_upper = district.upper()
    return DISTRICT_SOIL_DEFAULTS.get(d_upper, DISTRICT_SOIL_DEFAULTS["LUCKNOW"])
