from __future__ import annotations

from dataclasses import asdict, dataclass

from services.assets import Asset
from services.fortyguard import WeatherSnapshot


@dataclass(frozen=True)
class RiskFactor:
    name: str
    value: float | int | str | None
    points: float
    max_points: float
    explanation: str


@dataclass(frozen=True)
class RiskResult:
    asset_id: str
    asset_name: str
    asset_type: str
    latitude: float
    longitude: float
    temperature_celsius: float
    apparent_temperature_celsius: float
    threshold_celsius: float
    hours_above_threshold: int
    criticality: int
    age_years: int
    past_heat_incidents: int
    risk_score: int
    risk_level: str
    recommendation: str
    data_source: str
    factors: list[RiskFactor]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["factors"] = [asdict(factor) for factor in self.factors]
        return payload


def score_asset(asset: Asset, snapshot: WeatherSnapshot) -> RiskResult:
    """Calculate a transparent 0-100 heat exposure priority score."""
    if snapshot.apparent_temperature_celsius is None:
        raise ValueError(f"{asset.asset_id}: missing apparent temperature")

    severity_delta = snapshot.apparent_temperature_celsius - asset.heat_threshold_celsius
    severity_points = _clamp((severity_delta / 10) * 30, 0, 30)
    exposure_points = _clamp((snapshot.hours_above_threshold / 8) * 25, 0, 25)
    criticality_points = _clamp((asset.criticality / 5) * 20, 0, 20)
    age_points = _clamp((asset.age_years / 15) * 15, 0, 15)
    incident_points = _clamp(asset.past_heat_incidents * 2.5, 0, 10)

    score = round(
        severity_points
        + exposure_points
        + criticality_points
        + age_points
        + incident_points
    )
    score = int(_clamp(score, 0, 100))
    risk_level = classify_risk(score)

    return RiskResult(
        asset_id=asset.asset_id,
        asset_name=asset.asset_name,
        asset_type=asset.asset_type,
        latitude=asset.latitude,
        longitude=asset.longitude,
        temperature_celsius=snapshot.temperature_celsius,
        apparent_temperature_celsius=snapshot.apparent_temperature_celsius,
        threshold_celsius=asset.heat_threshold_celsius,
        hours_above_threshold=snapshot.hours_above_threshold,
        criticality=asset.criticality,
        age_years=asset.age_years,
        past_heat_incidents=asset.past_heat_incidents,
        risk_score=score,
        risk_level=risk_level,
        recommendation=recommend_action(risk_level),
        data_source=snapshot.source,
        factors=[
            RiskFactor(
                "temperature_severity",
                round(severity_delta, 2),
                round(severity_points, 1),
                30,
                "Higher when apparent temperature is above the configured asset threshold.",
            ),
            RiskFactor(
                "time_above_threshold",
                snapshot.hours_above_threshold,
                round(exposure_points, 1),
                25,
                "Higher when heat exposure persists for more hours.",
            ),
            RiskFactor(
                "asset_criticality",
                asset.criticality,
                round(criticality_points, 1),
                20,
                "Higher for assets with greater operational importance.",
            ),
            RiskFactor(
                "asset_age",
                asset.age_years,
                round(age_points, 1),
                15,
                "Older assets receive more inspection priority in this demo model.",
            ),
            RiskFactor(
                "past_heat_incidents",
                asset.past_heat_incidents,
                round(incident_points, 1),
                10,
                "Past heat incidents add priority without implying certain failure.",
            ),
        ],
    )


def classify_risk(score: int | float) -> str:
    if score < 25:
        return "Low"
    if score < 50:
        return "Moderate"
    if score < 75:
        return "High"
    return "Critical"


def recommend_action(risk_level: str) -> str:
    return {
        "Low": "Monitor",
        "Moderate": "Review during next maintenance window",
        "High": "Schedule Inspection",
        "Critical": "Prioritize Inspection",
    }[risk_level]


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))
