const configuredApiBaseUrl = (window.ASSETSHIELD_API_BASE_URL || "").replace(/\/$/, "");
const localApiBaseUrl = ["localhost", "127.0.0.1"].includes(window.location.hostname)
  ? "http://127.0.0.1:8000"
  : "";
const API_BASE_URL = configuredApiBaseUrl || localApiBaseUrl;

const state = {
  risks: [],
  filtered: [],
  selectedId: null,
  map: null,
  markerLayer: null,
  tileLayer: null,
  legendControl: null,
  shouldFitMap: true,
};

const riskOrder = ["Critical", "High", "Moderate", "Low"];

const riskColors = {
  Critical: "#dc2626",
  High: "#ea580c",
  Moderate: "#d97706",
  Low: "#16a34a",
};

const $ = (id) => document.getElementById(id);

async function init() {
  initTheme();

  state.risks = await loadRisks();

  updateFortyGuardBadge();

  state.selectedId = state.risks[0]?.asset_id || null;

  populateTypeFilter();
  bindEvents();

  applyFilters();

  await answerPrompt("inspect");
}

function initTheme() {
  const savedTheme = localStorage.getItem("assetshield-theme");
  const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;

  setTheme(savedTheme || (prefersDark ? "dark" : "light"));

  $("theme-toggle").addEventListener("click", () => {
    const nextTheme =
      document.body.dataset.theme === "dark" ? "light" : "dark";

    setTheme(nextTheme);
  });
}

function setTheme(theme) {
  document.body.dataset.theme = theme;
  localStorage.setItem("assetshield-theme", theme);

  const isDark = theme === "dark";

  $("theme-icon").src = isDark
    ? "/assets/sun.svg"
    : "/assets/moon.svg";

  $("theme-toggle").setAttribute(
    "aria-label",
    isDark ? "Switch to light mode" : "Switch to dark mode",
  );

  $("theme-toggle").setAttribute(
    "title",
    isDark ? "Switch to light mode" : "Switch to dark mode",
  );
}

async function loadRisks() {
  if (API_BASE_URL) {
    try {
      const response = await fetch(`${API_BASE_URL}/risks`);

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const data = await response.json();

      if (!Array.isArray(data) || data.length === 0) {
        throw new Error("Backend returned no assets");
      }

      $("data-mode").textContent = "Live backend";
      $("data-caption").textContent = API_BASE_URL;

      return data;
    } catch (error) {
      console.error(
        "AssetShield: live backend unavailable, falling back to bundled demo data —",
        error,
      );

      $("data-mode").textContent = "Demo fallback";
      $("data-caption").textContent =
        "Backend unavailable, using bundled data";
    }
  }

  try {
    return await loadBundledRisks();
  } catch (error) {
    console.error(
      "AssetShield: bundled demo data failed to load —",
      error,
    );

    $("data-mode").textContent = "Data unavailable";
    $("data-caption").textContent = error.message;

    return [];
  }
}

async function loadBundledRisks() {
  const [assetsCsv, cache] = await Promise.all([
    fetchText("/data/assets.csv"),
    fetchJson("/data/fortyguard_cache.json"),
  ]);

  return parseCsv(assetsCsv)
    .map((asset) => scoreAsset(asset, cache[asset.asset_id]))
    .sort((a, b) => b.risk_score - a.risk_score);
}

async function fetchText(path) {
  const response = await fetch(path);

  if (!response.ok) {
    throw new Error(
      `${path} returned ${response.status}. Run npm.cmd run build before serving the static UI.`,
    );
  }

  return response.text();
}

async function fetchJson(path) {
  const response = await fetch(path);

  if (!response.ok) {
    throw new Error(
      `${path} returned ${response.status}. Run npm.cmd run build before serving the static UI.`,
    );
  }

  return response.json();
}

function parseCsv(csv) {
  const [headerLine, ...lines] = csv.trim().split(/\r?\n/);
  const headers = headerLine.split(",");

  return lines.map((line) => {
    const values = line.split(",");

    return headers.reduce((row, header, index) => {
      row[header] = values[index];
      return row;
    }, {});
  });
}

