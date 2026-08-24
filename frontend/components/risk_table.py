import streamlit as st


def show_risk_table(df):

    st.markdown(
        '<div class="section-title">🏆 Asset Risk Ranking</div>',
        unsafe_allow_html=True,
    )

    if df.empty:

        st.info(
            "No assets match the current filters."
        )

        return

    ranked = df.sort_values(
        "risk_score",
        ascending=False,
    ).copy()

    ranked.insert(
        0,
        "Rank",
        range(1, len(ranked) + 1),
    )

    display_df = ranked[
        [
            "Rank",
            "asset_id",
            "asset_name",
            "asset_type",
            "temperature",
            "threshold",
            "risk_score",
            "risk_level",
        ]
    ].copy()

    display_df["temperature"] = (
        display_df["temperature"].round(1)
    )

    display_df["threshold"] = (
        display_df["threshold"].round(1)
    )

    display_df = display_df.rename(
        columns={
            "asset_id": "Asset ID",
            "asset_name": "Asset",
            "asset_type": "Type",
            "temperature": "Temp °C",
            "threshold": "Threshold °C",
            "risk_score": "Score",
            "risk_level": "Status",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Risk Score",
                min_value=0,
                max_value=100,
                format="%d",
            ),
        },
    )