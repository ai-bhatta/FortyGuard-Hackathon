import streamlit as st


def show_kpis(df):

    if "risk_filter" not in st.session_state:
        st.session_state["risk_filter"] = "All"

    total = len(df)
    critical = len(df[df["risk_level"] == "Critical"])
    high = len(df[df["risk_level"] == "High"])
    moderate = len(df[df["risk_level"] == "Moderate"])
    low = len(df[df["risk_level"] == "Low"])

    active = st.session_state["risk_filter"]
    columns = st.columns(5)

    metrics = [
        ("All", "Total Assets", total, "All monitored assets"),
        ("Critical", "Critical", critical, "Immediate attention"),
        ("High", "High", high, "Elevated risk"),
        ("Moderate", "Moderate", moderate, "Monitor closely"),
        ("Low", "Low", low, "Within normal range"),
    ]

    for column, metric in zip(columns, metrics):

        filter_value, label, value, description = metric

        with column:

            is_active = active == filter_value
            border = "2px solid #38bdf8" if is_active else "1px solid rgba(255,255,255,0.08)"

            st.markdown(
                f"""
                <div class="metric-card" style="border: {border};">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-description">
                        {description}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            btn_label = "✓ Active" if is_active else "Filter"
            if st.button(btn_label, key=f"kpi_filter_{filter_value}", use_container_width=True):
                st.session_state["risk_filter"] = filter_value
                st.rerun()