function scoreAsset(asset, weather) {
  const threshold = Number(asset.heat_threshold_celsius);
  const apparent = Number(weather.apparent_temperature_celsius);

  const severityDelta = apparent - threshold;

  const severityPoints = clamp(
    (severityDelta / 10) * 30,
    0,
    30,
  );

  const exposurePoints = clamp(
    (Number(weather.hours_above_threshold) / 8) * 25,
    0,
    25,
  );

  const criticalityPoints = clamp(
    (Number(asset.criticality) / 5) * 20,
    0,
    20,
  );

  const agePoints = clamp(
    (Number(asset.age_years) / 15) * 15,
    0,
    15,
  );

  const incidentPoints = clamp(
    Number(asset.past_heat_incidents) * 2.5,
    0,
    10,
  );

  const riskScore = Math.round(
    severityPoints +
      exposurePoints +
      criticalityPoints +
      agePoints +
      incidentPoints,
  );

  const riskLevel = classifyRisk(riskScore);

  const forecastPeak =
    weather.forecast_peak_celsius !== undefined &&
    weather.forecast_peak_celsius !== ""
      ? Number(weather.forecast_peak_celsius)
      : Number(
          (
            apparent +
            Math.max(
              1.5,
              severityDelta > 0 ? severityDelta * 0.6 : 1.5,
            )
          ).toFixed(1),
        );

  return {
    asset_id: asset.asset_id,
    asset_name: asset.asset_name,
    asset_type: asset.asset_type,
    latitude: Number(asset.latitude),
    longitude: Number(asset.longitude),
    temperature_celsius: Number(weather.temperature_celsius),
    apparent_temperature_celsius: apparent,
    forecast_peak_celsius: forecastPeak,
    threshold_celsius: threshold,
    hours_above_threshold: Number(weather.hours_above_threshold),
    criticality: Number(asset.criticality),
    age_years: Number(asset.age_years),
    past_heat_incidents: Number(asset.past_heat_incidents),
    risk_score: riskScore,
    risk_level: riskLevel,
    recommendation: recommendation(riskLevel),
    data_source: weather.source,

    factors: [
      factor(
        "Temperature severity",
        severityDelta,
        severityPoints,
        30,
      ),

      factor(
        "Time above threshold",
        Number(weather.hours_above_threshold),
        exposurePoints,
        25,
      ),

      factor(
        "Asset criticality",
        Number(asset.criticality),
        criticalityPoints,
        20,
      ),

      factor(
        "Asset age",
        Number(asset.age_years),
        agePoints,
        15,
      ),

      factor(
        "Past heat incidents",
        Number(asset.past_heat_incidents),
        incidentPoints,
        10,
      ),
    ],
  };
}

function factor(name, value, points, maxPoints) {
  return {
    name,
    value,
    points: Number(points.toFixed(1)),
    max_points: maxPoints,
  };
}

function classifyRisk(score) {
  if (score < 25) return "Low";
  if (score < 50) return "Moderate";
  if (score < 75) return "High";

  return "Critical";
}

function recommendation(level) {
  return {
    Low: "Monitor",
    Moderate: "Review during next maintenance window",
    High: "Schedule Inspection",
    Critical: "Prioritize Inspection",
  }[level];
}

function recommendationDetail(level) {
  return {
    Low: {
      action: "Monitor",
      window: "Next routine inspection",
      detail:
        "No action needed right now. Keep this asset in the normal monitoring rotation and re-check if conditions change.",
    },

    Moderate: {
      action: "Review at next maintenance window",
      window: "Within 30–60 days",
      detail:
        "Add this asset to the queue for the next regularly scheduled maintenance visit rather than an emergency callout.",
    },

    High: {
      action: "Schedule inspection",
      window: "Within 1–2 weeks",
      detail:
        "Heat exposure is elevated enough to warrant a dedicated inspection ahead of the normal maintenance cycle.",
    },

    Critical: {
      action: "Prioritize inspection",
      window: "Within 48–72 hours",
      detail:
        "This asset is under severe heat stress. Treat it as an emergency or out-of-cycle maintenance priority.",
    },
  }[level];
}

function failureRisk(level) {
  return {
    Critical: {
      probability: "High — roughly 60–85%",
      downtime: "4–12+ hrs of unplanned downtime",
    },

    High: {
      probability: "Elevated — roughly 30–55%",
      downtime: "1–4 hrs of unplanned downtime",
    },

    Moderate: {
      probability: "Low-moderate — roughly 10–25%",
      downtime: "Minimal, if any",
    },

    Low: {
      probability: "Low — under 10%",
      downtime: "None expected",
    },
  }[level];
}

