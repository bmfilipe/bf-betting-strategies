import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from config import init_session_state
from ui import (
    apply_custom_styles,
    render_tab_ingestion,
    render_tab_live,
    render_tab_h2h,
    render_tab_analysis,
    render_tab_slips,
    render_tab_admin
)

# Page configuration
st.set_page_config(
    page_title="BF Analista de Futebol | Análise Preditiva & Boletins (+EV)",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State & Custom CSS
init_session_state()
apply_custom_styles()

# Landing Page (Página Inicial se app_started for False)
if not st.session_state.get("app_started", False):
    # Top Action Bar with Theme Toggle on Landing Page
    col_l_blank, col_l_theme = st.columns([4, 1], vertical_alignment="center")
    with col_l_theme:
        current_theme = st.session_state.get("theme_mode", "light")
        theme_btn_label = "☀️ Claro" if current_theme == "dark" else "🌙 Escuro"
        if st.button(theme_btn_label, width="stretch", help="Alternar entre Modo Escuro (Dark) e Modo Claro (Light)"):
            st.session_state["theme_mode"] = "light" if current_theme == "dark" else "dark"
            st.rerun()

    # Adaptive Hero Banner Colors
    current_theme = st.session_state.get("theme_mode", "light")
    if current_theme == "light":
        hero_bg = "linear-gradient(135deg, #e2e8f0 0%, #ffffff 100%)"
        hero_title_color = "#0284c7"
        hero_text_color = "#334155"
        hero_border = "1px solid #cbd5e1"
        hero_shadow = "0 10px 30px rgba(0, 0, 0, 0.08)"
    else:
        hero_bg = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"
        hero_title_color = "#38bdf8"
        hero_text_color = "#94a3b8"
        hero_border = "1px solid #334155"
        hero_shadow = "0 10px 30px rgba(0, 0, 0, 0.5)"

    st.markdown(f"""
    <div style="text-align: center; padding: 40px 20px; background: {hero_bg}; border-radius: 16px; margin-bottom: 30px; border: {hero_border}; box-shadow: {hero_shadow};">
        <div style="font-size: 64px; margin-bottom: 10px;">⚽</div>
        <h1 style="color: {hero_title_color}; font-size: 42px; font-weight: 800; margin-bottom: 10px; letter-spacing: -1px;">BF Analista de Futebol</h1>
        <p style="color: {hero_text_color}; font-size: 18px; max-width: 800px; margin: 0 auto 25px auto; line-height: 1.6;">
            Sistema Quantitativo de Análise Preditiva (+EV), Matrizes Estatísticas de Poisson &amp; Geração Dinâmica de Boletins de Apostas Desportivas em Tempo Real.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature Grid Cards
    col_c1, col_c2, col_c3, col_c4, col_c5, col_c6 = st.columns(6)

    with col_c1:
        with st.container(border=True):
            st.markdown("### 🔍 Ingestão")
            st.write("Captação de jogos pré-jogo via **The Odds API** ou **Gemini 2.5**.")

    with col_c2:
        with st.container(border=True):
            st.markdown("### 🔴 Ao Vivo")
            st.write("Monitorização em tempo real de partidas in-play, minutos e odds ao vivo.")

    with col_c3:
        with st.container(border=True):
            st.markdown("### ⚔️ H2H Scraping")
            st.write("Comparador estatístico de equipas e raspagem de dados históricos.")

    with col_c4:
        with st.container(border=True):
            st.markdown("### 📊 Poisson")
            st.write("Cálculo de matrizes de Poisson 7x7 e Valor Esperado (**+EV**).")

    with col_c5:
        with st.container(border=True):
            st.markdown("### 💰 Kelly")
            st.write("Dimensionamento ótimo de stakes (1/4 Kelly) para gestão de risco.")

    with col_c6:
        with st.container(border=True):
            st.markdown("### 🎫 Boletins")
            st.write("Gerador de boletins combinados sem jogos duplicados (PDF/CSV).")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Hero Start Action Button
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button("🚀 Iniciar Aplicação", type="primary", width="stretch"):
            st.session_state["app_started"] = True
            st.session_state["confirm_exit"] = False
            st.rerun()

# Main Application Dashboard with Left Sidebar Navigation
else:
    nav_options = [
        "🔍 Obter Jogos",
        "🔴 Jogos ao Vivo",
        "⚔️ Comparador de Equipas",
        "📊 Análise & Probabilidades",
        "🎫 Gerador de Boletins"
    ]

    nav_mapping = {
        "🔍 Obter Jogos": "🔍 Obter Jogos (Odds API / OddsPortal / Gemini)",
        "🔴 Jogos ao Vivo": "🔴 Jogos ao Vivo (Live Scores & In-Play)",
        "⚔️ Comparador de Equipas": "⚔️ Comparador de Equipas (Confronto Direto H2H)",
        "📊 Análise & Probabilidades": "📊 Análise & Probabilidades (+EV)",
        "🎫 Gerador de Boletins": "🎫 Gerador de Boletins & Exportação"
    }

    # Left Sidebar Construction
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <div style="font-size: 38px; margin-bottom: 4px;">⚽</div>
            <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700;">BF Analista</h3>
            <p style="font-size: 0.75rem; opacity: 0.8; margin: 2px 0 0 0;">Análise Preditiva & Boletins (+EV)</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p class='sidebar-nav-title'>Navegação</p>", unsafe_allow_html=True)

        current_active = st.session_state.get("active_tab", nav_mapping["🔍 Obter Jogos"])
        default_idx = 0
        if current_active in nav_mapping.values():
            default_idx = list(nav_mapping.values()).index(current_active)

        selected_option = st.radio(
            label="Navegação Principal",
            options=nav_options,
            index=default_idx,
            label_visibility="collapsed",
            key="sidebar_nav_radio"
        )

        selected_full = nav_mapping[selected_option]
        if st.session_state.get("active_tab") != selected_full and st.session_state.get("active_tab") != "🔒 Área de Administrador":
            st.session_state["active_tab"] = selected_full

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<p class='sidebar-nav-title'>Painel & Sistema</p>", unsafe_allow_html=True)

        # Action buttons positioned below the main page menus as requested
        if st.button("🔒 Área de Administrador", width="stretch"):
            st.session_state["active_tab"] = "🔒 Área de Administrador"
            st.rerun()

        if st.button("🚪 Sair da Aplicação", width="stretch"):
            st.session_state["confirm_exit"] = True
            st.rerun()

        current_theme = st.session_state.get("theme_mode", "light")
        theme_btn_label = "☀️ Modo Claro" if current_theme == "dark" else "🌙 Modo Escuro"
        if st.button(theme_btn_label, width="stretch", help="Alternar entre Modo Escuro (Dark) e Modo Claro (Light)"):
            st.session_state["theme_mode"] = "light" if current_theme == "dark" else "dark"
            st.rerun()

        st.markdown("<p class='sidebar-nav-title'>🎨 Cor da Sidebar</p>", unsafe_allow_html=True)
        sidebar_colors = ["Padrão", "Vermelho", "Azul", "Verde"]
        current_sb_color = st.session_state.get("sidebar_color", "Padrão")
        sb_idx = sidebar_colors.index(current_sb_color) if current_sb_color in sidebar_colors else 0
        
        new_sb_color = st.selectbox(
            label="Cor de Fundo da Barra Lateral",
            options=sidebar_colors,
            index=sb_idx,
            key="sb_color_select",
            label_visibility="collapsed"
        )
        if new_sb_color != current_sb_color:
            st.session_state["sidebar_color"] = new_sb_color
            st.rerun()

    # Main Area (Right side of sidebar) Header
    st.markdown("""
    <div class="app-title-container">
        <div class="header-logo-badge">⚽</div>
        <h2 class="app-title">BF Analista de Futebol</h2>
    </div>
    """, unsafe_allow_html=True)

    # Confirmation Banner when Sair da Aplicação is clicked
    if st.session_state.get("confirm_exit", False):
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.warning("⚠️ **Tem a certeza de que deseja sair da aplicação?** Todos os dados não guardados permanecerão na sessão local.")
            col_yes, col_no, _ = st.columns([1, 1, 2])

            with col_yes:
                if st.button("✅ Sim, Sair", type="primary", width="stretch"):
                    st.session_state["app_started"] = False
                    st.session_state["confirm_exit"] = False
                    st.rerun()

            with col_no:
                if st.button("❌ Cancelar", width="stretch"):
                    st.session_state["confirm_exit"] = False
                    st.rerun()

    st.markdown("---")

    # Render Content of Selected Page on the Right Side
    active_view = st.session_state.get("active_tab", nav_mapping["🔍 Obter Jogos"])

    if active_view == "🔒 Área de Administrador":
        col_adm_title, col_adm_back = st.columns([3, 1])
        with col_adm_title:
            st.markdown("### 🔒 Painel de Administração & Vault")
        with col_adm_back:
            if st.button("⬅️ Voltar ao Dashboard", width="stretch"):
                st.session_state["active_tab"] = nav_mapping["🔍 Obter Jogos"]
                st.rerun()
        st.markdown("---")
        render_tab_admin()
    elif active_view == nav_mapping["🔴 Jogos ao Vivo"]:
        render_tab_live()
    elif active_view == nav_mapping["⚔️ Comparador de Equipas"]:
        render_tab_h2h()
    elif active_view == nav_mapping["📊 Análise & Probabilidades"]:
        render_tab_analysis()
    elif active_view == nav_mapping["🎫 Gerador de Boletins"]:
        render_tab_slips()
    else:
        render_tab_ingestion()


