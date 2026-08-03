import streamlit as st
import datetime
from services import LiveMatchesService
from database.db import load_live_matches_from_db

def render_tab_live():
    """Render Page: 🔴 Jogos ao Vivo em Tempo Real (Live Scores & In-Play Ingestion)."""
    st.subheader("🔴 Jogos ao Vivo em Tempo Real (In-Play Live Scores)")
    st.write("Acompanhamento quantitativo das partidas a decorrer neste momento no mundo, com resultados ao vivo, minuto a minuto e odds atualizadas.")

    col_btn, col_info = st.columns([1, 2], vertical_alignment="center")

    with col_btn:
        if st.button("🔄 Atualizar Jogos ao Vivo Agora", type="primary", width="stretch", help="Obter partidas a decorrer em tempo real"):
            with st.spinner("A consultar servidores de odds e dados ao vivo..."):
                api_key = st.session_state.get("api_football_key", "")
                live_matches, log_msg = LiveMatchesService.fetch_live_matches(api_key)
                st.session_state["live_matches_data"] = live_matches
                st.session_state["last_live_refresh"] = datetime.datetime.now().strftime("%H:%M:%S")
                st.session_state["live_ingestion_log"] = log_msg
                st.success(f"Captação concluída às {st.session_state['last_live_refresh']}!")
                st.rerun()

    with col_info:
        last_time = st.session_state.get("last_live_refresh", "Nunca")
        st.info(f"⏱️ **Última atualização:** `{last_time}` | **Estado do Servidor:** 🟢 Ligado (Gravação Ativa no SQLite)")

    st.markdown("---")

    # Retrieve live matches from session state or SQLite database
    live_matches = st.session_state.get("live_matches_data", [])
    if not live_matches:
        live_matches = load_live_matches_from_db()
        st.session_state["live_matches_data"] = live_matches

    if not live_matches:
        st.warning("Nenhum jogo ao vivo carregado de momento. Clique no botão acima para captação em tempo real.")
        return

    # Metric Cards Top Overview
    total_live = len(live_matches)
    total_goals = sum(m.get("score_home", 0) + m.get("score_away", 0) for m in live_matches)
    leagues_set = set(m.get("league", "Outros") for m in live_matches)
    highest_scoring_match = max(live_matches, key=lambda x: x.get("score_home", 0) + x.get("score_away", 0), default={})
    top_match_str = f"{highest_scoring_match.get('home')} {highest_scoring_match.get('score_home')}-{highest_scoring_match.get('score_away')} {highest_scoring_match.get('away')}" if highest_scoring_match else "N/A"

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.metric("🔴 Jogos ao Vivo", f"{total_live} partidas")
    with mcol2:
        st.metric("⚽ Total Golos Marcados", f"{total_goals} golos")
    with mcol3:
        st.metric("🏆 Ligas Ativas", f"{len(leagues_set)} ligas")
    with mcol4:
        st.metric("🔥 Jogo Mais Movimentado", top_match_str)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter Bar
    filter_c1, filter_c2 = st.columns(2)
    with filter_c1:
        all_leagues = ["Todas as Ligas"] + sorted(list(leagues_set))
        selected_league = st.selectbox("Filtrar por Liga / Competição:", options=all_leagues)

    with filter_c2:
        all_statuses = ["Todos os Tempos", "1º Tempo (1H)", "Intervalo (HT)", "2º Tempo (2H)"]
        selected_status = st.selectbox("Filtrar por Fase da Partida:", options=all_statuses)

    # Apply filters
    filtered_list = live_matches
    if selected_league != "Todas as Ligas":
        filtered_list = [m for m in filtered_list if m.get("league") == selected_league]
    
    if selected_status == "1º Tempo (1H)":
        filtered_list = [m for m in filtered_list if m.get("status") in ["1H", "1ST"]]
    elif selected_status == "Intervalo (HT)":
        filtered_list = [m for m in filtered_list if m.get("status") in ["HT", "INT"]]
    elif selected_status == "2º Tempo (2H)":
        filtered_list = [m for m in filtered_list if m.get("status") in ["2H", "2ND"]]

    st.markdown(f"#### ⚽ Lista de Partidas em Direto ({len(filtered_list)} de {total_live})")

    # Render Live Match Cards
    for idx, match in enumerate(filtered_list):
        with st.container(border=True):
            head_col, score_col, odd_col = st.columns([2.5, 2, 2.5], vertical_alignment="center")
            
            with head_col:
                minute = match.get("minute", 0)
                status_lbl = match.get("status", "1H")
                st.markdown(f"**{match.get('league')}** ({match.get('country')})")
                st.markdown(f"<span style='background-color: #ef4444; color: white; padding: 2px 8px; border-radius: 12px; font-weight: 700; font-size: 0.8rem;'>🔴 {minute}' min ({status_lbl})</span>", unsafe_allow_html=True)
                st.caption(f"Provedor: {match.get('provider', 'API Live')}")

            with score_col:
                st.markdown(f"""
                <div style="text-align: center; background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="font-size: 1.1rem; font-weight: 700;">{match.get('home')}</div>
                    <div style="font-size: 1.8rem; font-weight: 900; color: #38bdf8; margin: 4px 0;">{match.get('score_home')} - {match.get('score_away')}</div>
                    <div style="font-size: 1.1rem; font-weight: 700;">{match.get('away')}</div>
                </div>
                """, unsafe_allow_html=True)

            with odd_col:
                st.markdown("**Odds Ao Vivo (In-Play):**")
                o1, ox, o2 = st.columns(3)
                o1.metric("1 (Casa)", f"{match.get('odd_1', 2.00):.2f}")
                ox.metric("X (Empate)", f"{match.get('odd_x', 3.00):.2f}")
                o2.metric("2 (Fora)", f"{match.get('odd_2', 3.50):.2f}")

            events = match.get("events", [])
            if events:
                with st.expander("⚡ Cronologia de Eventos & xG Ao Vivo"):
                    st.write(f"**xG Estimado Ao Vivo:** Casa ({match.get('h_xg', 1.0)}) | Fora ({match.get('a_xg', 0.8)})")
                    for ev in events:
                        st.markdown(f"- {ev}")
