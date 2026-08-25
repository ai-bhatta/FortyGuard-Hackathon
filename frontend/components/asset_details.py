import pandas as pd
import streamlit as st

ASSET_DESCRIPTIONS = {
    "Transformer": "Step-up/step-down high-voltage electrical transformer. Converts electrical energy between circuits to maintain grid distribution stability.",
    "Electrical Cabinet": "Outdoor metal enclosure housing circuit breakers, switches, and power distribution controls exposed to ambient solar heat radiation.",
    "EV Charger": "High-power DC fast-charging station for electric vehicles. Generates high internal thermal output during active power transfer.",
    "Generator": "Backup diesel or natural gas generator providing emergency microgrid power. Requires strict ambient heat thresholds during peak runs.",
    "Telecom Cabinet": "Enclosed wireless node cabinet housing cellular base station transceivers, fiber switches, and emergency battery backups.",
    "Solar Inverter": "Photovoltaic power inverter converting direct current (DC) from solar arrays into grid-ready alternating current (AC).",
    "Battery System": "Industrial lithium-ion battery energy storage system (BESS). Highly sensitive to thermal runaway risks at high ambient temperatures.",
    "HVAC Equipment": "Industrial chilled water unit / rooftop compressor cooling critical indoor data equipment or facilities.",
    "Pump": "High-volume fluid transfer pump operating outdoor fluid pipelines or municipal water supply networks.",
}


def show_asset_details(df: pd.DataFrame):
    st.markdown('<div class="section-title">Asset Operational Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Deep technical inspection and risk breakdowns for targeted equipment.</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("No assets selected.")
        return

    asset_list = df["asset_name"].tolist()
    selected_name = st.selectbox("Select Asset for Deep Technical Diagnostics", asset_list)

    asset = df[df["asset_name"] == selected_name].iloc[0]

    # Calculate thermal margin
    thermal_margin = asset["threshold"] - asset["temperature"]
    margin_color = "#ef4444" if thermal_margin < 0 else ("#f97316" if thermal_margin < 3 else "#10b981")

    # Safe conversion for integer criticality ratings
    criticality_str = str(asset.get("criticality", "N/A"))

    # Asset functional description lookup
    asset_type = asset.get("asset_type", "Equipment")
    functional_desc = ASSET_DESCRIPTIONS.get(
        asset_type, "Outdoor critical industrial infrastructure asset monitored for thermal exposure."
    )

    # Render Detailed Technical Profile
    st.markdown(
        f"""
        <div class="asset-detail-card">
            <div class="asset-detail-title">{asset['asset_name']} <span style="font-size: 0.9rem; color: #9ca3af; font-family: 'Inter', sans-serif;">(ID: {asset['asset_id']})</span></div>
            <p style="color: #cbd5e1; font-size: 0.92rem; margin-bottom: 1rem; line-height: 1.5;">
                <b>Product Function:</b> {functional_desc}
            </p>
            <div class="asset-detail-subtext">
                <b>Equipment Type:</b> {asset_type} &nbsp;|&nbsp; 
                <b>Operational Age:</b> {asset['age_years']} Years &nbsp;|&nbsp; 
                <b>Criticality Rating:</b> {criticality_str} &nbsp;|&nbsp;
                <b>Operational Status:</b> {asset.get('status', 'Active')}
            </div>
            <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 1rem 0;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;">
                <div>
                    <div style="font-size: 0.75rem; color: #9ca3af; text-transform: uppercase; font-weight: 600;">FortyGuard Temp</div>
                    <div style="font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: #ffffff;">{asset['temperature']:.1f}°C</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #9ca3af; text-transform: uppercase; font-weight: 600;">Heat Threshold</div>
                    <div style="font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: #ffffff;">{asset['threshold']:.1f}°C</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #9ca3af; text-transform: uppercase; font-weight: 600;">Time Above Limit</div>
                    <div style="font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: #ffffff;">{asset.get('hours_above_threshold', 0)} hrs</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #9ca3af; text-transform: uppercase; font-weight: 600;">Thermal Margin</div>
                    <div style="font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: {margin_color};">{thermal_margin:+.1f}°C</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Detailed Engineering Breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.5); padding: 1.2rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08);">
                <h4 style="font-family: 'Playfair Display', serif; color: #f3f4f6; margin-top: 0;">Risk Diagnostics & Telemetry</h4>
                <ul style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.7; padding-left: 1.2rem;">
                    <li><b>Heat Exposure Score:</b> {asset['risk_score']}/100</li>
                    <li><b>Risk Level Category:</b> {asset['risk_level']}</li>
                    <li><b>Historical Overheat Incidents:</b> {asset.get('past_heat_incidents', 0)} logged events</li>
                    <li><b>Coordinates:</b> Lat {asset['latitude']:.4f}, Long {asset['longitude']:.4f}</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.5); padding: 1.2rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08);">
                <h4 style="font-family: 'Playfair Display', serif; color: #f3f4f6; margin-top: 0;">Prescriptive Maintenance Protocol</h4>
                <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6;">
                    <b>System Explanation:</b><br/>
                    {asset['asset_name']} is being monitored via FortyGuard thermal telemetry. Its operating temperature is compared against its rated ceiling of {asset['threshold']}°C. Based on its {criticality_str.lower()} business criticality, preventive inspection is recommended.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )