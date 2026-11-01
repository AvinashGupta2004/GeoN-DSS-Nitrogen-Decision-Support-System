"""
Weather Service — Synchronous meteorological parameters and 48-hour forecast
from Open-Meteo API or calibrated UP climate profiles.
"""
import os
from typing import Dict, Any
import requests

USE_ONLINE_WEATHER = os.getenv("USE_ONLINE_WEATHER", "false").lower() in ("true", "1")


def fetch_weather(lat: float, lon: float, season: str = "RABI") -> Dict[str, Any]:
    """
    Retrieves current weather and 48-hour precipitation forecast for field coordinates.
    Calibrated UP district climate baseline is used when offline or in development.
    """
    if USE_ONLINE_WEATHER:
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "weather_code"],
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "et0_fao_evapotranspiration"],
                "forecast_days": 3,
                "timezone": "auto"
            }
            resp = requests.get(url, params=params, timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                daily = data.get("daily", {})

                temp_max = float(daily.get("temperature_2m_max", [30.0])[0])
                temp_min = float(daily.get("temperature_2m_min", [18.0])[0])
                temp_avg = round((temp_max + temp_min) / 2.0, 1)
                humidity = float(current.get("relative_humidity_2m", 60.0))
                wind_speed = float(current.get("wind_speed_10m", 3.5))

                precip_sums = daily.get("precipitation_sum", [0.0, 0.0, 0.0])
                rainfall_24h = float(precip_sums[0]) if len(precip_sums) > 0 else 0.0
                rainfall_48h = round(rainfall_24h + (float(precip_sums[1]) if len(precip_sums) > 1 else 0.0), 1)
                rainfall_forecast_48h = round(sum(precip_sums[1:3]), 1) if len(precip_sums) >= 3 else 0.0

                et0_values = daily.get("et0_fao_evapotranspiration", [4.0])
                et0 = float(et0_values[0]) if et0_values else 4.0

                w_code = current.get("weather_code", 0)
                if w_code in [0, 1]:
                    weather_state = 0  # SUNNY
                elif w_code in [2, 3]:
                    weather_state = 1  # PARTLY_CLOUDY
                elif w_code in [45, 48]:
                    weather_state = 5  # FOGGY
                elif w_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                    weather_state = 3  # RAINFALL
                elif w_code in [95, 96, 99]:
                    weather_state = 4  # THUNDERSTORM
                else:
                    weather_state = 2  # OVERCAST

                return {
                    "temp_max_c": temp_max,
                    "temp_min_c": temp_min,
                    "temp_avg_c": temp_avg,
                    "rainfall_24h_mm": rainfall_24h,
                    "rainfall_48h_mm": rainfall_48h,
                    "rainfall_forecast_48h_mm": rainfall_forecast_48h,
                    "humidity_pct": humidity,
                    "wind_speed_ms": wind_speed,
                    "solar_radiation_wm2": 450.0,
                    "et0_mm": et0,
                    "weather_state": weather_state,
                    "source": "Open-Meteo live API"
                }
        except Exception:
            pass

    # Calibrated UP default fallback based on season
    if season == "KHARIF":
        return {
            "temp_max_c": 33.5,
            "temp_min_c": 26.0,
            "temp_avg_c": 29.8,
            "rainfall_24h_mm": 5.0,
            "rainfall_48h_mm": 12.0,
            "rainfall_forecast_48h_mm": 8.0,
            "humidity_pct": 78.0,
            "wind_speed_ms": 3.2,
            "solar_radiation_wm2": 420.0,
            "et0_mm": 4.5,
            "weather_state": 1,
            "source": "UP Kharif Climate Baseline"
        }
    elif season == "ZAID":
        return {
            "temp_max_c": 39.0,
            "temp_min_c": 25.0,
            "temp_avg_c": 32.0,
            "rainfall_24h_mm": 0.0,
            "rainfall_48h_mm": 0.0,
            "rainfall_forecast_48h_mm": 0.0,
            "humidity_pct": 38.0,
            "wind_speed_ms": 5.5,
            "solar_radiation_wm2": 720.0,
            "et0_mm": 7.5,
            "weather_state": 0,
            "source": "UP Zaid Climate Baseline"
        }
    else:  # RABI default
        return {
            "temp_max_c": 23.5,
            "temp_min_c": 10.5,
            "temp_avg_c": 17.0,
            "rainfall_24h_mm": 0.0,
            "rainfall_48h_mm": 0.0,
            "rainfall_forecast_48h_mm": 2.0,
            "humidity_pct": 58.0,
            "wind_speed_ms": 2.8,
            "solar_radiation_wm2": 380.0,
            "et0_mm": 2.8,
            "weather_state": 0,
            "source": "UP Rabi Climate Baseline"
        }
