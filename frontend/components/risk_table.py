import pandas as pd
import streamlit as st


def show_risk_table(df: pd.DataFrame):
    st.markdown('<div class="section-title">Interactive Risk Ranking Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Click headers to sort, select any row to highlight asset telemetry, or search dynamically.</div>',
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("No asset records available for the selected filters.")
        return

    # Keep only flat scalar columns so PyArrow can convert the DataFrame properly
    columns_to_keep = [
        "asset_id",
        "asset_name",
        "asset_type",
        "risk_score",
        "risk_level",
        "temperature",
        "threshold",
        "hours_above_threshold",
        "criticality",
    ]
    
    valid_cols = [col for col in columns_to_keep if col in df.columns]
    display_df = df[valid_cols].sort_values(by="risk_score", ascending=False).reset_index(drop=True)

    event = st.dataframe(
        display_df,
        column_config={
            "asset_id": st.column_config.TextColumn("Asset ID", help="Unique Equipment Identification"),
            "asset_name": st.column_config.TextColumn("Asset Name"),
            "asset_type": st.column_config.TextColumn("Type"),
            "temperature": st.column_config.NumberColumn(
                "Temp (°C)",
                format="%.1f °C",
                help="FortyGuard Hyperlocal Thermal Reading",
            ),
            "threshold": st.column_config.NumberColumn("Threshold (°C)", format="%.1f °C"),
            "hours_above_threshold": st.column_config.NumberColumn("Over Limit (hrs)"),
            "risk_score": st.column_config.ProgressColumn(
                "Heat Exposure Score",
                help="0 = Low Risk, 100 = Severe Thermal Risk",
                format="%d/100",
                min_value=0,
                max_value=100,
            ),
            "risk_level": st.column_config.SelectboxColumn(
                "Risk Rating",
                options=["Critical", "High", "Moderate", "Low"],
            ),
            "criticality": st.column_config.TextColumn("Criticality Level"),
        },
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    selected_rows = event.selection.get("rows", [])
    if selected_rows:
        selected_index = selected_rows[0]
        selected_asset_name = display_df.iloc[selected_index]["asset_name"]
        st.success(f"Selected Asset: **{selected_asset_name}**")