from __future__ import annotations

from services.assets import Asset, load_assets
from services.fortyguard import FortyGuardService
from risk.scoring import RiskResult, score_asset


def build_asset_risk_report(
    *,
    asset_path: str = "data/assets.csv",
    service: FortyGuardService | None = None,
) -> list[RiskResult]:
    """Load assets, fetch heat data, score them, and return highest risk first."""
    assets = load_assets(asset_path)
    fortyguard = service or FortyGuardService()
    results = [score_asset(asset, fortyguard.get_snapshot(asset)) for asset in assets]
    return sorted(results, key=lambda item: item.risk_score, reverse=True)


def build_frontend_payload() -> list[dict]:
    """Structured data for Streamlit/frontend/AI layers."""
    return [result.to_dict() for result in build_asset_risk_report()]


if __name__ == "__main__":
    for result in build_asset_risk_report():
        print(
            f"{result.asset_id} | {result.risk_score:3d} | "
            f"{result.risk_level:8s} | {result.recommendation} | {result.asset_name}"
        )
