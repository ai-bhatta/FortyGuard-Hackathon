import os
import sys
import streamlit as st

# Add the root directory to sys.path so modules resolve cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Component and helper imports
from frontend.components.asset_details import show_asset_details
from frontend.components.copilot import show_copilot
from frontend.components.kpis import show_kpis
from frontend.components.map import show_map
from frontend.components.risk_chart import show_risk_chart
from frontend.components.risk_table import show_risk_table
from frontend.data import load_asset_data
from frontend.styles import load_styles

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="AssetShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# CUSTOM STYLING
# ==========================================================

load_styles()

st.markdown(
    """<div class="app-header">
<div>
<div class="brand">
🛡️ AssetShield AI
</div>
<div class="brand-subtitle">
Industrial Climate Risk Intelligence
</div>
</div>
</div>""",
    unsafe_allow_html=True,
)

# ==========================================================
# LOAD DATA
# ==========================================================

try:
    df = load_asset_data()
except Exception as error:
    st.error("Unable to load asset data.")
    st.exception(error)
    st.stop()


# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("AssetShield AI")
st.sidebar.caption("Industrial Operations Center")
st.sidebar.divider()
st.sidebar.subheader("Filters")

# Risk filter
risk_options = [
    "All",
    "Critical",
    "High",
    "Moderate",
    "Low",
]

selected_risk = st.sidebar.selectbox(
    "Risk Level",
    risk_options,
)

# Asset type filter
asset_types = sorted(df["asset_type"].dropna().unique().tolist())

selected_type = st.sidebar.selectbox(
    "Asset Type",
    ["All"] + asset_types,
)

# Search
search_text = st.sidebar.text_input(
    "Search Asset",
    placeholder="e.g. Compressor C-14",
)


# ==========================================================
# APPLY FILTERS (filtered_df IS CREATED HERE)
# ==========================================================

filtered_df = df.copy()

if selected_risk != "All":
    filtered_df = filtered_df[filtered_df["risk_level"] == selected_risk]

if selected_type != "All":
    filtered_df = filtered_df[filtered_df["asset_type"] == selected_type]

if search_text:
    filtered_df = filtered_df[
        filtered_df["asset_name"].str.contains(
            search_text,
            case=False,
            na=False,
        )
    ]


# ==========================================================
# STATUS
# ==========================================================

st.sidebar.divider()
st.sidebar.caption(f"Showing {len(filtered_df)} of {len(df)} assets")


# ==========================================================
# MAIN KPI AREA
# ==========================================================

show_kpis(filtered_df)

st.write("")
st.divider()


# ==========================================================
# MORNING SAFETY NOTE
# ==========================================================

if not filtered_df.empty:
    highest = filtered_df.sort_values(
        "risk_score",
        ascending=False,
    ).iloc[0]

    st.markdown(
        f"""<div class="safety-alert">
<div class="safety-title">
☀️ Morning Safety Note
</div>
<div class="safety-text">
<strong>{highest['asset_name']}</strong> currently has the highest climate risk with a score of <strong>{highest['risk_score']}/100</strong>. Current temperature is <strong>{highest['temperature']:.1f}°C</strong> against a threshold of <strong>{highest['threshold']:.1f}°C</strong>. Review this asset before peak heat conditions.
</div>
</div>""",
        unsafe_allow_html=True,
    )

st.divider()


# ==========================================================
# RISK CHART & MAP (SIDE BY SIDE)
# ==========================================================

col1, col2 = st.columns([1, 1])

with col1:
    show_risk_chart(filtered_df)

with col2:
    show_map(filtered_df)

st.divider()


# ==========================================================
# RISK TABLE
# ==========================================================

show_risk_table(filtered_df)

st.divider()


# ==========================================================
# ASSET DETAILS
# ==========================================================

show_asset_details(filtered_df)

st.divider()


# ==========================================================
# AI COPILOT
# ==========================================================

show_copilot(filtered_df)


# ==========================================================
# FOOTER
# ==========================================================

st.markdown(
    """<div class="app-footer">
AssetShield AI • Climate-aware industrial asset intelligence
</div>""",
    unsafe_allow_html=True,
)