from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from requests import RequestException

from fortyguard import FortyGuardClient, FortyGuardError, TaskTimeoutError
from services.assets import Asset


class FortyGuardServiceError(RuntimeError):
    """Clear boundary error for callers that should not know API internals."""


@dataclass(frozen=True)
class WeatherSnapshot:
    asset_id: str
    temperature_celsius: float
    apparent_temperature_celsius: float
    relative_humidity_percent: float | None
    heat_index_celsius: float | None
    solar_irradiance_wm2: float | None
    hours_above_threshold: int
    source: str


class FortyGuardService:
    """Reusable service layer for FortyGuard-backed asset weather snapshots.

    Set ASSETSHIELD_USE_LIVE_API=true to call FortyGuard. Otherwise the service
    uses clearly labelled cached demo values from ASSETSHIELD_CACHE_PATH.
    """

    def __init__(
        self,
        *,
        use_live_api: bool | None = None,
        cache_path: str | Path | None = None,
        client: FortyGuardClient | None = None,
    ) -> None:
        load_dotenv()
        self.use_live_api = (
            os.getenv("ASSETSHIELD_USE_LIVE_API", "false").lower() == "true"
            if use_live_api is None
            else use_live_api
        )
        self.cache_path = Path(
            cache_path or os.getenv("ASSETSHIELD_CACHE_PATH", "data/fortyguard_cache.json")
        )
        self._client = client

    def get_snapshot(self, asset: Asset) -> WeatherSnapshot:
        if self.use_live_api:
            try:
                return self._get_live_snapshot(asset)
            except (FortyGuardError, TaskTimeoutError, RequestException, KeyError, TypeError, ValueError) as exc:
                raise FortyGuardServiceError(
                    f"Could not fetch FortyGuard data for {asset.asset_id}: {exc}"
                ) from exc
        return self._get_cached_snapshot(asset)

    def _get_live_snapshot(self, asset: Asset) -> WeatherSnapshot:
        client = self._client or FortyGuardClient()
        response = client.environmental_parameters(
            latitude=asset.latitude,
            longitude=asset.longitude,
            temperature=asset.heat_threshold_celsius,
            start_date=os.getenv("ASSETSHIELD_START_DATE", "2024-07-15"),
            start_time=os.getenv("ASSETSHIELD_START_TIME", "12:00"),
            end_time=os.getenv("ASSETSHIELD_END_TIME", "18:00"),
            filter_type=2,
            analysis=[
                "apparent_temperature_celsius",
                "relative_humidity_percent",
                "heat_index_celsius",
                "solar_irradiance",
            ],
            verbose=False,
        )
        result = response["result"]
        location = result["locations"][0]
        params = location["parameters"]
        apparent_values = _numeric_list(params.get("apparent_temperature_celsius"))
        if not apparent_values:
            raise FortyGuardServiceError("missing apparent_temperature_celsius")

        heat_index_values = _numeric_list(params.get("heat_index_celsius"))
        humidity_values = _numeric_list(params.get("relative_humidity_percent"))
        temperature = max(apparent_values)
        return WeatherSnapshot(
            asset_id=asset.asset_id,
            temperature_celsius=temperature,
            apparent_temperature_celsius=temperature,
            relative_humidity_percent=max(humidity_values) if humidity_values else None,
            heat_index_celsius=max(heat_index_values) if heat_index_values else None,
            solar_irradiance_wm2=_extract_solar(location),
            hours_above_threshold=sum(1 for value in apparent_values if value > asset.heat_threshold_celsius),
            source="fortyguard_live",
        )

    def _get_cached_snapshot(self, asset: Asset) -> WeatherSnapshot:
        if not self.cache_path.exists():
            raise FortyGuardServiceError(f"Cache file not found: {self.cache_path}")
        payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
        if asset.asset_id not in payload:
            raise FortyGuardServiceError(f"No cached demo data for asset {asset.asset_id}")
        return _snapshot_from_mapping(asset.asset_id, payload[asset.asset_id])


def _snapshot_from_mapping(asset_id: str, data: dict[str, Any]) -> WeatherSnapshot:
    required = [
        "temperature_celsius",
        "apparent_temperature_celsius",
        "hours_above_threshold",
        "source",
    ]
    missing = [field for field in required if field not in data or data[field] is None]
    if missing:
        raise FortyGuardServiceError(f"{asset_id}: cached data missing {missing}")
    return WeatherSnapshot(
        asset_id=asset_id,
        temperature_celsius=float(data["temperature_celsius"]),
        apparent_temperature_celsius=float(data["apparent_temperature_celsius"]),
        relative_humidity_percent=_optional_float(data.get("relative_humidity_percent")),
        heat_index_celsius=_optional_float(data.get("heat_index_celsius")),
        solar_irradiance_wm2=_optional_float(data.get("solar_irradiance_wm2")),
        hours_above_threshold=max(0, int(data["hours_above_threshold"])),
        source=str(data["source"]),
    )


def _numeric_list(values: Any) -> list[float]:
    if not isinstance(values, list):
        return []
    return [float(value) for value in values if value is not None]


def _optional_float(value: Any) -> float | None:
    return None if value is None else float(value)


def _extract_solar(location: dict[str, Any]) -> float | None:
    candidates = [
        location.get("solar_irradiance"),
        location.get("parameters", {}).get("solar_irradiance"),
    ]
    for candidate in candidates:
        if isinstance(candidate, (int, float)):
            return float(candidate)
        if isinstance(candidate, dict):
            ghi = candidate.get("clear_sky", {}).get("ghi") or candidate.get("ghi")
            if ghi is not None:
                return float(ghi)
    return None
