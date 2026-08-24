import streamlit as st


def show_kpis(df):

    total = len(df)

    critical = len(
        df[df["risk_level"] == "Critical"]
    )

    high = len(
        df[df["risk_level"] == "High"]
    )

    moderate = len(
        df[df["risk_level"] == "Moderate"]
    )

    low = len(
        df[df["risk_level"] == "Low"]
    )

    columns = st.columns(5)

    metrics = [
        ("Total Assets", total, "All monitored assets"),
        ("Critical", critical, "Immediate attention"),
        ("High", high, "Elevated risk"),
        ("Moderate", moderate, "Monitor closely"),
        ("Low", low, "Within normal range"),
    ]

    for column, metric in zip(columns, metrics):

        label, value, description = metric

        with column:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-description">
                        {description}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )