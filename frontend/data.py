import os
import sys
import pandas as pd

# Dynamic path resolution to project root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from risk.scoring import score_asset
from services.assets import Asset
from services.fortyguard import WeatherSnapshot


def load_asset_data() -> pd.DataFrame:
    csv_path = os.path.join(ROOT_DIR, "data", "assets.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Could not locate assets.csv at: {csv_path}")

    # Read exactly from assets.csv
    df_csv = pd.read_csv(csv_path)
    processed_records = []

    for _, row in df_csv.iterrows():
        asset_id = str(row["asset_id"])
        
        # 1. Map Asset strictly from CSV values
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

        # 2. Extract or safely default dynamic columns directly from CSV
        # (Uses CSV column if available, falls back to asset threshold baseline if not)
        temp_c = float(row.get("temperature", row["heat_threshold_celsius"] + 2.4))
        apparent_temp_c = float(row.get("apparent_temperature", temp_c + 3.0))
        hours_above = int(row.get("hours_above_threshold", 4))
        humidity = float(row.get("relative_humidity_percent", 45.0))
        heat_index = float(row.get("heat_index_celsius", apparent_temp_c))
        solar_irradiance = float(row.get("solar_irradiance_wm2", 800.0))

        weather = WeatherSnapshot(
            asset_id=asset_id,
            temperature_celsius=temp_c,
            apparent_temperature_celsius=apparent_temp_c,
            relative_humidity_percent=humidity,
            heat_index_celsius=heat_index,
            solar_irradiance_wm2=solar_irradiance,
            hours_above_threshold=hours_above,
            source="FortyGuard",
        )

        # 3. Compute risk score via risk engine
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