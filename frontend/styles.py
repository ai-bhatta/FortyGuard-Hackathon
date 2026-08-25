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

        /* Hide default Streamlit menu and footer, keep sidebar toggle button visible */
        #MainMenu, footer {
            visibility: hidden;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* Style and position the sidebar expand arrow for mobile */
        button[data-testid="stSidebarCollapseButton"], 
        button[data-testid="stBaseButton-headerNoPadding"] {
            visibility: visible !important;
            display: block !important;
            color: #ffffff !important;
            z-index: 999999 !important;
        }

        /* Serif Typography */
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
            transition: all 0.3s ease;
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

        /* Smooth Section Transitions */
        .section-wrapper {
            padding: 1rem 0;
            margin: 1.5rem 0;
            transition: opacity 0.4s ease-in-out, transform 0.4s ease-in-out;
        }

        .section-divider {
            height: 1px;
            background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0) 100%);
            margin: 2rem 0;
        }

        /* Card Elements */
        .metric-card {
            background: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 12px !important;
            padding: 1.25rem !important;
            min-height: 125px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
            transition: all 0.3s ease !important;
        }

        .metric-card:hover {
            transform: translateY(-4px);
            border-color: #93c5fd !important;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25) !important;
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

        /* Asset Detailed Card Frame */
        .asset-detail-card {
            background: rgba(17, 24, 39, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 14px;
            padding: 1.8rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            transition: border-color 0.3s ease;
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
            margin-bottom: 1.5rem;
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