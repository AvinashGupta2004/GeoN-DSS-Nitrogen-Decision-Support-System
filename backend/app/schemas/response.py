"""
Pydantic response schemas for the prediction endpoint.
"""

from pydantic import BaseModel
from typing import Optional, Dict, List


class RiskScores(BaseModel):
    rain_leach_score: float
    burn_risk_score: float
    weather_state: int
    weather_state_label: str


class SpectralData(BaseModel):
    ndvi: float
    gndvi: float
    ndre: float
    evi: float
    lai: float
    cloud_coverage_pct: float
    ndvi_15d_trend: float
    ndre_15d_trend: float
    image_date: str


class WeatherData(BaseModel):
    temp_max_c: float
    temp_avg_c: float
    humidity_pct: float
    rainfall_24h_mm: float
    rainfall_forecast_48h_mm: float
    wind_speed_ms: float
    et0_mm: float


class DosageSchedule(BaseModel):
    immediate_kg_ha: float       # 40% of recommendation
    post_irrigation_kg_ha: float # 60% of recommendation
    urea_total_kg_ha: float
    dap_total_kg_ha: float
    field_area_ha: float
    urea_total_kg: float         # scaled to actual field area
    dap_total_kg: float


class SHAPExplanation(BaseModel):
    top_features: List[Dict]     # [{"feature": str, "shap_value": float, "direction": str}]
    summary: str                 # Human-readable explanation


class PredictResponse(BaseModel):
    """Full API response for a nitrogen recommendation request."""
    status: str                  # "GO" or "NO_GO"
    window_class: int            # 0, 1, or 2
    no_go_reason: Optional[str]  # None if GO; "LEACHING_RISK" or "BURN_RISK" if NO_GO
    alert_message: Optional[str]

    recommended_N_kg_ha: Optional[float]
    dosage_schedule: Optional[DosageSchedule]

    risk_scores: RiskScores
    spectral_data: SpectralData
    weather_data: WeatherData
    shap_explanation: Optional[SHAPExplanation]

    centroid_lat: float
    centroid_lon: float
    field_area_ha: float
    location_name: Optional[str] = "Gorakhpur Farmland"
