import pandas as pd
import pydeck as pdk
import streamlit as st


def show_map(df: pd.DataFrame):
    st.markdown('<div class="section-title">🗺️ Interactive Asset Map</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("No location data available.")
        return

    # Map risk levels to RGB colors for Pydeck
    def get_color(level):
        colors = {
            "Critical": [239, 68, 68, 200],
            "High": [249, 115, 22, 200],
            "Moderate": [234, 179, 8, 200],
            "Low": [34, 197, 94, 200],
        }
        return colors.get(level, [59, 130, 246, 200])

    map_df = df.copy()
    map_df["color"] = map_df["risk_level"].apply(get_color)

    # Initial view centered on data average
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

    # Render interactive map with selection listener
    event = st.pydeck_chart(deck, on_select="rerun", selection_mode="single-object")

    # If user clicks an asset on the map, display selected product info box
    if event and event.selection and event.selection.get("objects"):
        selected_data = event.selection["objects"].get("ScatterplotLayer")
        if selected_data:
            item = selected_data[0]
            st.markdown(
                f"""
                <div class="safety-alert" style="border-left-color: #38bdf8; background: #0f172a; border: 1px solid #38bdf8;">
                    <div class="safety-title" style="color: #38bdf8;">📍 Selected Asset: {item['asset_name']} ({item['asset_id']})</div>
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