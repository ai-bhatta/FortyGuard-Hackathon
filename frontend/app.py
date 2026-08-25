import os
import sys
import streamlit as st

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from frontend.components.asset_details import show_asset_details
from frontend.components.copilot import show_copilot
from frontend.components.kpis import show_kpis
from frontend.components.map import show_map
from frontend.components.risk_chart import show_risk_chart
from frontend.components.risk_table import show_risk_table
from frontend.data import load_asset_data
from frontend.styles import load_styles

st.set_page_config(
    page_title="AssetShield AI - FortyGuard Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_styles()

# Header Banner
st.markdown(
    """<div class="app-header">
<div>
<div class="brand">
AssetShield AI
</div>
<div class="brand-subtitle">
Powered by FortyGuard Hyperlocal Temperature Intelligence
</div>
</div>
</div>""",
    unsafe_allow_html=True,
)

try:
    df = load_asset_data()
except Exception as error:
    st.error("Unable to load asset telemetry data.")
    st.exception(error)
    st.stop()

# Sidebar Setup
st.sidebar.title("AssetShield AI")
st.sidebar.caption("Industrial Operations Center")
st.sidebar.divider()
st.sidebar.subheader("Filters")

risk_options = ["All", "Critical", "High", "Moderate", "Low"]
selected_risk = st.sidebar.selectbox("Risk Level Category", risk_options)

asset_types = sorted(df["asset_type"].dropna().unique().tolist())
selected_type = st.sidebar.selectbox("Asset Type", ["All"] + asset_types)

search_text = st.sidebar.text_input("Search Asset Name", placeholder="e.g. Transformer A")

# Filtering Data
filtered_df = df.copy()

if selected_risk != "All":
    filtered_df = filtered_df[filtered_df["risk_level"] == selected_risk]

if selected_type != "All":
    filtered_df = filtered_df[filtered_df["asset_type"] == selected_type]

if search_text:
    filtered_df = filtered_df[
        filtered_df["asset_name"].str.contains(search_text, case=False, na=False)
    ]

st.sidebar.divider()
st.sidebar.caption(f"Displaying {len(filtered_df)} of {len(df)} registered assets")

# Section 1: Executive KPI Summary
show_kpis(filtered_df)

if not filtered_df.empty:
    highest = filtered_df.sort_values("risk_score", ascending=False).iloc[0]
    st.markdown(
        f"""<div class="safety-alert">
<div class="safety-title">Priority Maintenance Alert</div>
<div class="safety-text">
<strong>{highest['asset_name']}</strong> ({highest['asset_id']}) is currently exhibiting the highest thermal exposure with a Heat Exposure Score of <strong>{highest['risk_score']}/100</strong>. Recorded FortyGuard temperature is <strong>{highest['temperature']:.1f}°C</strong> against a configured threshold of <strong>{highest['threshold']:.1f}°C</strong>.
</div>
</div>""",
        unsafe_allow_html=True,
    )

# Transition 1
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# Section 2: Distribution & Geospatial Analysis
col1, col2 = st.columns([1, 1])
with col1:
    show_risk_chart(filtered_df)
with col2:
    show_map(filtered_df)

# Transition 2
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# Section 3: Ranked Risk Table
show_risk_table(filtered_df)

# Transition 3
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# Section 4: Detailed Asset Technical Diagnostics
show_asset_details(filtered_df)

# Transition 4
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# Section 5: AssetShield AI Copilot
show_copilot(filtered_df)

# Footer
st.markdown(
    """<div class="app-footer">
AssetShield AI • Hyperlocal Temperature Intelligence via FortyGuard API
</div>""",
    unsafe_allow_html=True,
)