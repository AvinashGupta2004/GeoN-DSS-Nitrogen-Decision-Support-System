"""
Risk Engine — Computes leaching and burn risk scores.
These are used by both the LightGBM classifier and the gatekeeper decision.
"""


WEATHER_STATE_LABELS = {
    0: "SUNNY", 1: "PARTLY_CLOUDY", 2: "OVERCAST",
    3: "RAINFALL", 4: "THUNDERSTORM", 5: "FOGGY"
}

# Rule-based thresholds (calibrated from UP agronomic data)
LEACH_SCORE_THRESHOLD = 4.0
BURN_SCORE_THRESHOLD  = 5.0
FORECAST_RAIN_NOGO_MM = 25.0
RAIN_24H_NOGO_MM      = 40.0
BURN_TEMP_THRESHOLD   = 40.0
BURN_HUMID_THRESHOLD  = 35.0


def compute_rain_leach_score(rainfall_24h_mm: float, forecast_48h_mm: float,
                              clay_pct: float) -> float:
    """
    Composite leaching risk: weighted recent + forecast rainfall
    normalized by clay content (clay retains N; sand leaches).
    Range: ~0–10 (>4.0 triggers NO-GO)
    """
    raw = 0.4 * rainfall_24h_mm + 0.6 * forecast_48h_mm
    score = raw / (clay_pct + 1.0)
    return round(score, 4)


def compute_burn_risk_score(temp_max_c: float, wind_speed_ms: float,
                             humidity_pct: float) -> float:
    """
    Composite burn risk: high temp + high wind + low humidity
    increases chance of foliar/soil burn after N application.
    Range: ~0–10 (>5.0 triggers NO-GO)
    """
    score = (temp_max_c * wind_speed_ms) / (humidity_pct + 1.0)
    return round(score, 4)


def classify_window(weather_state: int,
                    rainfall_24h_mm: float,
                    forecast_48h_mm: float,
                    temp_max_c: float,
                    humidity_pct: float,
                    rain_leach_score: float,
                    burn_risk_score: float) -> tuple[int, str | None]:
    """
    Rule-based window classification.

    Returns:
        (window_class: int, reason: str | None)
        0 → NO-GO (leaching), 1 → NO-GO (burn), 2 → GO
    """
    # NO-GO: Leaching risk
    if (weather_state in (3, 4)
            or rain_leach_score > LEACH_SCORE_THRESHOLD
            or forecast_48h_mm > FORECAST_RAIN_NOGO_MM
            or rainfall_24h_mm > RAIN_24H_NOGO_MM):
        return 0, "LEACHING_RISK"

    # NO-GO: Burn risk
    if (weather_state in (4, 5)
            or burn_risk_score > BURN_SCORE_THRESHOLD
            or (temp_max_c > BURN_TEMP_THRESHOLD and humidity_pct < BURN_HUMID_THRESHOLD)):
        return 1, "BURN_RISK"

    return 2, None


def get_alert_message(window_class: int, no_go_reason: str | None) -> str | None:
    if window_class == 0:
        return ("⚠️ NO-GO: High leaching risk detected. Rainfall or wet forecast will "
                "wash nitrogen below root zone. Wait for dry window.")
    if window_class == 1:
        return ("⚠️ NO-GO: Burn risk detected. High temperature with low humidity "
                "and strong winds may cause ammonia volatilization or foliar burn.")
    return None
