import streamlit as st

def apply_custom_styles():
    """Apply premium modern CSS styling with 100% high contrast for Dark & Light modes."""
    theme_mode = st.session_state.get("theme_mode", "light")
    
    if theme_mode == "light":
        bg_color = "#f8fafc"
        card_bg = "#ffffff"
        text_color = "#0f172a"
        subtitle_color = "#334155"
        border_color = "#cbd5e1"
        title_bg = "linear-gradient(135deg, #e2e8f0 0%, #ffffff 100%)"
        tab_bg = "#f1f5f9"
        tab_active_bg = "#ffffff"
        tab_text = "#334155"
        tab_active_text = "#0284c7"
        btn_sec_bg = "#f1f5f9"
        btn_sec_text = "#0f172a"
        btn_sec_border = "#cbd5e1"
        input_bg = "#ffffff"
        input_text = "#0f172a"
        sidebar_bg = "#f1f5f9"
        sidebar_border = "#cbd5e1"
        sidebar_text = "#0f172a"
        sidebar_item_hover = "#e2e8f0"
        sidebar_item_active = "#ffffff"
        sidebar_item_active_text = "#0284c7"
    else:
        bg_color = "#0f172a"
        card_bg = "rgba(30, 41, 59, 0.5)"
        text_color = "#f8fafc"
        subtitle_color = "#94a3b8"
        border_color = "rgba(255, 255, 255, 0.12)"
        title_bg = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"
        tab_bg = "rgba(30, 41, 59, 0.4)"
        tab_active_bg = "#1e293b"
        tab_text = "#94a3b8"
        tab_active_text = "#38bdf8"
        btn_sec_bg = "#1e293b"
        btn_sec_text = "#f8fafc"
        btn_sec_border = "rgba(255, 255, 255, 0.15)"
        input_bg = "#1e293b"
        input_text = "#f8fafc"
        sidebar_bg = "#1e293b"
        sidebar_border = "rgba(255, 255, 255, 0.12)"
        sidebar_text = "#f8fafc"
        sidebar_item_hover = "rgba(255, 255, 255, 0.05)"
        sidebar_item_active = "rgba(56, 189, 248, 0.15)"
        sidebar_item_active_text = "#38bdf8"

    sidebar_choice = st.session_state.get("sidebar_color", "Padrão")

    # Custom sidebar background & typography contrast mapping
    if sidebar_choice == "Vermelho":
        sidebar_bg = "#8b1111"
        sidebar_border = "#b91c1c"
        sidebar_text = "#ffffff"
        sidebar_nav_title_color = "#fef08a"
        sidebar_item_hover = "rgba(255, 255, 255, 0.18)"
        sidebar_is_custom = True
    elif sidebar_choice == "Azul":
        sidebar_bg = "#1e3a8a"
        sidebar_border = "#1d4ed8"
        sidebar_text = "#ffffff"
        sidebar_nav_title_color = "#fef08a"
        sidebar_item_hover = "rgba(255, 255, 255, 0.18)"
        sidebar_is_custom = True
    elif sidebar_choice == "Verde":
        sidebar_bg = "#14532d"
        sidebar_border = "#15803d"
        sidebar_text = "#ffffff"
        sidebar_nav_title_color = "#fef08a"
        sidebar_item_hover = "rgba(255, 255, 255, 0.18)"
        sidebar_is_custom = True
    else:
        sidebar_is_custom = False
        sidebar_nav_title_color = subtitle_color

    # High-contrast styling for sidebar collapse/expand toggle arrow
    if theme_mode == "light":
        collapse_btn_bg = "#ffffff"
        collapse_btn_border = "2px solid #0284c7"
        collapse_btn_color = "#0284c7"
        collapse_btn_hover_bg = "#0284c7"
        collapse_btn_hover_color = "#ffffff"
        collapse_btn_shadow = "0 2px 10px rgba(2, 132, 199, 0.35)"
    else:
        collapse_btn_bg = "#1e293b"
        collapse_btn_border = "2px solid #38bdf8"
        collapse_btn_color = "#38bdf8"
        collapse_btn_hover_bg = "rgba(56, 189, 248, 0.25)"
        collapse_btn_hover_color = "#38bdf8"
        collapse_btn_shadow = "0 0 12px rgba(56, 189, 248, 0.5)"

    custom_sidebar_css = f"""
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {{
        color: {sidebar_text} !important;
    }}

    /* High contrast button styling inside custom sidebar */
    section[data-testid="stSidebar"] button:not([data-testid="stBaseButton-header"]):not([kind="header"]),
    section[data-testid="stSidebar"] .stButton button {{
        background-color: rgba(0, 0, 0, 0.35) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
    }}

    section[data-testid="stSidebar"] button:not([data-testid="stBaseButton-header"]):not([kind="header"]) *,
    section[data-testid="stSidebar"] .stButton button * {{
        color: #ffffff !important;
    }}

    section[data-testid="stSidebar"] button:not([data-testid="stBaseButton-header"]):not([kind="header"]):hover,
    section[data-testid="stSidebar"] .stButton button:hover {{
        background-color: rgba(0, 0, 0, 0.55) !important;
        border-color: rgba(255, 255, 255, 0.7) !important;
        color: #ffffff !important;
    }}

    /* Selectbox dropdown inside custom sidebar */
    section[data-testid="stSidebar"] div[data-baseweb="select"] {{
        background-color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 8px !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] * {{
        color: #0f172a !important;
    }}
    """ if sidebar_is_custom else ""

    css = f"""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    /* Main Page Background Theme Control */
    .stApp, [data-testid="stAppViewContainer"], section.main, [data-testid="stHeader"] {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
        transition: background-color 0.3s ease, color 0.3s ease;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {sidebar_border} !important;
    }}

    section[data-testid="stSidebar"] .stRadio label {{
        font-weight: 600 !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        color: {sidebar_text} !important;
    }}

    section[data-testid="stSidebar"] .stRadio label:hover {{
        background-color: {sidebar_item_hover} !important;
    }}

    .sidebar-header {{
        padding: 10px 5px 15px 5px;
        text-align: center;
        border-bottom: 1px solid {sidebar_border};
        margin-bottom: 15px;
    }}

    .sidebar-nav-title {{
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {sidebar_nav_title_color} !important;
        margin: 12px 0 6px 4px;
    }}

    {custom_sidebar_css}

    /* Sidebar High Contrast Collapse/Expand Arrow Toggle Button */
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarHeader"] button,
    button[data-testid="stBaseButton-header"],
    div[data-testid="stHeader"] button[kind="header"],
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-header"] {{
        background-color: {collapse_btn_bg} !important;
        border: {collapse_btn_border} !important;
        border-radius: 8px !important;
        color: {collapse_btn_color} !important;
        box-shadow: {collapse_btn_shadow} !important;
        transition: all 0.2s ease-in-out !important;
    }}

    button[data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarHeader"] button svg,
    button[data-testid="stBaseButton-header"] svg,
    div[data-testid="stHeader"] button[kind="header"] svg,
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-header"] svg {{
        fill: {collapse_btn_color} !important;
        color: {collapse_btn_color} !important;
    }}

    button[data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="stSidebarHeader"] button:hover,
    button[data-testid="stBaseButton-header"]:hover {{
        background-color: {collapse_btn_hover_bg} !important;
        color: {collapse_btn_hover_color} !important;
    }}

    button[data-testid="stSidebarCollapseButton"]:hover svg,
    [data-testid="stSidebarHeader"] button:hover svg,
    button[data-testid="stBaseButton-header"]:hover svg {{
        fill: {collapse_btn_hover_color} !important;
        color: {collapse_btn_hover_color} !important;
    }}

    /* General Text Visibility & Contrast */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div[data-testid="stMarkdownContainer"] p {{
        color: {text_color} !important;
    }}

    .stCaption, caption {{
        color: {subtitle_color} !important;
    }}

    /* Header Container styling & Vertical Alignment */
    div[data-testid="stHorizontalBlock"]:has(.app-title-container) {{
        align-items: center !important;
    }}

    .app-title-container {{
        background: {title_bg};
        border-radius: 10px;
        padding: 8px 16px;
        color: {text_color} !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid {border_color};
        display: flex;
        align-items: center;
        gap: 12px;
        min-height: 48px;
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
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0;
        padding: 0;
        line-height: 1;
        background: linear-gradient(90deg, #0284c7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        white-space: nowrap;
        display: flex;
        align-items: center;
    }}

    /* Primary Buttons (ALWAYS VIBRANT BLUE WITH WHITE BOLD TEXT) */
    button[kind="primary"], button[data-testid="baseButton-primary"], .stButton button[kind="primary"] {{
        background-color: #0284c7 !important;
        border: 1px solid #0369a1 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3) !important;
    }}
    button[kind="primary"] *, button[data-testid="baseButton-primary"] *, .stButton button[kind="primary"] * {{
        color: #ffffff !important;
    }}
    button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {{
        background-color: #0369a1 !important;
        color: #ffffff !important;
    }}

    /* Secondary Buttons (ADAPTIVE CONTRAST FOR LIGHT & DARK) */
    button[kind="secondary"], button[data-testid="baseButton-secondary"], .stButton button[kind="secondary"], .stButton button:not([kind="primary"]) {{
        background-color: {btn_sec_bg} !important;
        border: 1px solid {btn_sec_border} !important;
        color: {btn_sec_text} !important;
        font-weight: 600 !important;
    }}
    button[kind="secondary"] *, button[data-testid="baseButton-secondary"] *, .stButton button:not([kind="primary"]) * {{
        color: {btn_sec_text} !important;
    }}

    /* Inputs, Selectboxes and Textareas */
    div[data-baseweb="input"], input, textarea, div[data-baseweb="select"] {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border-color: {border_color} !important;
    }}
    div[data-baseweb="input"] input {{
        color: {input_text} !important;
    }}

    /* Metric Cards */
    div[data-testid="stMetricValue"] {{
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #0284c7 !important;
    }}
    div[data-testid="stMetric"] {{
        background: {card_bg} !important;
        border: 1px solid {border_color} !important;
        padding: 12px 16px;
        border-radius: 10px;
    }}

    /* EV Badges */
    .ev-positive {{
        background-color: rgba(10, 185, 129, 0.2);
        color: #10b981 !important;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 6px;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }}
    .ev-neutral {{
        background-color: rgba(245, 158, 11, 0.2);
        color: #f59e0b !important;
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
        background-color: {tab_bg} !important;
        border-radius: 8px 8px 0 0;
        border: 1px solid {border_color} !important;
        padding: 0 20px;
        font-weight: 600;
        color: {tab_text} !important;
    }}
    .stTabs [data-baseweb="tab"] * {{
        color: {tab_text} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {tab_active_bg} !important;
        border-bottom: 2px solid #0284c7 !important;
        color: {tab_active_text} !important;
    }}
    .stTabs [aria-selected="true"] * {{
        color: {tab_active_text} !important;
    }}

    /* Container / Expander Card Styling */
    div[data-testid="stExpander"], div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {{
        border-color: {border_color} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
