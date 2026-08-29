import pandas as pd
import streamlit as st


def build_default_response(prompt_key: str, df: pd.DataFrame) -> str:
    if df.empty:
        return "**No Telemetry Available:** No asset data matches the current filters."

    ordered = df.sort_values("risk_score", ascending=False)
    top_asset = ordered.iloc[0]
    critical_df = ordered[ordered["risk_level"].str.upper() == "CRITICAL"]
    high_df = ordered[ordered["risk_level"].str.upper() == "HIGH"]
    above_threshold = ordered[ordered["temperature"] > ordered["threshold"]]

    if prompt_key == "critical":
        if critical_df.empty:
            return "**No Critical Risk Detected:** No visible assets are currently classified as critical."

        lines = ["### Critical Asset Breakdown"]
        for _, row in critical_df.iterrows():
            margin = row.get("temperature", 0) - row.get("threshold", 0)
            lines.append(
                f"- **{row.get('asset_name', 'Asset')}** (`{row.get('asset_id', 'N/A')}`): "
                f"{row.get('risk_score', 0)}/100 risk score, "
                f"{row.get('temperature', 0):.1f} C vs {row.get('threshold', 0):.1f} C threshold "
                f"({margin:+.1f} C margin)."
            )
        return "\n".join(lines)

    if prompt_key == "maintenance":
        lines = ["### Prioritized Maintenance Plan"]
        for index, (_, row) in enumerate(ordered.head(3).iterrows(), start=1):
            lines.append(
                f"{index}. **{row.get('asset_name')}** (`{row.get('asset_id')}`): "
                f"{row.get('risk_score', 0)}/100, {row.get('risk_level')}. "
                "Inspect cooling, ventilation, electrical load, and heat shielding."
            )
        return "\n".join(lines)

    return (
        "### Heat Exposure Summary\n"
        f"- Highest priority asset: **{top_asset.get('asset_name')}** (`{top_asset.get('asset_id')}`) "
        f"with a {top_asset.get('risk_score', 0)}/100 score.\n"
        f"- Visible portfolio: {len(critical_df)} critical, {len(high_df)} high-risk, "
        f"and {len(above_threshold)} assets above threshold.\n"
        "- These scores prioritize inspection attention based on heat exposure; they are not failure predictions."
    )


def show_copilot(df: pd.DataFrame):
    st.markdown('<div class="section-title">AssetShield Copilot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Use the default demo queries to review heat exposure, critical assets, and maintenance priority.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("**Default Demo Queries:**")
    q_col1, q_col2, q_col3 = st.columns(3)

    selected_prompt = st.session_state.get("selected_copilot_prompt", "maintenance")
    if q_col1.button("Critical Asset Breakdown", use_container_width=True):
        selected_prompt = "critical"
    if q_col2.button("Recommended Maintenance Plan", use_container_width=True):
        selected_prompt = "maintenance"
    if q_col3.button("Heat Exposure Summary", use_container_width=True):
        selected_prompt = "summary"

    st.session_state["selected_copilot_prompt"] = selected_prompt
    st.markdown(build_default_response(selected_prompt, df))
