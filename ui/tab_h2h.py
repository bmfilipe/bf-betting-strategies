import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from services import H2HScraperService
from database.db import load_matches_from_db, load_h2h_history_from_db
from models import PoissonEngine

def render_tab_h2h():
    """Render Page: ⚔️ Comparador de Equipas & Confronto Direto (H2H Web Scraping)."""
    st.subheader("⚔️ Comparador de Equipas & Confronto Direto (H2H)")
    st.write("Análise quantitativa do histórico de jogos, médias de golos, performance defensiva e matriz de probabilidades comparativa por *Web Scraping*.")

    # Gather known team names from existing database matches
    existing_matches = load_matches_from_db()
    known_teams = set()
    for m in existing_matches:
        if m.get("home"):
            known_teams.add(m.get("home"))
        if m.get("away"):
            known_teams.add(m.get("away"))
    
    sorted_teams = sorted(list(known_teams))
    if not sorted_teams:
        sorted_teams = ["Benfica", "Porto", "Sporting CP", "Real Madrid", "Barcelona", "Arsenal", "Liverpool", "Bayern Munique"]

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("#### 🛡️ Equipa A (Casa / Referência)")
        team_a_select = st.selectbox("Selecionar Equipa A (existente na BD):", options=sorted_teams, index=0, key="h2h_select_a")
        team_a_custom = st.text_input("Ou digita o nome de outra Equipa A:", placeholder="Ex: Manchester City", key="h2h_custom_a")
        team_a = team_a_custom.strip() if team_a_custom.strip() else team_a_select

    with col_t2:
        st.markdown("#### ⚔️ Equipa B (Fora / Adversário)")
        default_b_idx = 1 if len(sorted_teams) > 1 else 0
        team_b_select = st.selectbox("Selecionar Equipa B (existente na BD):", options=sorted_teams, index=default_b_idx, key="h2h_select_b")
        team_b_custom = st.text_input("Ou digita o nome de outra Equipa B:", placeholder="Ex: Real Madrid", key="h2h_custom_b")
        team_b = team_b_custom.strip() if team_b_custom.strip() else team_b_select

    st.markdown("<br>", unsafe_allow_html=True)

    col_opt, col_act = st.columns([1, 2], vertical_alignment="center")
    with col_opt:
        force_scraping = st.checkbox("🔄 Forçar Web Scraping Atualizado (Ignorar Cache SQLite)", value=False)

    with col_act:
        run_comp = st.button("⚔️ Executar Comparação & Web Scraping", type="primary", width="stretch")

    if run_comp or "h2h_active_result" in st.session_state:
        if run_comp:
            if team_a == team_b:
                st.error("Por favor seleciona duas equipas diferentes para a análise comparativa.")
                return

            with st.spinner(f"A recolher dados de estatísticas e confronto direto entre {team_a} e {team_b}..."):
                result = H2HScraperService.get_h2h_comparison(team_a, team_b, force_refresh=force_scraping)
                st.session_state["h2h_active_result"] = result

        result = st.session_state.get("h2h_active_result", {})
        if not result:
            return

        st.markdown("---")

        # Cache Status Notification
        if result.get("from_cache", False):
            st.info(f"📂 **Dados de Confronto Direto carregados da Base de Dados SQLite** (`team_h2h_history`). Atualizado em: `{result.get('scraped_at')}`")
        else:
            st.success(f"🟢 **Web Scraping concluído com sucesso!** Dados de `{team_a}` vs `{team_b}` guardados no SQLite. Fonte: `{result.get('source')}`")

        ta_name = result.get("team_a", "Equipa A")
        tb_name = result.get("team_b", "Equipa B")
        ta_stats = result.get("team_a_stats", {})
        tb_stats = result.get("team_b_stats", {})

        # Top Metric Cards Comparison
        st.markdown(f"### 📊 Análise Comparativa: {ta_name} vs {tb_name}")

        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        with sc1:
            st.markdown(f"**Guia de Forma (Últimos 5)**")
            st.markdown(f"**{ta_name}:** `{ta_stats.get('form')}`")
            st.markdown(f"**{tb_name}:** `{tb_stats.get('form')}`")
        with sc2:
            st.markdown(f"**Golos Marcados (Média)**")
            st.markdown(f"**{ta_name}:** `{ta_stats.get('avg_scored')} golos`")
            st.markdown(f"**{tb_name}:** `{tb_stats.get('avg_scored')} golos`")
        with sc3:
            st.markdown(f"**xG Estimado**")
            st.markdown(f"**{ta_name}:** `{ta_stats.get('xg')}`")
            st.markdown(f"**{tb_name}:** `{tb_stats.get('xg')}`")
        with sc4:
            st.markdown(f"**Over 2.5 Golos %**")
            st.markdown(f"**{ta_name}:** `{ta_stats.get('over25_pct')}%`")
            st.markdown(f"**{tb_name}:** `{tb_stats.get('over25_pct')}%`")
        with sc5:
            st.markdown(f"**Ambas Marcam (BTTS) %**")
            st.markdown(f"**{ta_name}:** `{ta_stats.get('btts_pct')}%`")
            st.markdown(f"**{tb_name}:** `{tb_stats.get('btts_pct')}%`")

        st.markdown("<br>", unsafe_allow_html=True)

        # Plotly Comparative Charts
        ch_col1, ch_col2 = st.columns(2)

        with ch_col1:
            st.markdown("#### 📈 Comparação de Ataque vs Defesa (Média de Golos)")
            categories = ["Golos Marcados", "Golos Sofridos", "xG Esperado"]
            fig_bar = go.Figure(data=[
                go.Bar(name=ta_name, x=categories, y=[ta_stats.get('avg_scored'), ta_stats.get('avg_conceded'), ta_stats.get('xg')], marker_color='#38bdf8'),
                go.Bar(name=tb_name, x=categories, y=[tb_stats.get('avg_scored'), tb_stats.get('avg_conceded'), tb_stats.get('xg')], marker_color='#f43f5e')
            ])
            fig_bar.update_layout(barmode='group', template='plotly_dark', margin=dict(l=20, r=20, t=30, b=20), height=300)
            st.plotly_chart(fig_bar, width="stretch")
        with ch_col2:
            st.markdown("#### ⚽ Histórico de Confrontos Diretos (H2H)")
            total_m = result.get("total_matches", 0)
            wins_a = result.get("team_a_wins", 0)
            wins_b = result.get("team_b_wins", 0)
            draws = result.get("draws", 0)

            labels = [f"Vitórias {ta_name}", f"Vitórias {tb_name}", "Empates"]
            values = [wins_a, wins_b, draws]
            colors = ['#38bdf8', '#f43f5e', '#e2e8f0']

            fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=colors)])
            fig_pie.update_layout(template='plotly_dark', margin=dict(l=20, r=20, t=30, b=20), height=300)
            st.plotly_chart(fig_pie, width="stretch")

        # Historical Match Table
        st.markdown(f"#### 📜 Histórico Recente de Jogos H2H ({total_m} partidas registadas)")
        h2h_list = result.get("h2h_matches", [])
        if h2h_list:
            df_h2h = pd.DataFrame(h2h_list)
            df_h2h.columns = ["Data", "Época", "Competição", "Equipa Casa", "Equipa Fora", "Golos Casa", "Golos Fora", "Vencedor"]
            st.dataframe(df_h2h, width="stretch", hide_index=True)

        # Poisson Simulation Projection for Team A vs Team B
        st.markdown(f"#### 🔮 Matriz de Poisson Preditiva ({ta_name} vs {tb_name})")
        with st.container(border=True):
            exp_h = float(ta_stats.get("avg_scored", 1.5))
            exp_a = float(tb_stats.get("avg_scored", 1.0))

            probs = PoissonEngine.calculate_match_probabilities(exp_h, exp_a)
            
            p_c1, p_c2, p_c3, p_c4, p_c5 = st.columns(5)
            p_c1.metric(f"Vitória {ta_name} (1)", f"{probs.get('prob_home_win', 0)*100:.1f}%", f"Odd Justa: {probs.get('fair_odd_1', 1.0):.2f}")
            p_c2.metric("Empate (X)", f"{probs.get('prob_draw', 0)*100:.1f}%", f"Odd Justa: {probs.get('fair_odd_x', 1.0):.2f}")
            p_c3.metric(f"Vitória {tb_name} (2)", f"{probs.get('prob_away_win', 0)*100:.1f}%", f"Odd Justa: {probs.get('fair_odd_2', 1.0):.2f}")
            p_c4.metric("Total +2.5 Golos", f"{probs.get('prob_over_25', 0)*100:.1f}%", f"Odd Justa: {probs.get('fair_odd_o25', 1.0):.2f}")
            p_c5.metric("Ambas Marcam (Sim)", f"{probs.get('prob_btts_yes', 0)*100:.1f}%", f"Odd Justa: {probs.get('fair_odd_btts_yes', 1.0):.2f}")
