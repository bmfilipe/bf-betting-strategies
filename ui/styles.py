import streamlit as st

def apply_custom_styles():
    """Apply premium modern CSS styling to Streamlit app (Dark / Light mode support)."""
    theme_mode = st.session_state.get("theme_mode", "dark")
    
    if theme_mode == "light":
        bg_color = "#f8fafc"
        card_bg = "#ffffff"
        text_color = "#0f172a"
        subtitle_color = "#475569"
        border_color = "rgba(15, 23, 42, 0.12)"
        title_bg = "linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 100%)"
        tab_bg = "rgba(241, 245, 249, 0.8)"
        tab_active_bg = "#ffffff"
    else:
        bg_color = "#0f172a"
        card_bg = "rgba(30, 41, 59, 0.5)"
        text_color = "#f8fafc"
        subtitle_color = "#94a3b8"
        border_color = "rgba(255, 255, 255, 0.1)"
        title_bg = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"
        tab_bg = "rgba(30, 41, 59, 0.4)"
        tab_active_bg = "#1e293b"

    css = f"""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    /* Header styling & Vertical Alignment */
    div[data-testid="stHorizontalBlock"]:has(.app-title-container) {{
        align-items: center !important;
    }}

    .app-title-container {{
        background: {title_bg};
        border-radius: 10px;
        padding: 6px 14px;
        color: {text_color};
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        border: 1px solid {border_color};
        display: flex;
        align-items: center;
        gap: 12px;
        min-height: 42px;
        box-sizing: border-box;
    }}

    .header-logo-badge {{
        font-size: 22px;
        line-height: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 8px;
        padding: 4px 8px;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
    }}

    .app-title {{
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
        background: linear-gradient(90deg, #0284c7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        white-space: nowrap;
    }}

    .app-subtitle {{
        color: {subtitle_color};
        font-size: 0.78rem;
        margin: 0;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    /* Metric Cards */
    div[data-testid="stMetricValue"] {{
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #0284c7 !important;
    }}
    div[data-testid="stMetric"] {{
        background: {card_bg};
        border: 1px solid {border_color};
        padding: 12px 16px;
        border-radius: 10px;
    }}

    /* Ev Badge */
    .ev-positive {{
        background-color: rgba(16, 185, 129, 0.2);
        color: #10b981;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 6px;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }}
    .ev-neutral {{
        background-color: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 6px;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }}

    /* Tab navigation style */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 48px;
        white-space: pre-wrap;
        background-color: {tab_bg};
        border-radius: 8px 8px 0 0;
        border: 1px solid {border_color};
        padding: 0 20px;
        font-weight: 600;
        color: {subtitle_color};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {tab_active_bg} !important;
        border-bottom: 2px solid #0284c7 !important;
        color: #0284c7 !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
