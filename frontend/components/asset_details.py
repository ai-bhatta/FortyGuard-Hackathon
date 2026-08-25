import pandas as pd
import streamlit as st


def show_asset_details(df: pd.DataFrame):
    st.markdown('<div class="section-title">Asset Operational Intelligence</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("No assets selected.")
        return

    asset_list = df["asset_name"].tolist()
    selected_name = st.selectbox("Select Asset for Deep Technical Diagnostics", asset_list)

    asset = df[df["asset_name"] == selected_name].iloc[0]

    # Calculate thermal margin
    thermal_margin = asset["threshold"] - asset["temperature"]
    margin_color = "#ef4444" if thermal_margin < 0 else ("#f97316" if thermal_margin < 3 else "#10b981")

    # Ensure criticality handles numbers safely
    criticality_str = str(asset.get("criticality", "N/A"))

    # Render Asset Detailed Technical Profile
    st.markdown(
        f"""
        <div class="asset-detail-card">
            <div class="asset-detail-title">{asset['asset_name']} <span style="font-size: 0.9rem; color: #9ca3af; font-family: 'Inter', sans-serif;">(ID: {asset['asset_id']})</span></div>
            <div class="asset-detail-subtext">
                <b>Equipment Type:</b> {asset['asset_type']} &nbsp;|&nbsp; 
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
                <h4 style="font-family: 'Playfair Display', serif; color: #f3f4f6; margin-top: 0;">Risk Analysis & Diagnostics</h4>
                <ul style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.7; padding-left: 1.2rem;">
                    <li><b>Heat Exposure Score:</b> {asset['risk_score']}/100</li>
                    <li><b>Risk Level Category:</b> {asset['risk_level']}</li>
                    <li><b>Historical Heat Incidents:</b> {asset.get('past_heat_incidents', 0)} past events</li>
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
                    <b>System Reason / Explanation:</b><br/>
                    This asset is experiencing temperature conditions evaluated against its configured heat threshold of {asset['threshold']}°C. Due to its {criticality_str.lower()} criticality rating and thermal exposure duration, maintenance priority has been heightened.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )