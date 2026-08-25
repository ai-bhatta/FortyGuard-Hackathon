import streamlit as st


def load_styles():
    st.markdown(
        """
        <!-- Import Google Fonts: Montserrat (Headings) & Poppins (Body/Cards) -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">

        <style>
        /* Modern Vibrant Dark Theme */
        html, body, [data-testid="stAppViewContainer"], .stApp {
            font-family: 'Poppins', sans-serif !important;
            background: radial-gradient(circle at top left, #1e1b4b 0%, #0f172a 40%, #020617 100%) !important;
            color: #f8fafc !important;
        }

        .main {
            padding-top: 1rem;
        }

        /* Hide default Streamlit chrome */
        #MainMenu, footer, header {
            visibility: hidden;
        }

        /* Distinct Bold Typography for Headers */
        h1, h2, h3, .section-title, .brand {
            font-family: 'Montserrat', sans-serif !important;
        }

        /* Glassmorphic Header Banner */
        .app-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.2rem 1.8rem;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(168, 85, 247, 0.25));
            backdrop-filter: blur(16px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            margin-bottom: 1.8rem;
        }

        .brand {
            font-size: 2.4rem;
            font-weight: 900;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.02em;
        }

        .brand-subtitle {
            color: #cbd5e1;
            font-size: 0.95rem;
            font-weight: 500;
        }

        /* Colorful & Interactive Flashcards / Metric Boxes */
        .metric-card {
            background: linear-gradient(145deg, #ffffff 0%, #f1f5f9 100%) !important;
            border: 2px solid #818cf8 !important;
            border-radius: 18px !important;
            padding: 1.2rem 1.4rem !important;
            min-height: 130px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }

        /* Vibrant Top Accent Bar on Cards */
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(90deg, #06b6d4, #3b82f6, #8b5cf6);
        }

        .metric-card:hover {
            transform: translateY(-8px) scale(1.03);
            box-shadow: 0 15px 35px rgba(99, 102, 241, 0.4) !important;
            border-color: #38bdf8 !important;
        }

        .metric-label {
            font-size: 0.85rem !important;
            color: #475569 !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .metric-value {
            font-family: 'Montserrat', sans-serif !important;
            font-size: 2.4rem !important;
            font-weight: 800 !important;
            margin-top: 4px;
            color: #0f172a !important;
            line-height: 1;
        }

        .metric-description {
            font-size: 0.82rem !important;
            color: #64748b !important;
            margin-top: 8px;
            font-weight: 600;
        }

        /* Glowing High-Contrast Risk Badges */
        .risk-critical {
            background: linear-gradient(135deg, #ef4444, #dc2626) !important;
            color: #ffffff !important;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 700;
            box-shadow: 0 4px 14px rgba(239, 68, 68, 0.5);
        }

        .risk-high {
            background: linear-gradient(135deg, #f97316, #ea580c) !important;
            color: #ffffff !important;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 700;
            box-shadow: 0 4px 14px rgba(249, 115, 22, 0.5);
        }

        .risk-moderate {
            background: linear-gradient(135deg, #eab308, #ca8a04) !important;
            color: #ffffff !important;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 700;
            box-shadow: 0 4px 14px rgba(234, 179, 8, 0.5);
        }

        .risk-low {
            background: linear-gradient(135deg, #22c55e, #16a34a) !important;
            color: #ffffff !important;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 700;
            box-shadow: 0 4px 14px rgba(34, 197, 94, 0.5);
        }

        /* Vibrant Alert Banner */
        .safety-alert {
            border-left: 8px solid #ef4444 !important;
            background: linear-gradient(90deg, #fef2f2, #ffffff) !important;
            padding: 1.3rem 1.6rem;
            border-radius: 16px;
            margin-bottom: 1.8rem;
            box-shadow: 0 10px 30px rgba(239, 68, 68, 0.25);
            transition: transform 0.2s ease;
        }

        .safety-alert:hover {
            transform: scale(1.01);
        }

        .safety-title {
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 800;
            font-size: 1.15rem;
            color: #b91c1c !important;
        }

        .safety-text {
            margin-top: 6px;
            color: #1e293b !important;
            font-size: 0.95rem;
            font-weight: 500;
        }

        /* Container Frames for Maps and Charts */
        [data-testid="stVegaLiteChart"], [data-testid="stPydeckChart"], .element-container iframe {
            background: rgba(30, 41, 59, 0.7) !important;
            border: 2px solid rgba(129, 140, 248, 0.3) !important;
            border-radius: 20px !important;
            padding: 10px !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
        }

        /* Custom Sidebar Styles */
        [data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.95) !important;
            border-right: 2px solid rgba(129, 140, 248, 0.2) !important;
        }

        [data-testid="stSidebar"] * {
            color: #f1f5f9 !important;
        }

        /* Styled Section Headings */
        .section-title {
            font-size: 1.4rem;
            font-weight: 800;
            color: #ffffff;
            margin-top: 1.2rem;
            margin-bottom: 1rem;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0f172a;
        }
        ::-webkit-scrollbar-thumb {
            background: #6366f1;
            border-radius: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )