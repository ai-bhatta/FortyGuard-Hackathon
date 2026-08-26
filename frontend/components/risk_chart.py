import altair as alt
import pandas as pd
import streamlit as st


def show_risk_chart(df: pd.DataFrame):
    if df.empty:
        st.info("No asset data available to display risk distribution.")
        return

    chart_df = df[["risk_level"]].copy()

    color_scale = alt.Scale(
        domain=["Critical", "High", "Moderate", "Low"],
        range=["#ef4444", "#f97316", "#eab308", "#22c55e"],
    )

    chart = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X(
                "risk_level:N",
                sort=["Critical", "High", "Moderate", "Low"],
                title="Risk Level Category",
                axis=alt.Axis(labelColor="#cbd5e1", titleColor="#ffffff"),
            ),
            y=alt.Y(
                "count():Q",
                title="Number of Assets",
                axis=alt.Axis(labelColor="#cbd5e1", titleColor="#ffffff"),
            ),
            color=alt.Color(
                "risk_level:N", scale=color_scale, legend=None
            ),
            tooltip=[
                alt.Tooltip("risk_level:N", title="Risk Category"),
                alt.Tooltip("count():Q", title="Total Count"),
            ],
        )
        .properties(height=260)
        .configure(background="transparent")
        .configure_view(strokeWidth=0)
    )

    st.markdown('<div class="section-title">Risk Level Distribution</div>', unsafe_allow_html=True)
    st.altair_chart(chart, use_container_width=True)