import streamlit as st


def generate_response(question, df):

    question = question.lower()

    if df.empty:

        return (
            "There are currently no assets matching "
            "your selected filters."
        )

    critical = df[
        df["risk_level"] == "Critical"
    ]

    high = df[
        df["risk_level"] == "High"
    ]

    highest = df.sort_values(
        "risk_score",
        ascending=False,
    ).iloc[0]

    if (
        "critical" in question
        or "danger" in question
        or "risk" in question
    ):

        if len(critical) > 0:

            names = ", ".join(
                critical["asset_name"].tolist()
            )

            return (
                f"There are **{len(critical)} critical "
                f"assets** requiring immediate attention: "
                f"{names}. "
                f"The highest risk asset is "
                f"**{highest['asset_name']}** with a "
                f"risk score of **{highest['risk_score']}**."
            )

        return (
            "There are currently no critical assets. "
            f"The highest risk asset is "
            f"**{highest['asset_name']}** with a "
            f"score of **{highest['risk_score']}**."
        )

    if (
        "temperature" in question
        or "hot" in question
    ):

        return (
            f"The hottest monitored asset is "
            f"**{highest['asset_name']}**, currently at "
            f"**{highest['temperature']:.1f}°C**. "
            f"Its threshold is "
            f"**{highest['threshold']:.1f}°C**."
        )

    if (
        "morning" in question
        or "today" in question
        or "recommend" in question
    ):

        return (
            f"Prioritize **{highest['asset_name']}** "
            f"this morning. Its risk score is "
            f"**{highest['risk_score']}** and its "
            f"temperature is "
            f"**{highest['temperature']:.1f}°C**. "
            f"Consider moving non-essential heavy work "
            f"to cooler operating periods."
        )

    return (
        f"I found **{len(critical)} critical** and "
        f"**{len(high)} high-risk** assets. "
        f"The asset currently requiring the most "
        f"attention is **{highest['asset_name']}**."
    )


def show_copilot(df):

    st.markdown(
        '<div class="section-title">🤖 AssetShield Copilot</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Ask questions about asset climate risk "
        "and operational priorities."
    )

    question = st.chat_input(
        "Ask AssetShield AI..."
    )

    if question:

        st.chat_message(
            "user"
        ).write(question)

        with st.chat_message("assistant"):

            with st.spinner(
                "Analyzing asset conditions..."
            ):

                response = generate_response(
                    question,
                    df,
                )

            st.markdown(response)