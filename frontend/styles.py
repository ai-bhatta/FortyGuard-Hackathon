import streamlit as st


def load_styles():
    st.markdown(
        """
        <!-- Import Google Fonts: Playfair Display (Serif) & Inter (Body) -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

        <style>
        /* Base Theme */
        html, body, [data-testid="stAppViewContainer"], .stApp {
            font-family: 'Inter', sans-serif !important;
            background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #030712 100%) !important;
            color: #f3f4f6 !important;
        }

        .main {
            padding-top: 1rem;
        }

        /* Hide Streamlit default menu & footer, keep sidebar toggle button visible */
        #MainMenu, footer {
            visibility: hidden;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        button[data-testid="stSidebarCollapseButton"], 
        button[data-testid="stBaseButton-headerNoPadding"] {
            visibility: visible !important;
            display: block !important;
            color: #ffffff !important;
            z-index: 999999 !important;
        }

        /* Keyframe Entrance Animation */
        @keyframes popUpFade {
            0% {
                opacity: 0;
                transform: translateY(20px) scale(0.98);
            }
            100% {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        /* Global Dynamic Pop-Up Trigger */
        .app-header, 
        .safety-alert, 
        .metric-card, 
        .asset-detail-card, 
        div[data-testid="stDataFrame"], 
        div[data-testid="stPlotlyChart"],
        div[data-testid="stExpander"],
        div[data-testid="stColumn"] > div {
            animation: popUpFade 0.55s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            will-change: transform, opacity;
        }

        /* Staggered Delays for Sequential Pop-Up Effects */
        div[data-testid="stColumn"]:nth-child(1) .metric-card { animation-delay: 0.05s; }
        div[data-testid="stColumn"]:nth-child(2) .metric-card { animation-delay: 0.12s; }
        div[data-testid="stColumn"]:nth-child(3) .metric-card { animation-delay: 0.19s; }
        div[data-testid="stColumn"]:nth-child(4) .metric-card { animation-delay: 0.26s; }

        .safety-alert { animation-delay: 0.3s; }
        .section-divider { animation-delay: 0.35s; }

        /* Typography */
        h1, h2, h3, .section-title, .brand, .asset-card-title, .brand-subtitle {
            font-family: 'Playfair Display', Georgia, serif !important;
            letter-spacing: -0.01em;
        }

        /* Header Banner */
        .app-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem 2rem;
            background: rgba(17, 24, 39, 0.85);
            backdrop-filter: blur(16px);
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            margin-bottom: 2rem;
        }

        .brand {
            font-size: 2.3rem;
            font-weight: 800;
            color: #f8fafc;
        }

        .brand-subtitle {
            font-style: italic;
            color: #9ca3af;
            font-size: 1rem;
            margin-top: 2px;
        }

        /* Divider & Transitions */
        .section-divider {
            height: 1px;
            background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.18) 50%, rgba(255,255,255,0) 100%);
            margin: 2.2rem 0;
        }

        /* Cards & Interactive Elements */
        .metric-card {
            background: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 12px !important;
            padding: 1.25rem !important;
            min-height: 125px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
            transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        }

        .metric-card:hover {
            transform: translateY(-6px) scale(1.01) !important;
            border-color: #93c5fd !important;
            box-shadow: 0 14px 30px rgba(0, 0, 0, 0.3) !important;
        }

        .metric-label {
            font-size: 0.8rem !important;
            color: #4b5563 !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .metric-value {
            font-family: 'Playfair Display', serif !important;
            font-size: 2.3rem !important;
            font-weight: 800 !important;
            margin-top: 4px;
            color: #111827 !important;
        }

        .metric-description {
            font-size: 0.8rem !important;
            color: #6b7280 !important;
            margin-top: 6px;
        }

        .asset-detail-card {
            background: rgba(17, 24, 39, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 14px;
            padding: 1.8rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }

        .asset-detail-card:hover {
            border-color: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
        }

        .asset-detail-title {
            font-family: 'Playfair Display', serif !important;
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.5rem;
        }

        .asset-detail-subtext {
            color: #9ca3af;
            font-size: 0.9rem;
            line-height: 1.6;
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #f3f4f6;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        .section-subtitle {
            font-size: 0.9rem;
            color: #9ca3af;
            margin-bottom: 1.2rem;
        }

        .safety-alert {
            background: rgba(127, 29, 29, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin-top: 1.8rem !important;  /* Added top margin to separate from KPI boxes */
            margin-bottom: 2rem !important;
        }

        .safety-title {
            font-family: 'Playfair Display', serif !important;
            font-size: 1.1rem;
            font-weight: 700;
            color: #fca5a5;
            margin-bottom: 0.4rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .safety-text {
            color: #f3f4f6;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .app-footer {
            text-align: center;
            color: #6b7280;
            font-size: 0.85rem;
            padding: 2rem 0;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            margin-top: 3rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )