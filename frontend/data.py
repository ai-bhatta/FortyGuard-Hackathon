import json
import os
import sys
import pandas as pd

# Add root directory to sys.path so modules (services, risk) can be imported
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from risk.scoring import score_asset
from services.assets import Asset
from services.fortyguard import WeatherSnapshot


def load_asset_data() -> pd.DataFrame:
    csv_path = os.path.join(ROOT_DIR, "data", "assets.csv")
    cache_path = os.path.join(ROOT_DIR, "data", "fortyguard_cache.json")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Could not locate assets.csv at: {csv_path}")

    # Load cached weather data by asset_id
    weather_cache = {}
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            weather_cache = json.load(f)

    df_csv = pd.read_csv(csv_path)
    processed_records = []

    for _, row in df_csv.iterrows():
        asset_id = str(row["asset_id"])

        # 1. Map Asset from assets.csv
        asset = Asset(
            asset_id=asset_id,
            asset_name=str(row["asset_name"]),
            asset_type=str(row["asset_type"]),
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            heat_threshold_celsius=float(row["heat_threshold_celsius"]),
            criticality=int(row["criticality"]),
            age_years=int(row["age_years"]),
            past_heat_incidents=int(row["past_heat_incidents"]),
        )

        # 2. Retrieve dynamic weather data for this asset_id from cache
        asset_weather = weather_cache.get(asset_id, {})

        weather = WeatherSnapshot(
            asset_id=asset_id,
            temperature_celsius=float(asset_weather.get("temperature_celsius", 35.0)),
            apparent_temperature_celsius=float(asset_weather.get("apparent_temperature_celsius", 37.0)),
            relative_humidity_percent=float(asset_weather.get("relative_humidity_percent", 40.0)),
            heat_index_celsius=float(asset_weather.get("heat_index_celsius", 36.5)),
            solar_irradiance_wm2=float(asset_weather.get("solar_irradiance_wm2", 800.0)),
            hours_above_threshold=int(asset_weather.get("hours_above_threshold", 0)),
            source=str(asset_weather.get("source", "cached_demo")),
        )

        # 3. Compute real-time risk score using actual cached weather data
        risk_result = score_asset(asset, weather)

        processed_records.append({
            "asset_id": risk_result.asset_id,
            "asset_name": risk_result.asset_name,
            "asset_type": risk_result.asset_type,
            "latitude": risk_result.latitude,
            "longitude": risk_result.longitude,
            "temperature": risk_result.temperature_celsius,
            "apparent_temperature": risk_result.apparent_temperature_celsius,
            "threshold": risk_result.threshold_celsius,
            "hours_above_threshold": risk_result.hours_above_threshold,
            "criticality": risk_result.criticality,
            "age_years": risk_result.age_years,
            "past_heat_incidents": risk_result.past_heat_incidents,
            "risk_score": risk_result.risk_score,
            "risk_level": risk_result.risk_level,
            "recommendation": risk_result.recommendation,
            "data_source": risk_result.data_source,
            "factors": risk_result.factors,
        })

    return pd.DataFrame(processed_records)