function riskEmoji(level) {
  return {
    Critical: "🔴",
    High: "🟠",
    Moderate: "🟡",
    Low: "🟢",
  }[level];
}

function temperatureExplainer(item) {
  const delta =
    item.apparent_temperature_celsius -
    item.threshold_celsius;

  const overUnder = delta >= 0 ? "above" : "below";

  return `
    The <strong>apparent temperature</strong> is what the asset
    actually experiences on site (it factors in humidity and
    heat load, not just the air temperature) — currently
    ${item.apparent_temperature_celsius.toFixed(1)}°C.

    Its <strong>heat threshold</strong> of
    ${item.threshold_celsius.toFixed(1)}°C is the safe operating
    limit set for this specific asset.

    Right now it is running
    ${Math.abs(delta).toFixed(1)}°C ${overUnder} that limit,
    and it has stayed there for
    <strong>${item.hours_above_threshold} hour${
      item.hours_above_threshold === 1 ? "" : "s"
    }</strong> today — the longer an asset sits above threshold,
    the more the risk score climbs.
  `;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(value, max));
}

function populateTypeFilter() {
  const select = $("type-filter");

  const types = [
    ...new Set(state.risks.map((item) => item.asset_type)),
  ].sort();

  for (const type of types) {
    const option = document.createElement("option");

    option.value = type;
    option.textContent = type;

    select.appendChild(option);
  }
}

function bindEvents() {
  $("risk-filter").addEventListener("change", applyFilters);

  $("type-filter").addEventListener("change", applyFilters);

  $("asset-search").addEventListener("input", applyFilters);

  $("reset-selection").addEventListener("click", () => {
    state.selectedId =
      state.filtered[0]?.asset_id ||
      state.risks[0]?.asset_id;

    state.shouldFitMap = true;

    render();
  });

  document
    .querySelectorAll("[data-prompt]")
    .forEach((button) => {
      button.addEventListener("click", () =>
        answerPrompt(button.dataset.prompt),
      );
    });
}

function applyFilters() {
  const risk = $("risk-filter").value;
  const type = $("type-filter").value;
  const search = $("asset-search").value
    .trim()
    .toLowerCase();

  state.filtered = state.risks.filter((item) => {
    const riskMatch =
      risk === "All" || item.risk_level === risk;

    const typeMatch =
      type === "All" || item.asset_type === type;

    const searchMatch =
      !search ||
      item.asset_name.toLowerCase().includes(search) ||
      item.asset_id.toLowerCase().includes(search);

    return riskMatch && typeMatch && searchMatch;
  });

  if (
    !state.filtered.some(
      (item) => item.asset_id === state.selectedId,
    )
  ) {
    state.selectedId =
      state.filtered[0]?.asset_id ||
      state.risks[0]?.asset_id;
  }

  state.shouldFitMap = true;

  render();
}

function render() {
  renderSummary();
  renderKpis();
  renderMap();
  renderTable();
  renderDetails();
}

function renderSummary() {
  const top = state.filtered[0] || state.risks[0];

  const average = state.filtered.length
    ? Math.round(
        state.filtered.reduce(
          (sum, item) => sum + item.risk_score,
          0,
        ) / state.filtered.length,
      )
    : 0;

  $("summary-top").textContent = top
    ? `${top.asset_id} / ${top.risk_level}`
    : "No assets";

  $("summary-average").textContent =
    state.filtered.length ? `${average}/100` : "--";
}

function renderKpis() {
  const counts = {
    "Total Assets": state.filtered.length,
    Critical: countRisk("Critical"),
    High: countRisk("High"),
    Moderate: countRisk("Moderate"),
    Low: countRisk("Low"),
  };

  $("kpi-grid").innerHTML = Object.entries(counts)
    .map(
      ([label, value]) => `
        <div class="kpi-card ${label.replaceAll(" ", "-")}">
          <span>${label}</span>
          <strong>${value}</strong>
        </div>
      `,
    )
    .join("");
}

