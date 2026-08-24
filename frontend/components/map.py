import streamlit as st
import pandas as pd


RISK_COLORS = {
    "Critical": [220, 38, 38],
    "High": [234, 88, 12],
    "Moderate": [245, 158, 11],
    "Low": [34, 197, 94],
}


def show_map(df):

    st.markdown(
        '<div class="section-title">📍 Asset Risk Map</div>',
        unsafe_allow_html=True,
    )

    if df.empty:

        st.info(
            "No assets match the selected filters."
        )

        return

    map_df = df.copy()

    map_df["color"] = map_df["risk_level"].map(
        RISK_COLORS
    )

    map_df["size"] = (
        map_df["risk_score"] / 4
    ).clip(lower=5)

    st.map(
        map_df,
        latitude="latitude",
        longitude="longitude",
        color="color",
        size="size",
    )

    st.caption(
        "🔴 Critical   🟠 High   🟡 Moderate   🟢 Low"
    )