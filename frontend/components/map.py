import pandas as pd
import pydeck as pdk
import streamlit as st

# Same thermal-red family used in risk_chart.py, converted to RGBA
RISK_COLORS = {
    "Critical": [127, 29, 29, 220],   # #7f1d1d
    "High": [220, 38, 38, 210],       # #dc2626
    "Moderate": [248, 113, 113, 200], # #f87171
    "Low": [254, 202, 202, 190],      # #fecaca
}


def show_map(df: pd.DataFrame):
    st.markdown('<div class="section-title">🗺️ Interactive Asset Map</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("No location data available.")
        return

    def get_color(level):
        return RISK_COLORS.get(level, [148, 163, 184, 200])

    map_df = df.copy()
    map_df["color"] = map_df["risk_level"].apply(get_color)

    view_state = pdk.ViewState(
        latitude=map_df["latitude"].mean(),
        longitude=map_df["longitude"].mean(),
        zoom=10,
        pitch=45,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        map_df,
        get_position=["longitude", "latitude"],
        get_fill_color="color",
        get_radius=120,
        pickable=True,
        auto_highlight=True,
        radius_min_pixels=8,
        radius_max_pixels=25,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>{asset_name}</b> ({asset_id})<br/>"
                    "Type: {asset_type}<br/>"
                    "Risk Score: <b>{risk_score}/100</b> ({risk_level})<br/>"
                    "Temp: {temperature}°C (Threshold: {threshold}°C)",
            "style": {"color": "white", "backgroundColor": "#0f172a", "fontSize": "12px", "padding": "8px", "borderRadius": "8px"},
        },
    )

    event = st.pydeck_chart(deck, on_select="rerun", selection_mode="single-object")

    # Only update the stored selection when a NEW click actually happened.
    # This is what prevents the card from vanishing on unrelated reruns.
    if event and event.selection and event.selection.get("objects"):
        selected_data = event.selection["objects"].get("ScatterplotLayer")
        if selected_data:
            st.session_state["selected_map_asset"] = selected_data[0]
            st.session_state["selected_asset_id"] = selected_data[0]["asset_id"]

    # Always render from session_state, not from the live event — so it persists
    # across reruns triggered by filters, nav clicks, etc.
    item = st.session_state.get("selected_map_asset")
    if item:
        jump_col1, jump_col2 = st.columns([5, 1])
        with jump_col1:
            st.markdown(
                f"""
                <div class="safety-alert" style="border-left-color: #f87171; background: #0f172a; border: 1px solid #f87171;">
                    <div class="safety-title" style="color: #f87171;">📍 Selected Asset: {item['asset_name']} ({item['asset_id']})</div>
                    <div class="safety-text" style="color: #cbd5e1;">
                        <b>Product Type:</b> {item['asset_type']}<br/>
                        <b>Current Risk:</b> {item['risk_score']}/100 ({item['risk_level']})<br/>
                        <b>Operational Temp:</b> {item['temperature']}°C / Threshold: {item['threshold']}°C<br/>
                        <b>Recommendation:</b> {item.get('recommendation', 'Inspect thermal insulation')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with jump_col2:
            st.write("")
            if st.button("✕ Clear", key="clear_map_selection", use_container_width=True):
                st.session_state["selected_map_asset"] = None
                st.rerun()