function countRisk(level) {
  return state.filtered.filter(
    (item) => item.risk_level === level,
  ).length;
}

function isLiveFortyGuard() {
  return $("data-mode").textContent === "Live backend";
}

function updateFortyGuardBadge() {
  const pill = $("fortyguard-live-pill");

  if (!pill) return;

  pill.hidden = !isLiveFortyGuard();
}

/* =========================================================
   INTERACTIVE MAP
   ========================================================= */

function renderMap() {
  $("visible-count").textContent =
    `${state.filtered.length} assets`;

  const mapElement = $("map-canvas");

  if (!state.risks.length) {
    mapElement.innerHTML = `
      <div class="map-unavailable">
        <strong>No asset data loaded.</strong>
        <span>
          The FortyGuard backend and the bundled demo data
          (/data/assets.csv, /data/fortyguard_cache.json)
          were both unreachable.
        </span>
      </div>
    `;

    return;
  }

  if (!window.L) {
    mapElement.innerHTML = `
      <div class="map-unavailable">
        <strong>Interactive map could not load.</strong>
        <span>
          Check your internet connection because the web demo
          loads Leaflet and OpenStreetMap tiles from public CDNs.
        </span>
      </div>
    `;

    return;
  }

  /* Create the map only once */
  if (!state.map) {
    mapElement.innerHTML = "";

    state.map = L.map(mapElement, {
      center: [37.25, -119.75],
      zoom: 6,
      minZoom: 5,
      maxZoom: 15,

      maxBounds: [
        [32.1, -125.0],
        [42.5, -113.5],
      ],

      maxBoundsViscosity: 0.65,

      scrollWheelZoom: true,
      zoomControl: true,
    });

    state.tileLayer = L.tileLayer(
      "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        attribution:
          "&copy; OpenStreetMap contributors",

        maxZoom: 19,
      },
    ).addTo(state.map);

    state.markerLayer =
      L.layerGroup().addTo(state.map);

    state.legendControl =
      L.control({ position: "topright" });

    state.legendControl.onAdd = () => {
      const div = L.DomUtil.create(
        "div",
        "map-legend leaflet-map-legend",
      );

      div.innerHTML = riskOrder
        .map(
          (level) => `
            <span>
              <i class="${level}"></i>
              ${level}
            </span>
          `,
        )
        .join("");

      /*
       * Prevent clicks on the legend from being
       * interpreted as map clicks.
       */
      L.DomEvent.disableClickPropagation(div);

      return div;
    };

    state.legendControl.addTo(state.map);
  }

  /* Remove old markers before creating the current ones */
  state.markerLayer.clearLayers();

  state.filtered.forEach((item) => {
    const isSelected =
      item.asset_id === state.selectedId;

    /*
     * Create the clickable circle.
     */
    const marker = L.circleMarker(
      [item.latitude, item.longitude],
      {
        radius: isSelected
          ? 13
          : 8 + item.risk_score / 18,

        color: "#ffffff",

        weight: isSelected ? 5 : 3,

        fillColor:
          riskColors[item.risk_level],

        fillOpacity: 0.92,

        opacity: 1,

        bubblingMouseEvents: false,

        className: isSelected
          ? "risk-marker selected"
          : "risk-marker",
      },
    );

    /*
     * Tooltip when hovering.
     */
    marker.bindTooltip(
      `
        <strong>${escapeHtml(item.asset_name)}</strong>
        <br>
        ${escapeHtml(item.asset_type)}
        <br>
        ${item.risk_level} /
        ${item.risk_score}/100
        <br>
        <strong>Click to inspect</strong>
      `,
      {
        direction: "top",
        offset: [0, -8],
        sticky: true,
      },
    );

    /*
     * Popup shown when a circle is clicked.
     */
    marker.bindPopup(
      `
        <div class="asset-popup">

          <div class="asset-popup-header">
            <strong>
              ${escapeHtml(item.asset_name)}
            </strong>

            <span class="badge ${item.risk_level}">
              ${item.risk_level}
            </span>
          </div>

          <div class="asset-popup-id">
            ${escapeHtml(item.asset_id)}
            · ${escapeHtml(item.asset_type)}
          </div>

          <div class="asset-popup-grid">

            <div>
              <span>Temperature</span>
              <strong>
                ${item.apparent_temperature_celsius.toFixed(1)}°C
              </strong>
            </div>

            <div>
              <span>Threshold</span>
              <strong>
                ${item.threshold_celsius.toFixed(1)}°C
              </strong>
            </div>

            <div>
              <span>Risk Score</span>
              <strong>
                ${item.risk_score}/100
              </strong>
            </div>

            <div>
              <span>Exposure</span>
              <strong>
                ${item.hours_above_threshold} hrs
              </strong>
            </div>

          </div>

          <button
            type="button"
            class="popup-button"
            data-asset-id="${escapeHtml(item.asset_id)}"
          >
            View Asset Details →
          </button>

        </div>
      `,
      {
        maxWidth: 320,
        minWidth: 260,
        className: "asset-popup-container",
      },
    );

    /*
     * MAIN CLICK HANDLER
     *
     * Clicking the circle:
     * 1. selects the asset
     * 2. prevents the map from treating it as a
     *    normal map click
     * 3. opens the popup
     * 4. updates the right-hand details panel
     */
    marker.on("click", (event) => {
      L.DomEvent.stopPropagation(event);

      state.selectedId = item.asset_id;

      /*
       * IMPORTANT:
       * Do NOT fit the map again after clicking.
       * Otherwise the map may jump around.
       */
      state.shouldFitMap = false;

      /*
       * Open popup immediately.
       */
      marker.openPopup();

      /*
       * Update the dashboard.
       */
      render();

      /*
       * render() recreates the markers, so the popup
       * above belongs to the old marker. Open the popup
       * again on the newly-created selected marker
       * on the next animation frame.
       */
      window.requestAnimationFrame(() => {
        const selectedMarker =
          findMarkerByAssetId(item.asset_id);

        if (selectedMarker) {
          selectedMarker.openPopup();
        }
      });
    });

    /*
     * When popup opens, attach the button's click event.
     */
    marker.on("popupopen", (event) => {
      const popupElement =
        event.popup.getElement();

      if (!popupElement) return;

      const button =
        popupElement.querySelector(
          ".popup-button",
        );

      if (!button) return;

      button.addEventListener("click", () => {
        state.selectedId =
          item.asset_id;

        state.shouldFitMap = false;

        render();

        window.requestAnimationFrame(() => {
          const selectedMarker =
            findMarkerByAssetId(item.asset_id);

          if (selectedMarker) {
            selectedMarker.openPopup();
          }
        });
      });
    });

    /*
     * Add marker to map.
     */
    marker.addTo(state.markerLayer);
  });

  /*
   * Fit map ONLY after filters change,
   * not when a user clicks a marker.
   */
  if (
    state.shouldFitMap &&
    state.filtered.length
  ) {
    const bounds = L.latLngBounds(
      state.filtered.map((item) => [
        item.latitude,
        item.longitude,
      ]),
    );

    state.map.fitBounds(
      bounds.pad(0.2),
      {
        maxZoom: 8,
        animate: true,
      },
    );

    state.shouldFitMap = false;
  }

  /*
   * Make sure Leaflet knows the map's actual size.
   */
  window.requestAnimationFrame(() => {
    if (state.map) {
      state.map.invalidateSize();
    }
  });
}

