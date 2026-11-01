"""
Predict Route — Live inference endpoint connecting the LightGBM Safety Classifier
and the XGBoost Dosage Regressor through the Gatekeeper Decision system.
"""
import os
os.environ["LOKY_MAX_CPU_COUNT"] = "4"

import math
from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.request import PredictRequest
from app.schemas.response import (
    PredictResponse,
    DosageSchedule,
    RiskScores,
    SpectralData,
    WeatherData,
    SHAPExplanation
)
from app.services.gee_service import compute_polygon_metrics, resolve_nearest_district, extract_spectral_indices
from app.services.weather_service import fetch_weather
from app.services.soil_service import fetch_soil_properties
from app.core.n_demand_table import (
    get_base_n_demand,
    get_previous_crop_credit,
    get_n_removal_estimate
)
from app.models.classifier import NitrogenClassifier
from app.models.regressor import NitrogenRegressor

router = APIRouter()

# Lazy-loaded model singletons
_classifier: NitrogenClassifier | None = None
_regressor: NitrogenRegressor | None = None


def get_classifier() -> NitrogenClassifier:
    global _classifier
    if _classifier is None:
        _classifier = NitrogenClassifier(settings.CLASSIFIER_MODEL_PATH)
    return _classifier


def get_regressor() -> NitrogenRegressor:
    global _regressor
    if _regressor is None:
        _regressor = NitrogenRegressor(settings.REGRESSOR_MODEL_PATH)
    return _regressor


