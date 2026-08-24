from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Asset:
    asset_id: str
    asset_name: str
    asset_type: str
    latitude: float
    longitude: float
    heat_threshold_celsius: float
    criticality: int
    age_years: int
    past_heat_incidents: int = 0


def load_assets(path: str | Path = "data/assets.csv") -> list[Asset]:
    """Load and validate the demo asset inventory."""
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"Asset dataset not found: {target}")

    assets: list[Asset] = []
    with target.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            asset = Asset(
                asset_id=row["asset_id"].strip(),
                asset_name=row["asset_name"].strip(),
                asset_type=row["asset_type"].strip(),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                heat_threshold_celsius=float(row["heat_threshold_celsius"]),
                criticality=int(row["criticality"]),
                age_years=int(row["age_years"]),
                past_heat_incidents=int(row.get("past_heat_incidents") or 0),
            )
            validate_asset(asset)
            assets.append(asset)
    if not 10 <= len(assets) <= 20:
        raise ValueError("Demo asset dataset must contain 10-20 assets.")
    return assets


def validate_asset(asset: Asset) -> None:
    if not asset.asset_id:
        raise ValueError("Asset ID is required.")
    if not -90 <= asset.latitude <= 90:
        raise ValueError(f"{asset.asset_id}: invalid latitude {asset.latitude}")
    if not -180 <= asset.longitude <= 180:
        raise ValueError(f"{asset.asset_id}: invalid longitude {asset.longitude}")
    if not 1 <= asset.criticality <= 5:
        raise ValueError(f"{asset.asset_id}: criticality must be 1-5")
    if asset.age_years < 0:
        raise ValueError(f"{asset.asset_id}: age cannot be negative")
    if asset.past_heat_incidents < 0:
        raise ValueError(f"{asset.asset_id}: past incidents cannot be negative")
