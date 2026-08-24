# AssetShield AI Backend

AssetShield AI turns FortyGuard temperature intelligence into an explainable maintenance-priority score for outdoor assets. This backend focuses on the hackathon MVP requirements from the team document: demo assets, FortyGuard integration boundary, 0-100 heat exposure scoring, risk labels, recommendations, and frontend-ready structured output.

## What Is Done

- Demo asset dataset with 12 labelled California industrial assets in `data/assets.csv`.
- Reusable FortyGuard service in `services/fortyguard.py`.
- API key loading from environment variables, with no committed secret.
- Cached demo response support in `data/fortyguard_cache.json` for reliable demos.
- Validation for asset coordinates, required cached fields, missing API fields, HTTP/API errors, and timeouts.
- Explainable 0-100 heat exposure scoring in `risk/scoring.py`.
- Risk classifications: Low, Moderate, High, Critical.
- Recommendation logic: Monitor, Review during next maintenance window, Schedule Inspection, Prioritize Inspection.
- Frontend/AI-ready payload builder in `assetshield_backend.py`.
- FastAPI HTTP endpoints in `api_server.py` for frontend integration.
- Tests for scoring boundaries, critical/high cases, demo asset loading, and ranked output.

This is a transparent prioritization model for heat exposure and inspection attention. It does not predict exact equipment failure.

## Setup With uv

```bash
uv sync
```

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

## Where To Add Your API Key

Add your real FortyGuard key to `.env`:

```env
FORTYGUARD_API_KEY=your_real_key_here
FORTYGUARD_BASE_URL=https://api.fortyguard.com
ASSETSHIELD_USE_LIVE_API=true
ASSETSHIELD_CACHE_PATH=data/fortyguard_cache.json
```

Keep `ASSETSHIELD_USE_LIVE_API=false` if you want to use cached demo data without calling the API.

## Run The Backend Demo

```bash
uv run python assetshield_backend.py
```

The script prints assets ranked by score, highest risk first.

## Run The HTTP API

```bash
uv run uvicorn api_server:app --reload
```

Default local URL:

```text
http://127.0.0.1:8000
```

Frontend handoff endpoints:

- `GET /health`: backend health check.
- `GET /assets`: raw California demo asset inventory.
- `GET /risks`: ranked scored assets, highest risk first.
- `GET /risks?risk_level=High`: filter by risk level.
- `GET /risks?asset_type=Telecom`: filter by asset type.
- `GET /risks/{asset_id}`: one asset detail with score breakdown.
- `GET /docs`: interactive FastAPI docs.

By default, endpoints use cached demo data. To call FortyGuard live, pass `live=true`, for example `GET /risks?live=true`, and set `ASSETSHIELD_USE_LIVE_API=true` plus `FORTYGUARD_API_KEY` in `.env`.

## Run Tests

```bash
uv run pytest
```

## Backend Modules

- `services/assets.py`: loads and validates the demo asset inventory.
- `services/fortyguard.py`: single integration point for live FortyGuard data or cached demo data.
- `risk/scoring.py`: calculates the 0-100 score and factor-by-factor explanation.
- `assetshield_backend.py`: builds the structured ranked report for Streamlit, React, or the AI Copilot.
- `api_server.py`: exposes the backend over HTTP for the frontend.

## Remaining Work

- Connect these endpoints to the frontend dashboard UI.
- Connect the same structured facts to the AssetShield Copilot.
- Capture a few real successful FortyGuard responses and store them as clearly labelled cached demo data for final presentation reliability.
- Expand tests once the frontend and copilot integration are added.
