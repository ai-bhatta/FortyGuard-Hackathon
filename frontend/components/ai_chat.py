import streamlit as st


def show_ai_chat(df):

    st.subheader("💬 Ask AssetShield AI")

    question = st.chat_input(
        "Ask about your industrial assets..."
    )

    if question:

        st.chat_message("user").write(question)

        high_risk = df[
            df["risk_level"].isin(
                ["High", "Extreme"]
            )
        ]

        if len(high_risk) > 0:

            most_at_risk = high_risk.sort_values(
                "risk_score",
                ascending=False
            ).iloc[0]

            response = (
                f"The asset requiring the most attention is "
                f"**{most_at_risk['asset_name']}**. "
                f"It has a risk score of "
                f"**{most_at_risk['risk_score']}** "
                f"and a temperature of "
                f"**{most_at_risk['temperature']:.1f}°C**."
            )

        else:

            response = (
                "No high-risk assets have been detected."
            )

        st.chat_message("assistant").write(response)