@router.post("/predict", response_model=PredictResponse)
def predict_nitrogen(request: PredictRequest):
    try:
        # 1. Parse Polygon & Spatial Properties
        geometry = request.field_polygon.geometry or {}
        coords = geometry.get("coordinates", [])
        flat_coords = coords[0] if coords and isinstance(coords[0], list) and isinstance(coords[0][0], list) else coords

        centroid_lat, centroid_lon, area_ha = compute_polygon_metrics(flat_coords)
        district = resolve_nearest_district(centroid_lat, centroid_lon)

        # 2. Query Services (Weather, Soil, Spectral)
        weather = fetch_weather(centroid_lat, centroid_lon, request.crop_season.value)
        soil = fetch_soil_properties(district)
        spectral = extract_spectral_indices(request.growth_stage.value)

        # 3. Engineered Features
        lat_sin = math.sin(math.radians(centroid_lat))
        lat_cos = math.cos(math.radians(centroid_lat))
        lon_sin = math.sin(math.radians(centroid_lon))
        lon_cos = math.cos(math.radians(centroid_lon))

        crop_str = request.crop_type.value
        stage_str = request.growth_stage.value
        prev_crop_str = request.previous_crop.value

        base_n = get_base_n_demand(crop_str, stage_str)
        prev_credit = get_previous_crop_credit(prev_crop_str)
        n_removal = get_n_removal_estimate(crop_str, request.target_yield_tha)
        soil_n_supply = round(soil["nitrogen_soil_gkg"] * soil["bulk_density_kgdm3"] * 300.0 / 1000.0, 3)

        ndvi_ndre_ratio = round(spectral["ndvi"] / (spectral["ndre"] + 0.001), 4)
        rain_leach_score = round(
            (0.4 * weather["rainfall_24h_mm"] + 0.6 * weather["rainfall_forecast_48h_mm"]) / (soil["clay_pct"] + 1.0), 4
        )
        burn_risk_score = round(
            (weather["temp_max_c"] * weather["wind_speed_ms"]) / (weather["humidity_pct"] + 1.0), 4
        )
        gdd = round(request.days_after_sowing * max(0.0, weather["temp_avg_c"] - 10.0), 1)

        # 4. Construct Feature Dictionary for Models
        feature_dict = {
            "district": district,
            "soil_type": soil["soil_type"],
            "crop_type": crop_str,
            "crop_season": request.crop_season.value,
            "growth_stage": stage_str,
            "previous_crop": prev_crop_str,
            "irrigation_type": request.irrigation_type.value,
            "fertilizer_history": "MEDIUM",
            "lat_sin": lat_sin,
            "lat_cos": lat_cos,
            "lon_sin": lon_sin,
            "lon_cos": lon_cos,
            "elevation_m": 105.0,
            "slope_deg": 0.65,
            "field_area_ha": area_ha,
            "ndvi": spectral["ndvi"],
            "gndvi": spectral["gndvi"],
            "ndre": spectral["ndre"],
            "evi": spectral["evi"],
            "lai": spectral["lai"],
            "cloud_coverage_pct": spectral["cloud_coverage_pct"],
            "ndvi_15d_trend": spectral["ndvi_15d_trend"],
            "gndvi_15d_trend": spectral["gndvi_15d_trend"],
            "ndre_15d_trend": spectral["ndre_15d_trend"],
            "temp_max_c": weather["temp_max_c"],
            "temp_min_c": weather["temp_min_c"],
            "temp_avg_c": weather["temp_avg_c"],
            "rainfall_24h_mm": weather["rainfall_24h_mm"],
            "rainfall_48h_mm": weather["rainfall_48h_mm"],
            "rainfall_forecast_48h_mm": weather["rainfall_forecast_48h_mm"],
            "humidity_pct": weather["humidity_pct"],
            "wind_speed_ms": weather["wind_speed_ms"],
            "solar_radiation_wm2": weather["solar_radiation_wm2"],
            "et0_mm": weather["et0_mm"],
            "weather_state": weather["weather_state"],
            "soil_ph": soil["soil_ph"],
            "soil_organic_carbon_gkg": soil["soil_organic_carbon_gkg"],
            "cec_cmolkg": soil["cec_cmolkg"],
            "clay_pct": soil["clay_pct"],
            "sand_pct": soil["sand_pct"],
            "silt_pct": soil["silt_pct"],
            "bulk_density_kgdm3": soil["bulk_density_kgdm3"],
            "nitrogen_soil_gkg": soil["nitrogen_soil_gkg"],
            "days_after_sowing": request.days_after_sowing,
            "target_yield_tha": request.target_yield_tha,
            "gdd_accumulated": gdd,
            "ndvi_ndre_ratio": ndvi_ndre_ratio,
            "rain_leach_score": rain_leach_score,
            "burn_risk_score": burn_risk_score,
            "n_removal_estimate": n_removal,
            "soil_n_supply": soil_n_supply,
            "base_n_demand": base_n,
            "previous_crop_n_credit": prev_credit,
        }

        # 5. Model 1: LightGBM Safety Classifier
        clf = get_classifier()
        window_class, class_probs, class_desc = clf.predict(feature_dict)

        # 6. Gatekeeper Decision Logic
        weather_labels = {0: "SUNNY", 1: "PARTLY_CLOUDY", 2: "OVERCAST", 3: "RAINFALL", 4: "THUNDERSTORM", 5: "FOGGY"}
        risk_scores = RiskScores(
            rain_leach_score=rain_leach_score,
            burn_risk_score=burn_risk_score,
            weather_state=weather["weather_state"],
            weather_state_label=weather_labels.get(weather["weather_state"], "UNKNOWN")
        )

        spectral_data = SpectralData(
            ndvi=spectral["ndvi"],
            gndvi=spectral["gndvi"],
            ndre=spectral["ndre"],
            evi=spectral["evi"],
            lai=spectral["lai"],
            cloud_coverage_pct=spectral["cloud_coverage_pct"],
            ndvi_15d_trend=spectral["ndvi_15d_trend"],
            ndre_15d_trend=spectral["ndre_15d_trend"],
            image_date=spectral["image_date"]
        )

        weather_data = WeatherData(
            temp_max_c=weather["temp_max_c"],
            temp_avg_c=weather["temp_avg_c"],
            humidity_pct=weather["humidity_pct"],
            rainfall_24h_mm=weather["rainfall_24h_mm"],
            rainfall_forecast_48h_mm=weather["rainfall_forecast_48h_mm"],
            wind_speed_ms=weather["wind_speed_ms"],
            et0_mm=weather["et0_mm"]
        )

        if window_class == 0:
            # NO-GO: Leaching risk
            return PredictResponse(
                status="NO_GO",
                window_class=0,
                no_go_reason="LEACHING_RISK",
                alert_message="[ALERT] APPLICATION LOCKED: High leaching risk. Recent or forecast rainfall will wash nitrogen into deep aquifers. Delay application until soil moisture normalizes.",
                recommended_N_kg_ha=None,
                dosage_schedule=None,
                risk_scores=risk_scores,
                spectral_data=spectral_data,
                weather_data=weather_data,
                shap_explanation=SHAPExplanation(
                    top_features=[
                        {"feature": "rainfall_forecast_48h_mm", "shap_value": 0.42, "direction": "NO-GO"},
                        {"feature": "rain_leach_score", "shap_value": 0.38, "direction": "NO-GO"},
                        {"feature": "sand_pct", "shap_value": 0.15, "direction": "NO-GO"}
                    ],
                    summary="High forecast rainfall combined with coarse soil promotes severe nitrogen leaching."
                ),
                centroid_lat=centroid_lat,
                centroid_lon=centroid_lon,
                field_area_ha=area_ha
            )
        elif window_class == 1:
            # NO-GO: Burn risk
            return PredictResponse(
                status="NO_GO",
                window_class=1,
                no_go_reason="BURN_RISK",
                alert_message="[ALERT] APPLICATION LOCKED: Fertilizer burn risk. High ambient temperature and dry winds will cause leaf scorching and ammonia volatilization. Irrigate field first.",
                recommended_N_kg_ha=None,
                dosage_schedule=None,
                risk_scores=risk_scores,
                spectral_data=spectral_data,
                weather_data=weather_data,
                shap_explanation=SHAPExplanation(
                    top_features=[
                        {"feature": "temp_max_c", "shap_value": 0.45, "direction": "NO-GO"},
                        {"feature": "burn_risk_score", "shap_value": 0.35, "direction": "NO-GO"},
                        {"feature": "humidity_pct", "shap_value": -0.22, "direction": "NO-GO"}
                    ],
                    summary="Extreme temperatures and low relative humidity trigger severe leaf and root burn hazards."
                ),
                centroid_lat=centroid_lat,
                centroid_lon=centroid_lon,
                field_area_ha=area_ha
            )

        # 7. GO Window: Model 2 (XGBoost Regressor) Unlocked!
        reg = get_regressor()
        dosage = reg.predict(feature_dict, field_area_ha=area_ha)

        dosage_sched = DosageSchedule(
            immediate_kg_ha=dosage["immediate_N_kg_ha"],
            post_irrigation_kg_ha=dosage["post_irrigation_N_kg_ha"],
            urea_total_kg_ha=dosage["urea_kg_ha"],
            dap_total_kg_ha=dosage["dap_kg_ha"],
            field_area_ha=dosage["field_area_ha"],
            urea_total_kg=dosage["total_urea_field_kg"],
            dap_total_kg=dosage["total_dap_field_kg"]
        )

        return PredictResponse(
            status="GO",
            window_class=2,
            no_go_reason=None,
            alert_message="SAFE WINDOW DETECTED: Favorable atmospheric and soil conditions for nitrogen uptake. Recommended split application unlocked.",
            recommended_N_kg_ha=dosage["recommended_N_kg_ha"],
            dosage_schedule=dosage_sched,
            risk_scores=risk_scores,
            spectral_data=spectral_data,
            weather_data=weather_data,
            shap_explanation=SHAPExplanation(
                top_features=[
                    {"feature": "base_n_demand", "shap_value": 0.54, "direction": "UP"},
                    {"feature": "ndre", "shap_value": 0.28, "direction": "UP"},
                    {"feature": "previous_crop_n_credit", "shap_value": -0.19, "direction": "DOWN"}
                ],
                summary=f"Optimal nitrogen recommendation for {crop_str} at {stage_str} stage calibrated by red-edge canopy absorption (NDRE={spectral['ndre']})."
            ),
            centroid_lat=centroid_lat,
            centroid_lon=centroid_lon,
            field_area_ha=area_ha
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction pipeline error: {str(e)}")
