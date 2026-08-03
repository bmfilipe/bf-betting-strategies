import streamlit as st
import pandas as pd
import datetime
from services.gemini_ingestion import GeminiIngestionService
from services.odds_api_ingestion import OddsApiService
from services.oddsportal_ingestion import OddsPortalIngestionService
from services.api_football_ingestion import ApiFootballIngestionService
from config import DEFAULT_MOCK_MATCHES

def render_tab_ingestion():
    """Render Tab 1: Ingestão de Dados via Provedor Selecionado (The Odds API / OddsPortal / Gemini)."""
    today_str = datetime.date.today().strftime("%d/%m/%Y")
    active_provider = st.session_state.get("odds_provider", "The Odds API (the-odds-api.com)")

    st.subheader(f"🔍 Ingestão e Captação de Jogos em Tempo Real - HOJE ({today_str})")
    
    col_info, col_prov_badge = st.columns([3, 1])
    with col_info:
        st.write(f"Consulta a API/Feed ativo (**{active_provider}**) para obter jogos reais e cotações de futebol para **hoje ({today_str})** com odds completas (1X2, Golos, BTTS).")
    with col_prov_badge:
        st.success(f"🎯 **Provedor Ativo:**\n{active_provider}")
        st.caption("ℹ️ Podes alterar o provedor na **Área de Administrador**.")

    st.caption("ℹ️ **Origem das Odds:** As cotações (Odds) captadas representam a **Média de Consenso do Mercado Europeu / Global**, agregando os valores das principais casas reguladas (**Betfair Exchange**, **Pinnacle**, **Betano**, **Betclic**, **1xBet** e **OddsPortal**).")

    # Search Configuration Container
    with st.container(border=True):
        st.markdown(f"#### ⚙️ Filtros de Pesquisa ({active_provider})")
        col_f1, col_f2 = st.columns([2, 1])

        with col_f1:
            # Alphabetically sorted options starting with fixed default option
            country_options = [
                "Todas as Ligas/Países",
                "Alemanha (Bundesliga / 2. Bundesliga)",
                "Argentina (Liga Profesional)",
                "Áustria (Bundesliga)",
                "Bélgica (Pro League)",
                "Brasil (Brasileirão Serie A / Serie B)",
                "Dinamarca (Superliga)",
                "Escócia (Premiership)",
                "Espanha (La Liga / Segunda División)",
                "EUA / América do Norte (MLS)",
                "Europa (UEFA Champions / Europa League / Conference League)",
                "França (Ligue 1 / Ligue 2)",
                "Inglaterra (Premier League / Championship / League 1)",
                "Islandia (Primeira Liga / Segunda Liga)",
                "Itália (Serie A / Serie B)",
                "Noruega (Eliteserien)",
                "Países Baixos (Eredivisie)",
                "Portugal (Primeira Liga / Segunda Liga)",
                "Suécia (Allsvenskan)",
                "Suíça (Super League)",
                "Turquia (Süper Lig)"
            ]
            selected_countries = st.multiselect(
                "Filtrar por Países / Competições Alvo:",
                options=country_options,
                default=["Todas as Ligas/Países"]
            )

        with col_f2:
            max_matches = st.slider(
                "Quantidade de Jogos a Mapear:",
                min_value=5,
                max_value=50,
                value=20,
                step=5
            )

    col_btn, col_clear = st.columns([2, 1])

    with col_btn:
        btn_label = f"🔎 Pesquisar Jogos via {active_provider.split(' ')[0]}"
        if st.button(btn_label, type="primary", width="stretch"):
            if "The Odds API" in active_provider:
                with st.spinner(f"A obter cotações reais via The Odds API (www.the-odds-api.com) para até {max_matches} jogos de {today_str}..."):
                    odds_key = st.session_state.get("odds_api_key", "")
                    matches, msg = OddsApiService.fetch_today_matches(
                        odds_key,
                        selected_countries=selected_countries,
                        max_matches=max_matches
                    )
            elif "API-Football" in active_provider:
                with st.spinner(f"A obter jogos e cotações via API-Football (v3 - api-sports.io) para até {max_matches} jogos de {today_str}..."):
                    api_f_key = st.session_state.get("api_football_key", "")
                    matches, msg = ApiFootballIngestionService.fetch_today_matches(
                        api_f_key,
                        selected_countries=selected_countries,
                        max_matches=max_matches
                    )
            elif "OddsPortal" in active_provider:
                with st.spinner(f"A extrair cotações dinâmicas do OddsPortal Feed (www.oddsportal.com) para até {max_matches} jogos de {today_str}..."):
                    matches, msg = OddsPortalIngestionService.fetch_today_matches(
                        selected_countries=selected_countries,
                        max_matches=max_matches
                    )
            else:
                with st.spinner(f"A pesquisar na Web com Gemini 2.5 Flash até {max_matches} jogos reais de {today_str}..."):
                    matches, msg = GeminiIngestionService.fetch_today_matches(
                        st.session_state.get("gemini_key", ""),
                        selected_countries=selected_countries,
                        max_matches=max_matches
                    )
            
            # Filter out finished matches (keep only scheduled or live matches)
            finished_statuses = ["FINISHED", "FT", "AET", "PEN", "TERMINADO", "COMPLETED"]
            matches = [m for m in matches if str(m.get("status", "")).upper() not in finished_statuses]

            st.session_state["matches_data"] = matches
            st.session_state["last_ingestion_log"] = msg

            if matches:
                try:
                    from database.db import save_matches_to_db
                    save_matches_to_db(matches)
                except Exception as db_err:
                    print(f"[DB ERROR] Erro ao guardar em SQLite: {db_err}")

            if "Sucesso" in msg:
                st.success(msg)
            elif "Aviso" in msg:
                st.warning(msg)
            else:
                st.error(msg)

    with col_clear:
        if st.button("🗑️ Limpar Dados em Memória", width="stretch"):
            st.session_state["confirm_clear_ingestion"] = True

    # Security Confirmation Container for Clear Memory Action
    if st.session_state.get("confirm_clear_ingestion", False):
        with st.container(border=True):
            st.warning("⚠️ **Tem a certeza de que deseja limpar todos os dados em memória e na base de dados SQLite?** Todos os jogos captados e análises guardadas serão removidos.")
            col_c_yes, col_c_no, _ = st.columns([1, 1, 2])

            with col_c_yes:
                if st.button("✅ Sim, Limpar Tudo", type="primary", width="stretch"):
                    st.session_state["matches_data"] = []
                    st.session_state["analysed_results"] = []
                    st.session_state["last_ingestion_log"] = "Dados de memória e base de dados SQLite limpos."
                    st.session_state["confirm_clear_ingestion"] = False
                    try:
                        from database.db import clear_db
                        clear_db()
                    except Exception as db_err:
                        print(f"[DB ERROR] Erro ao limpar SQLite: {db_err}")
                    st.info("Memória de dados e base de dados SQLite limpas com sucesso.")
                    st.rerun()

            with col_c_no:
                if st.button("❌ Cancelar", width="stretch"):
                    st.session_state["confirm_clear_ingestion"] = False
                    st.rerun()

    if st.session_state.get("last_ingestion_log"):
        st.info(f"**Último Estado:** {st.session_state['last_ingestion_log']}")

    st.markdown("---")

    # Display matches
    matches = st.session_state.get("matches_data", [])
    if not matches:
        st.info("💡 **Nenhum jogo em memória de momento.** Clica no botão **'🔎 Pesquisar Jogos via <Provedor>'** acima para pesquisar partidas reais em tempo real.")
        return

    @st.fragment
    def render_matches_table_fragment(all_matches):
        # Controls bar above the table: Search input and Show count
        col_search, col_show, col_metric = st.columns([2, 1, 1])

        with col_search:
            search_query = st.text_input("🔍 Pesquisar em jogos encontrados (equipa, liga, mercado, data, resultado...):", "", key="ingest_search_query")

        with col_show:
            show_option = st.selectbox("Mostrar partidas:", options=[20, 50, 100, "Tudo"], index=0, key="ingest_show_option")

        with col_metric:
            st.metric("Total Jogos", f"{len(all_matches)}")

        # Ensure default date and result values exist
        for m in all_matches:
            if "date" not in m or not m["date"]:
                m["date"] = f"{today_str} 20:00"
            if "result" not in m or not m["result"]:
                m["result"] = "Por iniciar"

        # Apply search query filter
        filtered_matches = all_matches
        if search_query:
            q = search_query.lower()
            filtered_matches = [
                m for m in all_matches
                if q in str(m.get("home", "")).lower()
                or q in str(m.get("away", "")).lower()
                or q in str(m.get("country", "")).lower()
                or q in str(m.get("league", "")).lower()
                or q in str(m.get("market", "")).lower()
                or q in str(m.get("date", "")).lower()
                or q in str(m.get("result", "")).lower()
            ]

        # Apply limit
        if show_option != "Tudo":
            limit = int(show_option)
            display_matches = filtered_matches[:limit]
        else:
            display_matches = filtered_matches

        st.write(f"### 📋 Tabela de Jogos Mapeados ({len(display_matches)} de {len(all_matches)} exibidos)")

        df = pd.DataFrame(display_matches)
        if not df.empty:
            column_mapping = {
                "date": "Data Jogo",
                "country": "País",
                "league": "Liga",
                "home": "Equipa Casa",
                "away": "Equipa Fora",
                "odd_1": "Odd (1)",
                "odd_x": "Odd (X)",
                "odd_2": "Odd (2)",
                "odd_o05": "Odd (+0.5)",
                "odd_o15": "Odd (+1.5)",
                "odd_o25": "Odd (+2.5)",
                "odd_btts_yes": "Odd (BTTS Sim)",
                "odd_btts_no": "Odd (BTTS Não)",
                "market": "Mercado Recomendado",
                "result": "Resultado"
            }

            cols_present = [c for c in column_mapping.keys() if c in df.columns]
            display_df = df[cols_present].rename(columns=column_mapping)

            # Custom Pandas Styler for Mercado Recomendado & Live Match Rows
            def style_matches_table(data_df):
                def highlight_cells(row):
                    res_val = str(row.get("Resultado", "")).lower()
                    status_val = str(row.get("status", "")).upper()
                    is_live = "ao vivo" in res_val or "em curso" in res_val or "live" in res_val or status_val == "LIVE"
                    
                    styles = [''] * len(row)
                    
                    if "Mercado Recomendado" in row.index:
                        idx_m = row.index.get_loc("Mercado Recomendado")
                        styles[idx_m] = 'font-weight: bold; color: #38bdf8; background-color: rgba(56, 189, 248, 0.15);'
                    
                    if is_live:
                        if "Resultado" in row.index:
                            idx_r = row.index.get_loc("Resultado")
                            styles[idx_r] = 'font-weight: bold; color: #f59e0b; background-color: rgba(245, 158, 11, 0.25);'
                        for i in range(len(styles)):
                            if "Mercado Recomendado" in row.index and i == row.index.get_loc("Mercado Recomendado"):
                                continue
                            if not styles[i]:
                                styles[i] = 'background-color: rgba(245, 158, 11, 0.08);'
                    return styles

                return data_df.style.apply(highlight_cells, axis=1)

            styled_df = style_matches_table(display_df)
            st.dataframe(styled_df, width="stretch")

    render_matches_table_fragment(matches)

    with st.expander("📝 Editar ou Inserir Dados Manualmente (JSON)"):
        json_str = st.text_area(
            "Payload JSON dos Jogos",
            value=pd.Series([matches]).to_json(orient='records')[1:-1],
            height=200
        )
        if st.button("💾 Atualizar Dados da Tabela"):
            try:
                import json
                parsed = json.loads(json_str)
                st.session_state["matches_data"] = parsed
                st.success("Dados atualizados com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Formato JSON inválido: {str(e)}")