/*
 * Find the currently selected marker.
 *
 * This is used after render() because render()
 * recreates the marker objects.
 */
function findMarkerByAssetId(assetId) {
  if (!state.markerLayer) return null;

  let selectedMarker = null;

  state.markerLayer.eachLayer((layer) => {
    if (
      layer.options &&
      layer.options.assetId === assetId
    ) {
      selectedMarker = layer;
    }
  });

  /*
   * Fallback:
   * match by coordinates if assetId isn't attached.
   */
  if (!selectedMarker) {
    const item = state.filtered.find(
      (asset) => asset.asset_id === assetId,
    );

    if (!item) return null;

    state.markerLayer.eachLayer((layer) => {
      const latLng = layer.getLatLng?.();

      if (!latLng) return;

      if (
        Math.abs(latLng.lat - item.latitude) <
          0.000001 &&
        Math.abs(latLng.lng - item.longitude) <
          0.000001
      ) {
        selectedMarker = layer;
      }
    });
  }

  return selectedMarker;
}

/* =========================================================
   TABLE
   ========================================================= */

function renderTable() {
  const rows = state.filtered
    .map(
      (item, index) => `
        <tr
          data-id="${escapeHtml(item.asset_id)}"
          class="${item.risk_level} ${
            item.asset_id === state.selectedId
              ? "selected"
              : ""
          }"
        >

          <td>${index + 1}</td>

          <td>
            <strong>
              ${escapeHtml(item.asset_name)}
            </strong>
            <br>
            <small>
              ${escapeHtml(item.asset_id)}
            </small>
          </td>

          <td>
            ${escapeHtml(item.asset_type)}
          </td>

          <td>
            ${item.temperature_celsius.toFixed(1)}°C
          </td>

          <td>
            ${item.threshold_celsius.toFixed(1)}°C
          </td>

          <td>
            <span class="score-pill">
              ${item.risk_score}
            </span>
          </td>

          <td>
            <span class="badge ${item.risk_level}">
              ${item.risk_level}
            </span>
          </td>

        </tr>
      `,
    )
    .join("");

  $("risk-table").innerHTML =
    rows ||
    `
      <tr>
        <td colspan="7">
          <div class="empty-state">
            No assets match the current filters.
          </div>
        </td>
      </tr>
    `;

  $("risk-table")
    .querySelectorAll("tr[data-id]")
    .forEach((row) => {
      row.addEventListener("click", () => {
        state.selectedId =
          row.dataset.id;

        state.shouldFitMap = false;

        render();

        /*
         * Bring the selected marker into view.
         */
        window.requestAnimationFrame(() => {
          const item = state.risks.find(
            (asset) =>
              asset.asset_id ===
              row.dataset.id,
          );

          if (item && state.map) {
            state.map.panTo(
              [item.latitude, item.longitude],
              {
                animate: true,
              },
            );
          }
        });
      });
    });
}

