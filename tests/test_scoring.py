from services.assets import Asset
from services.fortyguard import WeatherSnapshot
from risk.scoring import classify_risk, score_asset


def test_risk_boundaries():
    assert classify_risk(0) == "Low"
    assert classify_risk(24) == "Low"
    assert classify_risk(25) == "Moderate"
    assert classify_risk(49) == "Moderate"
    assert classify_risk(50) == "High"
    assert classify_risk(74) == "High"
    assert classify_risk(75) == "Critical"


def test_critical_asset_above_threshold_scores_high():
    asset = Asset("A001", "Critical Pump", "Pump", 24.4, 54.3, 38, 5, 12, 3)
    snapshot = WeatherSnapshot("A001", 45, 48, 60, 50, 900, 8, "test")

    result = score_asset(asset, snapshot)

    assert result.risk_score >= 75
    assert result.risk_level == "Critical"
    assert result.recommendation == "Prioritize Inspection"
    assert len(result.factors) == 5


def test_below_threshold_asset_still_reflects_criticality_without_false_failure_claim():
    asset = Asset("A002", "New Sensor", "Sensor", 24.4, 54.3, 40, 2, 1, 0)
    snapshot = WeatherSnapshot("A002", 33, 34, 40, 35, 700, 0, "test")

    result = score_asset(asset, snapshot)

    assert result.risk_level in {"Low", "Moderate"}
    assert "failure" not in result.recommendation.lower()
