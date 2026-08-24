import streamlit as st


def show_asset_details(df):
    st.markdown(
        '<div class="section-title">🔎 Asset Details</div>',
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("Select different filters to view assets.")
        return

    asset_names = df["asset_name"].tolist()

    selected_name = st.selectbox(
        "Select an asset",
        asset_names,
        key="asset_selector",
    )

    asset = df[df["asset_name"] == selected_name].iloc[0]

    left, right = st.columns([1, 2])

    with left:
        st.markdown(f"### {asset['asset_name']}")
        st.write(f"**Asset ID:** {asset['asset_id']}")
        st.write(f"**Type:** {asset['asset_type']}")
        st.write(
            f"**Location:** "
            f"{asset['latitude']:.5f}, "
            f"{asset['longitude']:.5f}"
        )

    with right:
        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Temperature",
                f"{asset['temperature']:.1f}°C",
            )

        with c2:
            st.metric(
                "Threshold",
                f"{asset['threshold']:.1f}°C",
            )

        with c3:
            st.metric(
                "Risk Score",
                int(asset["risk_score"]),
            )

    difference = asset["temperature"] - asset["threshold"]

    if difference > 0:
        st.error(f"⚠️ This asset is {difference:.1f}°C above its threshold.")
    else:
        st.success("✓ Temperature is currently within the configured threshold.")

    if asset["risk_level"] == "Critical":
        st.markdown(
            """<div class="safety-alert">
    <div class="safety-title">
        🚨 Immediate attention required
    </div>
    <div class="safety-text">
        This asset has reached a critical climate-risk level. Review operating conditions and schedule inspection.
    </div>
</div>""",
            unsafe_allow_html=True,
        )

    elif asset["risk_level"] == "High":
        st.warning(
            "⚠️ Elevated risk. Monitor this asset closely during peak temperature periods."
        )

    elif asset["risk_level"] == "Moderate":
        st.info("Monitor this asset as environmental conditions change.")

    else:
        st.success("✓ No immediate climate-related action is indicated.")