/* =========================================================
   DETAILS PANEL
   ========================================================= */

function renderDetails() {
  const item = state.risks.find(
    (risk) =>
      risk.asset_id === state.selectedId,
  );

  if (!item) {
    $("detail-panel").innerHTML = `
      <div class="empty-state">
        Select an asset to view details.
      </div>
    `;

    return;
  }

  $("detail-panel").innerHTML = `
    <div class="asset-title">

      <div>
        <p class="eyebrow">
          ${escapeHtml(item.asset_id)}
          /
          ${escapeHtml(item.asset_type)}
        </p>

        <h3>
          ${escapeHtml(item.asset_name)}
        </h3>
      </div>

      <span class="badge ${item.risk_level}">
        ${item.risk_level}
      </span>

    </div>

    <div
      class="score-ring"
      style="
        --score:${item.risk_score};
        --accent:${riskColors[item.risk_level]}
      "
    >
      <div>
        ${item.risk_score}
      </div>
    </div>

    <div class="metric-list">

      <div class="mini-metric">
        <span>Temperature</span>
        <strong>
          ${item.temperature_celsius.toFixed(1)}°C
        </strong>
      </div>

      <div class="mini-metric">
        <span>Threshold</span>
        <strong>
          ${item.threshold_celsius.toFixed(1)}°C
        </strong>
      </div>

      <div class="mini-metric">
        <span>Above Threshold</span>
        <strong>
          ${item.hours_above_threshold} hrs
        </strong>
      </div>

      <div class="mini-metric">
        <span>Criticality</span>
        <strong>
          ${item.criticality}/5
        </strong>
      </div>

    </div>

    <p class="temp-explainer">
      ${temperatureExplainer(item)}
    </p>

    <div class="recommendation">

      <div class="recommendation-header">

        <strong>
          ${recommendationDetail(
            item.risk_level,
          ).action}
        </strong>

        <span class="recommendation-window">
          ${recommendationDetail(
            item.risk_level,
          ).window}
        </span>

      </div>

      <p>
        ${recommendationDetail(
          item.risk_level,
        ).detail}
      </p>

    </div>

    <div class="factor-list">

      ${item.factors
        .map(
          (factorItem) => `
            <div class="factor-row">

              <div>

                <strong>
                  ${escapeHtml(
                    factorItem.name.replaceAll(
                      "_",
                      " ",
                    ),
                  )}
                </strong>

                <div class="bar">
                  <span
                    style="
                      width:${
                        (factorItem.points /
                          factorItem.max_points) *
                        100
                      }%
                    "
                  ></span>
                </div>

              </div>

              <small>
                ${factorItem.points}/
                ${factorItem.max_points}
              </small>

            </div>
          `,
        )
        .join("")}

    </div>
  `;
}

