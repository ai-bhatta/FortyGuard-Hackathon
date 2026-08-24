from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from assetshield_backend import build_asset_risk_report
from services.assets import load_assets
from services.fortyguard import FortyGuardService, FortyGuardServiceError


app = FastAPI(
    title="AssetShield AI Backend",
    description="Heat exposure scoring API for California demo assets.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "assetshield-backend"}


@app.get("/assets")
def list_assets() -> list[dict]:
    return [asset.__dict__ for asset in load_assets()]


@app.get("/risks")
def list_risks(
    risk_level: str | None = Query(default=None),
    asset_type: str | None = Query(default=None),
    live: bool = Query(default=False, description="Call FortyGuard instead of cached demo data."),
) -> list[dict]:
    return _risk_payload(risk_level=risk_level, asset_type=asset_type, live=live)


@app.get("/risks/{asset_id}")
def get_asset_risk(asset_id: str, live: bool = Query(default=False)) -> dict:
    for item in _risk_payload(live=live):
        if item["asset_id"].lower() == asset_id.lower():
            return item
    raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")


def _risk_payload(
    *,
    risk_level: str | None = None,
    asset_type: str | None = None,
    live: bool = False,
) -> list[dict]:
    try:
        report = build_asset_risk_report(service=FortyGuardService(use_live_api=live))
    except FortyGuardServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    payload = [result.to_dict() for result in report]
    if risk_level:
        payload = [
            item for item in payload
            if item["risk_level"].lower() == risk_level.lower()
        ]
    if asset_type:
        payload = [
            item for item in payload
            if item["asset_type"].lower() == asset_type.lower()
        ]
    return payload
