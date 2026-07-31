import streamlit as st
from config import init_session_state
from ui import (
    apply_custom_styles,
    render_tab_ingestion,
    render_tab_analysis,
    render_tab_slips,
    render_tab_admin
)

# Page configuration
st.set_page_config(
    page_title="BF Analista de Futebol | Análise Preditiva & Boletins (+EV)",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State & Custom CSS
init_session_state()
apply_custom_styles()

# Landing Page (Página Inicial se app_started for False)
if not st.session_state.get("app_started", False):
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-radius: 16px; margin-bottom: 30px; border: 1px solid #334155; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
        <div style="font-size: 64px; margin-bottom: 10px;">⚽</div>
        <h1 style="color: #38bdf8; font-size: 42px; font-weight: 800; margin-bottom: 10px; letter-spacing: -1px;">BF Analista de Futebol</h1>
        <p style="color: #94a3b8; font-size: 18px; max-width: 800px; margin: 0 auto 25px auto; line-height: 1.6;">
            Sistema Quantitativo de Análise Preditiva (+EV), Matrizes Estatísticas de Poisson & Geração Dinâmica de Boletins de Apostas Desportivas em Tempo Real.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature Grid Cards
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)

    with col_c1:
        with st.container(border=True):
            st.markdown("### 🔍 Tempo Real")
            st.write("Captação de jogos do dia via **The Odds API** (odds reais) ou **Gemini 2.5 Flash**.")

    with col_c2:
        with st.container(border=True):
            st.markdown("### 📊 Poisson 7x7")
            st.write("Cálculo quantitativo de probabilidades implícitas e apuramento de apostas com **Valor Esperado (+EV)**.")

    with col_c3:
        with st.container(border=True):
            st.markdown("### 💰 Gestão Kelly")
            st.write("Dimensionamento ótimo de stakes por fração de Kelly (1/4 Kelly) para máxima proteção de banca.")

    with col_c4:
        with st.container(border=True):
            st.markdown("### 🎫 Boletins +EV")
            st.write("Geração combinatória por estratégias sem jogos duplicados e exportação em **PDF, TXT e CSV**.")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Hero Start Action Button
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button("🚀 Iniciar Aplicação", type="primary", width="stretch"):
            st.session_state["app_started"] = True
            st.session_state["confirm_exit"] = False
            st.rerun()

# Main Application Dashboard
else:
    # Top Action Bar with App Title, Admin Quick Access, and Exit Button
    col_hdr1, col_hdr_admin, col_hdr_exit = st.columns([3, 1, 1])

    with col_hdr1:
        st.markdown("""
        <div class="app-title-container" style="padding: 10px 15px;">
            <h2 class="app-title" style="font-size: 24px; margin: 0;">⚽ BF Analista de Futebol</h2>
            <p class="app-subtitle" style="margin: 0; font-size: 13px;">Ingestão em Tempo Real • Matrizes de Poisson 7x7 • Boletins por Estratégia (+EV)</p>
        </div>
        """, unsafe_allow_html=True)

    with col_hdr_admin:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if st.button("🔒 Área de Administrador", width="stretch"):
            st.session_state["active_tab"] = "🔒 Área de Administrador"
            st.rerun()

    with col_hdr_exit:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sair da Aplicação", width="stretch"):
            st.session_state["confirm_exit"] = True

    # Confirmation Banner when Sair is clicked
    if st.session_state.get("confirm_exit", False):
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

    # Navigation Options & Sync (3 main tabs; Admin is accessed via top header button)
    nav_options = [
        "🔍 Obter Jogos (Odds API / OddsPortal / Gemini)",
        "📊 Análise & Probabilidades (+EV)",
        "🎫 Gerador de Boletins & Exportação"
    ]

    active_view = st.session_state.get("active_tab", nav_options[0])

    if active_view == "🔒 Área de Administrador":
        col_adm_title, col_adm_back = st.columns([3, 1])
        with col_adm_title:
            st.markdown("### 🔒 Painel de Administração & Vault")
        with col_adm_back:
            if st.button("⬅️ Voltar ao Dashboard", width="stretch"):
                st.session_state["active_tab"] = nav_options[0]
                st.rerun()
        st.markdown("---")
        render_tab_admin()
    else:
        current_tab = active_view if active_view in nav_options else nav_options[0]

        if hasattr(st, "segmented_control"):
            selected_nav = st.segmented_control(
                "Navegação Principal",
                options=nav_options,
                default=current_tab,
                label_visibility="collapsed"
            )
            if selected_nav and selected_nav != st.session_state.get("active_tab"):
                st.session_state["active_tab"] = selected_nav
                st.rerun()

            active_view = st.session_state.get("active_tab", nav_options[0])
            if active_view == nav_options[0]:
                render_tab_ingestion()
            elif active_view == nav_options[1]:
                render_tab_analysis()
            elif active_view == nav_options[2]:
                render_tab_slips()

        else:
            tab1, tab2, tab3 = st.tabs(nav_options)
            with tab1:
                render_tab_ingestion()
            with tab2:
                render_tab_analysis()
            with tab3:
                render_tab_slips()