/* =========================================================
   COPILOT
   ========================================================= */

function answerPrompt(prompt) {
  const top =
    state.filtered[0] ||
    state.risks[0];

  let bodyHtml;

  if (!top) {
    bodyHtml = `
      <div>
        ${escapeHtml(
          "No asset data is available.",
        )}
      </div>
    `;
  } else if (prompt === "inspect") {
    bodyHtml = decisionCardHtml(top);
  } else if (prompt === "whatif") {
    bodyHtml = whatIfHtml(top);
  } else {
    bodyHtml = `
      <div>
        ${formatAnswer(
          localCopilotAnswer(prompt),
        )}
      </div>
    `;
  }

  $("copilot-answer").innerHTML = `
    ${bodyHtml}

    <small class="answer-source">
      ${
        isLiveFortyGuard()
          ? "Live FortyGuard data"
          : "Default demo response"
      }
    </small>
  `;
}

function decisionCardHtml(item) {
  const detail =
    recommendationDetail(item.risk_level);

  const forecastExceeds =
    item.forecast_peak_celsius >
    item.threshold_celsius;

  const loadNote =
    item.risk_level === "Critical" ||
    item.risk_level === "High"
      ? " and reduce load where possible"
      : "";

  return `
    <div class="decision-card ${item.risk_level}">

      <div class="decision-head">

        <span class="decision-emoji">
          ${riskEmoji(item.risk_level)}
        </span>

        <span class="decision-title">
          ${item.risk_level.toUpperCase()}
          —
          ${escapeHtml(item.asset_name)}
        </span>

      </div>

      <div class="decision-rows">

        <div>
          <dt>Current temperature</dt>
          <dd>
            ${item.apparent_temperature_celsius.toFixed(1)}°C
          </dd>
        </div>

        <div>
          <dt>Forecast peak</dt>
          <dd>
            ${item.forecast_peak_celsius.toFixed(1)}°C
          </dd>
        </div>

        <div>
          <dt>Safe operating threshold</dt>
          <dd>
            ${item.threshold_celsius.toFixed(1)}°C
          </dd>
        </div>

        <div>
          <dt>Estimated exposure</dt>
          <dd>
            ${item.hours_above_threshold.toFixed(1)} hrs
          </dd>
        </div>

      </div>

      <div class="decision-recommendation">
        <strong>Recommendation:</strong>
        ${detail.action},
        ${detail.window.toLowerCase()}
        ${loadNote}.
      </div>

      <div class="decision-reason">
        <strong>Reason:</strong>
        ${
          forecastExceeds
            ? "Forecasted temperature exceeds this asset’s threshold"
            : "Current temperature is already past this asset’s threshold"
        }
        for an extended window, driving a
        ${item.risk_score}/100 risk score.
      </div>

    </div>
  `;
}

function whatIfHtml(item) {
  const risk =
    failureRisk(item.risk_level);

  const detail =
    recommendationDetail(item.risk_level);

  return `
    <div class="whatif-card">

      <p class="whatif-asset">
        ${escapeHtml(item.asset_name)}
        —
        ${item.risk_level}
        (${item.risk_score}/100)
      </p>

      <div class="whatif-columns">

        <div class="whatif-col do-nothing">

          <h4>
            If you do nothing
          </h4>

          <ol>

            <li>
              Temperature keeps tracking toward
              the forecast peak of
              ${item.forecast_peak_celsius.toFixed(1)}°C
            </li>

            <li>
              Asset stays above its
              ${item.threshold_celsius.toFixed(1)}°C
              threshold for
              ${item.hours_above_threshold.toFixed(1)}+
              hrs
            </li>

            <li>
              Failure likelihood:
              ${risk.probability}
            </li>

            <li>
              Potential downtime:
              ${risk.downtime}
            </li>

          </ol>

        </div>

        <div class="whatif-col intervene">

          <h4>
            Recommended intervention
          </h4>

          <ol>

            <li>
              ${detail.action},
              ${detail.window.toLowerCase()}
            </li>

            <li>
              Reduce load on the asset where possible
            </li>

            <li>
              Re-check apparent temperature
              after cooling/adjustment
            </li>

            <li>
              Return the asset to normal monitoring
              once risk drops
            </li>

          </ol>

        </div>

      </div>

      <p class="whatif-disclaimer">
        Failure likelihood and downtime are illustrative
        estimates based on risk level, not a certified
        reliability model.
      </p>

    </div>
  `;
}

