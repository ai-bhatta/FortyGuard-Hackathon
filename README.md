# AssetShield AI

AssetShield AI is a hackathon MVP that turns FortyGuard climate intelligence into operational heat-risk priorities for California outdoor industrial assets. It loads demo assets, fetches or reuses clearly labelled climate data, calculates an explainable 0-100 heat exposure score, and exposes the result through a FastAPI backend, a Streamlit local dashboard, and a Vercel-ready static web UI.

This is a transparent inspection-priority model. It does not predict exact equipment failure.

## Current Status

Done:

- California demo asset dataset with 12 assets in `data/assets.csv`.
- Cached California climate demo data in `data/fortyguard_cache.json`.
- FortyGuard API client wrapper in `fortyguard/`.
- Reusable service layer in `services/fortyguard.py`.
- Asset loading and validation in `services/assets.py`.
- Explainable scoring engine in `risk/scoring.py`.
- Risk levels: Low, Moderate, High, Critical.
- Maintenance recommendations: Monitor, Review during next maintenance window, Schedule Inspection, Prioritize Inspection.
- Backend report builder in `assetshield_backend.py`.
- FastAPI endpoints in `api_server.py`.
- Streamlit dashboard in `frontend/app.py`.
- Vercel-ready static dashboard in `web/`.
- Automated tests for scoring, backend payloads, and API endpoints.
- `uv` project setup with `pyproject.toml` and `uv.lock`.
- Node build scripts for Vercel in `package.json` and `scripts/`.

Still optional / future work:

- Verify live FortyGuard calls with a real API key.
- Replace cached demo data with cached responses captured from real successful FortyGuard California requests.
- Connect the copilot to a real LLM if the team wants richer natural-language answers.

## Project Structure

```text
.
|-- api_server.py              # FastAPI HTTP API for frontend integration
|-- assetshield_backend.py     # CLI/report builder
|-- data/
|   |-- assets.csv             # California demo asset inventory
|   `-- fortyguard_cache.json  # cached demo climate data
|-- fortyguard/                # FortyGuard API client
|-- frontend/                  # Streamlit dashboard
|-- web/                       # static dashboard for Vercel
|-- scripts/                   # static web build/local server scripts
|-- risk/                      # scoring and classification logic
|-- services/                  # asset loading and FortyGuard service layer
|-- tests/                     # pytest suite
|-- package.json               # Vercel/static UI scripts
|-- pyproject.toml             # uv project dependencies
|-- vercel.json                # Vercel deployment config
`-- uv.lock                    # locked dependency versions
```

## Setup

Install dependencies with `uv`:

```bash
uv sync
```

Create a local `.env` file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Add your FortyGuard key in `.env`:

```env
FORTYGUARD_API_KEY=your_real_key_here
FORTYGUARD_BASE_URL=https://api.fortyguard.com
ASSETSHIELD_USE_LIVE_API=false
ASSETSHIELD_CACHE_PATH=data/fortyguard_cache.json
```

Keep `ASSETSHIELD_USE_LIVE_API=false` for stable cached demo mode. Set it to `true` when testing live FortyGuard data.

## Local Testing Guide

### 1. Run Automated Tests

```bash
uv run pytest
```

Expected result:

```text
11 passed
```

### 2. Test The Backend CLI

```bash
uv run python assetshield_backend.py
```

Expected behavior: the command prints California assets ranked by risk score, highest first.

### 3. Start The FastAPI Backend

```bash
uv run uvicorn api_server:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Useful endpoints:

- `GET /health`
- `GET /assets`
- `GET /risks`
- `GET /risks?risk_level=High`
- `GET /risks?asset_type=Telecom`
- `GET /risks/{asset_id}`

Example:

```text
http://127.0.0.1:8000/risks/A001
```

To test live FortyGuard mode, set your API key in `.env`, set `ASSETSHIELD_USE_LIVE_API=true`, then call:

```text
http://127.0.0.1:8000/risks?live=true
```

### 4. Run The Streamlit Dashboard

In a second terminal:

```bash
uv run streamlit run frontend/app.py
```

Expected behavior: Streamlit opens a local dashboard with KPI cards, filters, an asset map, a ranked risk table, asset details, and a lightweight AssetShield Copilot.

### 5. Test The Vercel Web UI Locally

Build the static web app:

```bash
npm run build
```

Serve the static UI locally:

```bash
npm run dev
```

On Windows PowerShell, use:

```powershell
npm.cmd run dev
```

Open:

```text
http://localhost:3000
```

Expected behavior: the browser shows a polished AssetShield operations dashboard with KPI cards, filters, map-style asset markers, a selected asset details panel, a risk ranking table, and copilot prompt buttons.

By default, the static UI uses bundled demo data copied into `dist/data/`. If a deployed backend URL is available, set it in `web/index.html` before building:

```html
<script>
  window.ASSETSHIELD_API_BASE_URL = "https://your-backend-url.example.com";
</script>
```

### 6. Deploy The Web UI On Vercel

From this repo, Vercel should use:

```text
Build Command: npm run build
Output Directory: dist
```

These are already configured in `vercel.json`.

If the FastAPI backend is hosted separately, add that backend URL to `window.ASSETSHIELD_API_BASE_URL` in `web/index.html` before deploying. If no hosted backend is available, the Vercel UI still works as a demo using bundled California cache data.

### 7. Frontend Handoff Notes

The frontend can either:

- Import local Python data through `frontend/data.py`.
- Call the FastAPI endpoints from `api_server.py`.
- Use the static Vercel UI in `web/` for the deployed demo.

For a cleaner team split, use the HTTP API as the contract:

- Dashboard cards: derive counts from `GET /risks`.
- Map markers: use `latitude`, `longitude`, `risk_level`, and `risk_score` from `GET /risks`.
- Asset detail panel: use `GET /risks/{asset_id}`.
- Filters: call `GET /risks?risk_level=...` and `GET /risks?asset_type=...`.

## Notes

- Do not commit `.env`.
- `.venv/`, `__pycache__/`, and `.pytest_cache/` are ignored.
- `dist/` and `node_modules/` are ignored.
- Cached data must be labelled as cached demo data during demos.
- The score is for heat exposure prioritization, not failure prediction.
