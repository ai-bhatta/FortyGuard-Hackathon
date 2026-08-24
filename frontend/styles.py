import streamlit as st


def load_styles():

    st.markdown(
        """
        <style>

        /* Main page */

        .main {
            padding-top: 1rem;
        }

        /* Hide default Streamlit branding */

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        /* Header */

        .app-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0 1.2rem 0;
        }

        .brand {
            font-size: 2rem;
            font-weight: 700;
        }

        .brand-subtitle {
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-top: -8px;
        }

        /* Cards */

        .metric-card {
            background: white;
            border: 1px solid #e6e9ef;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            min-height: 120px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }

        .metric-label {
            font-size: 0.85rem;
            color: #6b7280;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            margin-top: 8px;
        }

        .metric-description {
            font-size: 0.78rem;
            color: #8a8f98;
            margin-top: 4px;
        }

        /* Risk badges */

        .risk-critical {
            background: #fee2e2;
            color: #991b1b;
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: 600;
        }

        .risk-high {
            background: #ffedd5;
            color: #9a3412;
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: 600;
        }

        .risk-moderate {
            background: #fef3c7;
            color: #92400e;
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: 600;
        }

        .risk-low {
            background: #dcfce7;
            color: #166534;
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: 600;
        }

        /* Safety alert */

        .safety-alert {
            border-left: 5px solid #dc2626;
            background: #fef2f2;
            padding: 1rem 1.2rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }

        .safety-title {
            font-weight: 700;
            font-size: 1.05rem;
        }

        .safety-text {
            margin-top: 5px;
            color: #4b5563;
        }

        /* Section title */

        .section-title {
            font-size: 1.25rem;
            font-weight: 650;
            margin-top: 0.5rem;
            margin-bottom: 0.8rem;
        }

        /* Footer */

        .app-footer {
            text-align: center;
            color: #9ca3af;
            padding: 2rem 0 1rem 0;
            font-size: 0.8rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )