from assetshield_backend import build_asset_risk_report
from services.assets import load_assets
from services.fortyguard import FortyGuardService


def test_load_assets_has_required_demo_size():
    assets = load_assets()

    assert 10 <= len(assets) <= 20
    assert all(asset.asset_id for asset in assets)


def test_build_report_returns_ranked_cached_results():
    report = build_asset_risk_report(service=FortyGuardService(use_live_api=False))

    assert len(report) == 12
    assert report[0].risk_score >= report[-1].risk_score
    assert {item.data_source for item in report} == {"cached_demo"}
