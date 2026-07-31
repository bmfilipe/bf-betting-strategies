import streamlit as st

def apply_custom_styles():
    """Apply premium modern CSS styling to Streamlit app."""
    css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Header styling */
    .app-title-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 12px;
        padding: 24px;
        color: #ffffff;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .app-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .app-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 6px;
    }

    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 12px 16px;
        border-radius: 10px;
    }

    /* Ev Badge */
    .ev-positive {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10b981;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 6px;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .ev-neutral {
        background-color: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 6px;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }

    /* Tab navigation style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: rgba(30, 41, 59, 0.4);
        border-radius: 8px 8px 0 0;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 0 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        border-bottom: 2px solid #38bdf8 !important;
        color: #38bdf8 !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