function formatAnswer(answer) {
  return escapeHtml(
    answer || "No answer was returned.",
  ).replace(/\n/g, "<br>");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function localCopilotAnswer(prompt) {
  const top =
    state.filtered[0] ||
    state.risks[0];

  const critical =
    state.filtered.filter(
      (item) =>
        item.risk_level === "Critical",
    );

  const high =
    state.filtered.filter(
      (item) =>
        item.risk_level === "High",
    );

  const moderate =
    state.filtered.filter(
      (item) =>
        item.risk_level === "Moderate",
    );

  const above =
    state.filtered.filter(
      (item) =>
        item.apparent_temperature_celsius >
        item.threshold_celsius,
    );

  const needsMaintenance =
    state.filtered.filter(
      (item) =>
        item.risk_level === "Critical" ||
        item.risk_level === "High",
    );

  let answer = "";

  if (!top) {
    answer =
      "No asset data is available.";

  } else if (prompt === "inspect") {
    const topDetail =
      recommendationDetail(
        top.risk_level,
      );

    answer =
      `${top.asset_name} should be reviewed first. ` +
      `Its apparent temperature is ` +
      `${top.apparent_temperature_celsius.toFixed(1)}°C, ` +
      `which is ` +
      `${Math.abs(
        top.apparent_temperature_celsius -
          top.threshold_celsius,
      ).toFixed(1)}°C past its ` +
      `${top.threshold_celsius.toFixed(1)}°C heat threshold, ` +
      `and it has held that for ` +
      `${top.hours_above_threshold} hour(s) today — ` +
      `driving a ${top.risk_score}/100 heat exposure score. ` +
      `Recommended action: ` +
      `${topDetail.action.toLowerCase()}, ` +
      `${topDetail.window.toLowerCase()}.`;

  } else if (prompt === "above") {
    answer = above.length
      ? `${above.length} asset(s) are running hotter than their configured heat threshold — meaning the apparent temperature on site now exceeds the safe operating limit set for that equipment: ${above
          .slice(0, 5)
          .map((item) => item.asset_id)
          .join(", ")}. The longer they stay above threshold, the higher their risk score climbs.`
      : "No visible assets are currently above their configured heat threshold, meaning apparent temperatures are within each asset's safe operating range today.";

  } else if (prompt === "maintenance") {
    answer = needsMaintenance.length
      ? `${needsMaintenance.length} asset(s) should be scheduled for maintenance ahead of the normal cycle: ${needsMaintenance
          .slice(0, 5)
          .map(
            (item) =>
              `${item.asset_id} (${recommendationDetail(
                item.risk_level,
              ).window.toLowerCase()})`,
          )
          .join(
            ", ",
          )}. Critical assets should be booked within 48–72 hours as an emergency or out-of-cycle visit; High assets within 1–2 weeks. ${moderate.length} moderate-risk asset(s) can simply be added to the next regular maintenance window (30–60 days) instead of an urgent callout.`
      : "No assets currently need maintenance scheduled outside the normal cycle — moderate and low risk assets can stay on the standard rotation.";

  } else {
    answer =
      `The visible portfolio has ${critical.length} critical and ${high.length} high-risk assets out of ${state.filtered.length} shown. The highest priority is ${top.asset_name} at ${top.risk_score}/100. As a next step, critical assets should be booked for inspection within 48–72 hours and high-risk assets within 1–2 weeks; moderate and low-risk assets can stay on the standard maintenance rotation. These scores prioritize heat exposure and inspection attention, not certain equipment failure.`;
  }

  return answer;
}

init().catch((error) => {
  document.body.innerHTML = `
    <main class="empty-state">
      Unable to load AssetShield data:
      ${escapeHtml(error.message)}
    </main>
  `;
});
