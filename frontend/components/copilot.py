import os
import streamlit as st
import pandas as pd

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def build_fallback_response(user_query: str, df: pd.DataFrame) -> str:
    """Generates a structured, deterministic analytical response when OpenAI quota is unavailable."""
    if df.empty:
        return "⚠️ **No Telemetry Available**: No asset data matches your currently selected dashboard filters."

    query_lower = user_query.lower()
    critical_df = df[df['risk_level'].str.upper() == 'CRITICAL'] if 'risk_level' in df.columns else pd.DataFrame()

    if "critical" in query_lower or "breakdown" in query_lower:
        if critical_df.empty:
            return "✅ **No Critical Risk Detected**: All currently monitored assets are operating within acceptable thermal parameters."

        output = ["### 🔥 Critical Thermal Risk Analysis\n"]
        for _, row in critical_df.iterrows():
            margin = row.get('temperature', 0) - row.get('threshold', 0)
            output.append(
                f"* **{row.get('asset_name', 'Asset')}** (`{row.get('asset_id', 'N/A')}`)\n"
                f"  * **FortyGuard Telemetry:** Measured `{row.get('temperature', 0):.1f}°C` vs safe threshold `{row.get('threshold', 0):.1f}°C` (**+{margin:.1f}°C overload**).\n"
                f"  * **Risk Exposure Score:** `{row.get('risk_score', 0)}/100` (`CRITICAL`).\n"
                f"  * **Root Cause:** Extended ambient heat exposure exceeding design envelope for over `{row.get('hours_above_threshold', 0)}` consecutive operational hours."
            )
        return "\n".join(output)

    elif "maintenance" in query_lower or "action plan" in query_lower or "plan" in query_lower:
        top_assets = df.sort_values("risk_score", ascending=False).head(3)
        output = ["### 🛠️ Prioritized Preventive Maintenance Protocol\n"]

        idx = 1
        for _, row in top_assets.iterrows():
            output.append(
                f"**Step {idx}: Inspect & Cool {row.get('asset_name')} (`{row.get('asset_id')}`)**\n"
                f"* **Current Risk Score:** `{row.get('risk_score', 0)}/100` | Temp: `{row.get('temperature', 0):.1f}°C`\n"
                f"* **Action:** Deploy auxiliary evaporative cooling units, inspect heat exchangers for dust blockage, and apply localized thermal insulation shielding.\n"
            )
            idx += 1
        return "\n".join(output)

    elif "why" in query_lower:
        matched = None
        for _, row in df.iterrows():
            if str(row.get("asset_name", "")).lower() in query_lower:
                matched = row
                break
        target = matched if matched is not None else df.sort_values("risk_score", ascending=False).iloc[0]
        margin = target.get('temperature', 0) - target.get('threshold', 0)
        return (
            f"### 🔎 Risk Explanation: {target.get('asset_name')}\n"
            f"* **Recorded Temperature:** `{target.get('temperature', 0):.1f}°C` vs threshold `{target.get('threshold', 0):.1f}°C` "
            f"(**{margin:+.1f}°C margin**)\n"
            f"* **Criticality:** `{target.get('criticality', 'N/A')}`\n"
            f"* **Hours Above Limit:** `{target.get('hours_above_threshold', 0)}`\n"
            f"* **Heat Exposure Score:** `{target.get('risk_score', 0)}/100` → **{target.get('risk_level', 'N/A')}**\n\n"
            f"This asset's score reflects thermal severity above threshold, exposure duration, and its business criticality rating — not a failure prediction."
        )

    else:
        top_asset = df.sort_values("risk_score", ascending=False).iloc[0]
        return (
            f"### ⚡ FortyGuard Thermal Risk Summary\n"
            f"* **Highest Thermal Risk Asset:** **{top_asset.get('asset_name')}** (`{top_asset.get('asset_id')}`)\n"
            f"* **Recorded Temperature:** `{top_asset.get('temperature', 0):.1f}°C` against safe threshold `{top_asset.get('threshold', 0):.1f}°C`\n"
            f"* **Heat Exposure Score:** `{top_asset.get('risk_score', 0)}/100`\n\n"
            f"**Recommended Action:** Shed high operational loads during peak daily heat waves and perform infrared thermal scanning on electrical junctions."
        )


def query_openai(messages: list, df: pd.DataFrame) -> str:
    """Queries OpenAI API with fallback to local rule engine upon quota errors."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", None)
        except Exception:
            api_key = None

    if not api_key or not HAS_OPENAI:
        return build_fallback_response(messages[-1]["content"], df)

    try:
        client = OpenAI(api_key=api_key)

        context_str = df.to_json(orient="records")
        system_prompt = (
            "You are AssetShield AI, an industrial thermal engineer powered by FortyGuard heat data. "
            f"Here is the active telemetry dataset: {context_str}. Answer queries with strict factual detail."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            temperature=0.2,
            max_tokens=600,
        )
        return response.choices[0].message.content
    except Exception:
        return build_fallback_response(messages[-1]["content"], df)


def show_copilot(df: pd.DataFrame):
    """Renders the AssetShield Copilot Interface."""
    st.markdown('<div class="section-title">AssetShield Copilot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Ask technical questions about heat exposure, asset risk factors, and recommended maintenance protocols.</div>',
        unsafe_allow_html=True,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am **AssetShield AI**, your thermal intelligence co-pilot. "
                    "How can I assist you with asset risk diagnostics, threshold violations, or maintenance planning today?"
                ),
            }
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("**Suggested Quick Queries:**")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)

    selected_query = None
    if q_col1.button("🔥 Critical Assets Risk Breakdown"):
        selected_query = "Which assets are currently in critical condition, what are their FortyGuard temperatures versus thresholds, and why?"
    if q_col2.button("🛠️ Recommended Maintenance Plan"):
        selected_query = "Provide a prioritized step-by-step preventive maintenance action plan for the top 3 highest risk assets."
    if q_col3.button("⚡ High Ambient Heat Impact"):
        selected_query = "Summarize how current ambient heat levels are affecting equipment longevity and operational efficiency across all monitored assets."
    if q_col4.button("🗑️ Clear Chat"):
        st.session_state.messages = st.session_state.messages[:1]
        st.rerun()

    pending_question = st.session_state.pop("pending_copilot_question", None)

    user_input = st.chat_input("Ask a diagnostic question about your assets...")
    prompt = user_input or selected_query or pending_question

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing FortyGuard telemetry..."):
                formatted_history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                answer = query_openai(formatted_history, df)
                st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})