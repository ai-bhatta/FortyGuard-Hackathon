const API_BASE_URL = (window.ASSETSHIELD_API_BASE_URL || "").replace(/\/$/, "");

const state = {
  risks: [],
  filtered: [],
  selectedId: null,
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
  state.selectedId = state.risks[0]?.asset_id || null;
  populateTypeFilter();
  bindEvents();
  applyFilters();
  answerPrompt("inspect");
}

function initTheme() {
  const savedTheme = localStorage.getItem("assetshield-theme");
  const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
  setTheme(savedTheme || (prefersDark ? "dark" : "light"));
  $("theme-toggle").addEventListener("click", () => {
    const nextTheme = document.body.dataset.theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
  });
}

function setTheme(theme) {
  document.body.dataset.theme = theme;
  localStorage.setItem("assetshield-theme", theme);
  const isDark = theme === "dark";
  $("theme-icon").textContent = isDark ? "Sun" : "Moon";
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
      if (!response.ok) throw new Error(`Backend returned ${response.status}`);
      $("data-mode").textContent = "Live backend";
      $("data-caption").textContent = API_BASE_URL;
      return await response.json();
    } catch (error) {
      $("data-mode").textContent = "Demo fallback";
      $("data-caption").textContent = "Backend unavailable, using bundled data";
    }
  }
  return loadBundledRisks();
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
    throw new Error(`${path} returned ${response.status}. Run npm.cmd run build before serving the static UI.`);
  }
  return response.text();
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}. Run npm.cmd run build before serving the static UI.`);
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
  const severityPoints = clamp((severityDelta / 10) * 30, 0, 30);
  const exposurePoints = clamp((Number(weather.hours_above_threshold) / 8) * 25, 0, 25);
  const criticalityPoints = clamp((Number(asset.criticality) / 5) * 20, 0, 20);
  const agePoints = clamp((Number(asset.age_years) / 15) * 15, 0, 15);
  const incidentPoints = clamp(Number(asset.past_heat_incidents) * 2.5, 0, 10);
  const riskScore = Math.round(
    severityPoints + exposurePoints + criticalityPoints + agePoints + incidentPoints,
  );
  const riskLevel = classifyRisk(riskScore);

  return {
    asset_id: asset.asset_id,
    asset_name: asset.asset_name,
    asset_type: asset.asset_type,
    latitude: Number(asset.latitude),
    longitude: Number(asset.longitude),
    temperature_celsius: Number(weather.temperature_celsius),
    apparent_temperature_celsius: apparent,
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
      factor("Temperature severity", severityDelta, severityPoints, 30),
      factor("Time above threshold", Number(weather.hours_above_threshold), exposurePoints, 25),
      factor("Asset criticality", Number(asset.criticality), criticalityPoints, 20),
      factor("Asset age", Number(asset.age_years), agePoints, 15),
      factor("Past heat incidents", Number(asset.past_heat_incidents), incidentPoints, 10),
    ],
  };
}

function factor(name, value, points, maxPoints) {
  return { name, value, points: Number(points.toFixed(1)), max_points: maxPoints };
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

function clamp(value, min, max) {
  return Math.max(min, Math.min(value, max));
}

function populateTypeFilter() {
  const select = $("type-filter");
  const types = [...new Set(state.risks.map((item) => item.asset_type))].sort();
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
    state.selectedId = state.filtered[0]?.asset_id || state.risks[0]?.asset_id;
    render();
  });
  document.querySelectorAll("[data-prompt]").forEach((button) => {
    button.addEventListener("click", () => answerPrompt(button.dataset.prompt));
  });
}

function applyFilters() {
  const risk = $("risk-filter").value;
  const type = $("type-filter").value;
  const search = $("asset-search").value.trim().toLowerCase();
  state.filtered = state.risks.filter((item) => {
    const riskMatch = risk === "All" || item.risk_level === risk;
    const typeMatch = type === "All" || item.asset_type === type;
    const searchMatch = !search
      || item.asset_name.toLowerCase().includes(search)
      || item.asset_id.toLowerCase().includes(search);
    return riskMatch && typeMatch && searchMatch;
  });
  if (!state.filtered.some((item) => item.asset_id === state.selectedId)) {
    state.selectedId = state.filtered[0]?.asset_id || state.risks[0]?.asset_id;
  }
  render();
}

function render() {
  renderKpis();
  renderMap();
  renderTable();
  renderDetails();
}

function renderKpis() {
  const counts = {
    "Total Assets": state.filtered.length,
    Critical: countRisk("Critical"),
    High: countRisk("High"),
    Moderate: countRisk("Moderate"),
    Low: countRisk("Low"),
  };
  $("kpi-grid").innerHTML = Object.entries(counts).map(([label, value]) => `
    <div class="kpi-card">
      <span>${label}</span>
      <strong>${value}</strong>
    </div>
  `).join("");
}

function countRisk(level) {
  return state.filtered.filter((item) => item.risk_level === level).length;
}

function renderMap() {
  $("visible-count").textContent = `${state.filtered.length} assets`;
  const canvas = $("map-canvas");
  const lats = state.risks.map((item) => item.latitude);
  const lngs = state.risks.map((item) => item.longitude);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLng = Math.min(...lngs);
  const maxLng = Math.max(...lngs);

  canvas.innerHTML = state.filtered.map((item) => {
    const x = 8 + ((item.longitude - minLng) / (maxLng - minLng || 1)) * 84;
    const y = 8 + ((maxLat - item.latitude) / (maxLat - minLat || 1)) * 84;
    const size = 14 + item.risk_score / 8;
    return `
      <button
        class="map-point ${item.risk_level}"
        style="left:${x}%;top:${y}%;width:${size}px;height:${size}px"
        title="${item.asset_name}: ${item.risk_score}/100"
        data-id="${item.asset_id}">
      </button>
    `;
  }).join("");

  canvas.querySelectorAll(".map-point").forEach((point) => {
    point.addEventListener("click", () => {
      state.selectedId = point.dataset.id;
      render();
    });
  });
}

function renderTable() {
  const rows = state.filtered.map((item, index) => `
    <tr data-id="${item.asset_id}" class="${item.asset_id === state.selectedId ? "selected" : ""}">
      <td>${index + 1}</td>
      <td><strong>${item.asset_name}</strong><br><small>${item.asset_id}</small></td>
      <td>${item.asset_type}</td>
      <td>${item.temperature_celsius.toFixed(1)} C</td>
      <td>${item.threshold_celsius.toFixed(1)} C</td>
      <td><span class="score-pill">${item.risk_score}</span></td>
      <td><span class="badge ${item.risk_level}">${item.risk_level}</span></td>
    </tr>
  `).join("");
  $("risk-table").innerHTML = rows || `<tr><td colspan="7"><div class="empty-state">No assets match the current filters.</div></td></tr>`;

  $("risk-table").querySelectorAll("tr[data-id]").forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedId = row.dataset.id;
      render();
    });
  });
}

function renderDetails() {
  const item = state.risks.find((risk) => risk.asset_id === state.selectedId);
  if (!item) {
    $("detail-panel").innerHTML = `<div class="empty-state">Select an asset to view details.</div>`;
    return;
  }
  $("detail-panel").innerHTML = `
    <div class="asset-title">
      <div>
        <p class="eyebrow">${item.asset_id} / ${item.asset_type}</p>
        <h3>${item.asset_name}</h3>
      </div>
      <span class="badge ${item.risk_level}">${item.risk_level}</span>
    </div>
    <div class="score-ring" style="--score:${item.risk_score};--accent:${riskColors[item.risk_level]}">
      <div>${item.risk_score}</div>
    </div>
    <div class="metric-list">
      <div class="mini-metric"><span>Temperature</span><strong>${item.temperature_celsius.toFixed(1)} C</strong></div>
      <div class="mini-metric"><span>Threshold</span><strong>${item.threshold_celsius.toFixed(1)} C</strong></div>
      <div class="mini-metric"><span>Above Threshold</span><strong>${item.hours_above_threshold} hrs</strong></div>
      <div class="mini-metric"><span>Criticality</span><strong>${item.criticality}/5</strong></div>
    </div>
    <div class="recommendation">${item.recommendation}</div>
    <div class="factor-list">
      ${item.factors.map((factorItem) => `
        <div class="factor-row">
          <div>
            <strong>${factorItem.name.replaceAll("_", " ")}</strong>
            <div class="bar"><span style="width:${(factorItem.points / factorItem.max_points) * 100}%"></span></div>
          </div>
          <small>${factorItem.points}/${factorItem.max_points}</small>
        </div>
      `).join("")}
    </div>
  `;
}

function answerPrompt(prompt) {
  const top = state.filtered[0] || state.risks[0];
  const critical = state.filtered.filter((item) => item.risk_level === "Critical");
  const high = state.filtered.filter((item) => item.risk_level === "High");
  const above = state.filtered.filter((item) => item.apparent_temperature_celsius > item.threshold_celsius);
  let answer = "";

  if (!top) {
    answer = "No asset data is available.";
  } else if (prompt === "inspect") {
    answer = `<strong>${top.asset_name}</strong> should be reviewed first. It has a ${top.risk_score}/100 heat exposure score, ${top.hours_above_threshold} hours above threshold, and a recommendation to ${top.recommendation.toLowerCase()}.`;
  } else if (prompt === "above") {
    answer = above.length
      ? `${above.length} assets are above their configured heat threshold: ${above.slice(0, 5).map((item) => item.asset_id).join(", ")}.`
      : "No visible assets are currently above their configured heat threshold.";
  } else {
    answer = `The visible portfolio has ${critical.length} critical and ${high.length} high-risk assets. The highest priority is <strong>${top.asset_name}</strong>. These scores prioritize heat exposure and inspection attention, not certain equipment failure.`;
  }
  $("copilot-answer").innerHTML = answer;
}

init().catch((error) => {
  document.body.innerHTML = `<main class="empty-state">Unable to load AssetShield data: ${error.message}</main>`;
});
