"""
Soil Service — Retrieves soil properties for field coordinates.
Uses coordinate-seeded micro-variation so each drawn field returns
slightly different but agronomically realistic soil readings.
"""
import math
from typing import Dict, Any


# UP Regional Soil Calibration by District (base values)
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
    },
}

# Variation ranges per property (±max_delta around the base)
_VARIATION = {
    "soil_ph":                  0.25,   # ± 0.25 pH units
    "soil_organic_carbon_gkg":  1.2,    # ± 1.2 g/kg
    "clay_pct":                 6.0,    # ± 6 %
    "sand_pct":                 6.0,
    "silt_pct":                 4.0,
    "cec_cmolkg":               3.0,
    "bulk_density_kgdm3":       0.08,
    "nitrogen_soil_gkg":        0.18,
}


def _field_seed(lat: float, lon: float) -> float:
    """
    Returns a deterministic scalar in [−1, +1] derived from the centroid.
    Different lat/lon → different seed → different soil reading.
    """
    # Use a mix of trig functions so nearby fields still differ noticeably
    raw = math.sin(lat * 173.31) * math.cos(lon * 211.47) + \
          math.sin((lat + lon) * 97.63) * 0.5
    # raw is roughly in [−1.5, +1.5]; clamp to [−1, +1]
    return max(-1.0, min(1.0, raw))


def fetch_soil_properties(district: str, lat: float = 0.0, lon: float = 0.0) -> Dict[str, Any]:
    """
    Returns soil physical and chemical parameters for the field.
    Uses lat/lon to introduce realistic field-to-field variation so that
    different drawn polygons produce meaningfully different predictions.
    """
    base = dict(DISTRICT_SOIL_DEFAULTS.get(district.upper(), DISTRICT_SOIL_DEFAULTS["LUCKNOW"]))
    seed = _field_seed(lat, lon)

    for key, delta in _VARIATION.items():
        if key in base:
            base[key] = round(base[key] + seed * delta, 3)

    # Hard clamp to realistic agronomic bounds
    base["soil_ph"]                 = round(max(5.5, min(9.0,  base["soil_ph"])), 2)
    base["soil_organic_carbon_gkg"] = round(max(1.5, min(14.0, base["soil_organic_carbon_gkg"])), 2)
    base["clay_pct"]                = round(max(5.0, min(70.0, base["clay_pct"])), 1)
    base["sand_pct"]                = round(max(5.0, min(80.0, base["sand_pct"])), 1)
    base["silt_pct"]                = round(max(5.0, min(70.0, base["silt_pct"])), 1)
    base["cec_cmolkg"]              = round(max(5.0, min(40.0, base["cec_cmolkg"])), 1)
    base["bulk_density_kgdm3"]      = round(max(1.0, min(1.9,  base["bulk_density_kgdm3"])), 3)
    base["nitrogen_soil_gkg"]       = round(max(0.1, min(2.5,  base["nitrogen_soil_gkg"])), 3)

    return base
