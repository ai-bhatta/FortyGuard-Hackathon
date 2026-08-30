# AssetShield AI

AssetShield AI is a project built for the FortyGuard Hackathon by team **Asset Guards**.

Team members:

- Aimy Acksa Shaji 
- Taima Hoque 
- Asma Ahmed 

## Project Overview

AssetShield AI helps operators understand which outdoor industrial assets are most exposed to heat and should be inspected first.

Many companies manage equipment that sits outside all day, such as EV chargers, telecom nodes, transformers, pumps, solar inverters, batteries, sensors, HVAC units, and port equipment. During extreme heat, teams may not have enough time or staff to inspect everything at once. AssetShield AI turns location-based climate data into a simple operational priority list.

The system uses FortyGuard climate intelligence for U.S.-based locations and demonstrates the workflow with California industrial assets. It calculates an explainable heat exposure score from 0 to 100, assigns a risk level, and recommends what the maintenance team should do next.

AssetShield AI does **not** claim that equipment will fail. It prioritizes heat exposure and inspection attention.

## The Problem

Outdoor industrial assets are exposed to rising temperatures, direct sunlight, and long periods of heat stress. Maintenance teams often need to answer practical questions quickly:

- Which assets need attention today?
- Which assets are above their heat threshold?
- Which locations have the highest heat exposure?
- Why is one asset more urgent than another?
- What should the team inspect first?

Without a clear ranking system, teams may rely on manual checks, scattered spreadsheets, or incomplete local weather information.

## The Solution

AssetShield AI combines asset data with FortyGuard temperature intelligence to create a heat-risk operations dashboard.

The application:

- Loads a portfolio of California demo assets.
- Uses cached demo climate data by default for reliable demos.
- Can be configured to use the live FortyGuard API.
- Calculates a transparent 0-100 heat exposure score.
- Classifies assets as Low, Moderate, High, or Critical.
- Provides maintenance recommendations such as Monitor, Schedule Inspection, or Prioritize Inspection.
- Shows risk information in a dashboard, interactive map view, ranked table, and asset detail panel.
- Includes an AssetShield Copilot demo area with default queries and deterministic built-in answers.

## How The Score Works

The score is a transparent prioritization model. It considers:

- Temperature severity: how far apparent temperature is above the asset threshold.
- Time above threshold: how many hours the asset has elevated heat exposure.
- Asset criticality: how important the asset is to operations.
- Asset age: older assets receive more attention in this demo model.
- Past heat incidents: previous issues add extra priority.

Each asset receives:

- `risk_score`: a number from 0 to 100.
- `risk_level`: Low, Moderate, High, or Critical.
- `recommendation`: a maintenance action.
- `factors`: a breakdown explaining where the score came from.

## Current Features

- California demo asset dataset with 12 assets.
- FortyGuard API client wrapper.
- FastAPI backend endpoints for frontend integration.
- Streamlit dashboard for local Python testing.
- Vercel-ready static web dashboard.
- Light mode and dark mode in the Vercel UI.
- KPI cards for total, critical, high, moderate, and low assets.
- Interactive Leaflet/OpenStreetMap asset risk map for panning, zooming, and marker selection.
- Ranked asset risk table.
- Asset detail panel with score breakdown.
- Copilot prompt buttons with default demo answers.
- Cached demo data fallback for stable hackathon demos.
- Automated tests for scoring, backend payloads, and API endpoints.

## Business Aspect

AssetShield AI is positioned as a B2B SaaS product for organizations that manage outdoor infrastructure.

Potential customers:

- Utility companies
- Telecom operators
- EV charging networks
- Solar farm operators
- Industrial facility operators
- Port and logistics operators
- Equipment manufacturers

Value proposition:

- Helps teams prioritize limited maintenance resources.
- Converts climate data into operational decisions.
- Reduces guesswork during heat events.
- Gives managers an explainable reason for inspection priority.
- Supports future integration with asset management and work order systems.

Possible business model:

- Subscription pricing based on number of monitored assets or sites.
- Enterprise plans for API integrations, custom thresholds, and reporting.
- Future add-ons for automated alerts, historical trend analysis, and work-order routing.

## Tech Stack

Backend:

- Python
- FastAPI
- FortyGuard API client
- `requests`
- `python-dotenv`
- `pytest`

Frontend:

- Streamlit for local Python dashboard testing
- Static HTML, CSS, and JavaScript for the Vercel-ready web UI
- Leaflet with OpenStreetMap tiles for the interactive Vercel map
- Vercel static deployment

Data and tooling:

- CSV demo asset inventory
- JSON cached climate data
- `uv` for Python dependency management
- Node.js scripts for static web build and local serving

## Project Structure

```text
.
|-- api_server.py              # FastAPI HTTP API
|-- assetshield_backend.py     # CLI report builder
|-- data/
|   |-- assets.csv             # California demo asset inventory
|   `-- fortyguard_cache.json  # cached demo climate data
|-- fortyguard/                # FortyGuard API client
|-- frontend/                  # Streamlit dashboard
|-- web/                       # Vercel-ready static dashboard
|-- scripts/                   # static web build and dev server scripts
|-- risk/                      # scoring and classification logic
|-- services/                  # asset loading and FortyGuard service layer
|-- tests/                     # pytest suite
|-- package.json               # web UI scripts
|-- pyproject.toml             # uv project dependencies
|-- vercel.json                # Vercel deployment config
`-- uv.lock                    # locked Python dependency versions
```

## Local Setup

Install Python dependencies:

```bash
uv sync
```

Create a local environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Add your FortyGuard API key in `.env`:

```env
FORTYGUARD_API_KEY=your_real_key_here
FORTYGUARD_BASE_URL=https://api.fortyguard.com
ASSETSHIELD_USE_LIVE_API=false
ASSETSHIELD_CACHE_PATH=data/fortyguard_cache.json
ASSETSHIELD_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Keep `ASSETSHIELD_USE_LIVE_API=false` for cached demo mode. Set it to `true` only when testing live FortyGuard calls.

## How To Test Locally

### 1. Run Automated Tests

```bash
uv run pytest
```

Expected result:

```text
11 passed
```

### 2. Run The Backend CLI

```bash
uv run python assetshield_backend.py
```

This prints California assets ranked by heat exposure score.

### 3. Run The FastAPI Backend

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

### 4. Run The Streamlit Dashboard

```bash
uv run streamlit run frontend/app.py
```

This is useful for local Python-based testing and quick demos.

### 5. Run The Vercel-Ready Web UI Locally

Build and serve the static dashboard:

```bash
npm run dev
```

On Windows PowerShell:

```powershell
npm.cmd run dev
```

Open the URL printed in the terminal. It usually starts at:

```text
http://localhost:3000
```

If port 3000 is busy, the script will try the next available port, such as:

```text
http://localhost:3001
```

The static UI copilot uses built-in demo answers for the default queries, so it does not require an AI API key.
The Vercel map uses Leaflet and OpenStreetMap tiles, so the real basemap requires internet access in the browser.

## Vercel Deployment

The Vercel-ready frontend lives in `web/`.

Live demo:

```text
https://fortyguardhackathon.vercel.app/
```
