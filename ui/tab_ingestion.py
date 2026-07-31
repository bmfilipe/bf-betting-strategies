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
            selected_countries = st.multiselect(
                "Filtrar por Países / Competições Alvo:",
                options=[
                    "Todas as Ligas/Países",
                    "Portugal (Primeira Liga / Segunda Liga)",
                    "Inglaterra (Premier League / Championship / League 1)",
                    "Espanha (La Liga / Segunda División)",
                    "Itália (Serie A / Serie B)",
                    "Alemanha (Bundesliga / 2. Bundesliga)",
                    "França (Ligue 1 / Ligue 2)",
                    "Europa (UEFA Champions / Europa League / Conference League)",
                    "Brasil (Brasileirão Serie A / Serie B)",
                    "Países Baixos (Eredivisie)",
                    "Bélgica (Pro League)",
                    "Turquia (Süper Lig)",
                    "Argentina (Liga Profesional)",
                    "EUA / América do Norte (MLS)",
                    "Escócia (Premiership)",
                    "Suécia (Allsvenskan)",
                    "Noruega (Eliteserien)",
                    "Dinamarca (Superliga)",
                    "Suíça (Super League)",
                    "Áustria (Bundesliga)",
                    "Outras Ligas Internacionais"
                ],
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
                    odds_key = st.session_state.get("odds_api_key", "0679363fc9fed7e8be5414173c5c1b8a")
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
            
            st.session_state["matches_data"] = matches
            st.session_state["last_ingestion_log"] = msg

            if "Sucesso" in msg:
                st.success(msg)
            elif "Aviso" in msg:
                st.warning(msg)
            else:
                st.error(msg)

    with col_clear:
        if st.button("🗑️ Limpar Dados em Memória", width="stretch"):
            st.session_state["matches_data"] = []
            st.session_state["analysed_results"] = []
            st.session_state["last_ingestion_log"] = "Dados de memória limpos."
            st.info("Memória de dados limpa com sucesso.")
            st.rerun()

    if st.session_state.get("last_ingestion_log"):
        st.info(f"**Último Estado:** {st.session_state['last_ingestion_log']}")

    st.markdown("---")

    # Display matches
    matches = st.session_state.get("matches_data", [])
    if not matches:
        st.info("💡 **Nenhum jogo em memória de momento.** Clica no botão **'🔎 Pesquisar Jogos de Hoje'** acima para pesquisar partidas reais em tempo real via Gemini Flash.")
        return

    # Controls bar above the table: Search input and Show count
    col_search, col_show, col_metric = st.columns([2, 1, 1])

    with col_search:
        search_query = st.text_input("🔍 Pesquisar em jogos encontrados (equipa, liga, mercado...):", "")

    with col_show:
        show_option = st.selectbox("Mostrar partidas:", options=[20, 50, 100, "Tudo"], index=0)

    with col_metric:
        st.metric("Total Jogos", f"{len(matches)}")

    # Apply search query filter
    filtered_matches = matches
    if search_query:
        q = search_query.lower()
        filtered_matches = [
            m for m in matches
            if q in str(m.get("home", "")).lower()
            or q in str(m.get("away", "")).lower()
            or q in str(m.get("country", "")).lower()
            or q in str(m.get("league", "")).lower()
            or q in str(m.get("market", "")).lower()
        ]

    # Apply limit
    if show_option != "Tudo":
        limit = int(show_option)
        display_matches = filtered_matches[:limit]
    else:
        display_matches = filtered_matches

    st.write(f"### 📋 Tabela de Jogos Mapeados ({len(display_matches)} de {len(matches)} exibidos)")

    df = pd.DataFrame(display_matches)
    if not df.empty:
        # Re-structure columns to prioritize 1X2, Total Goals, BTTS & Bold Recommended Market
        column_mapping = {
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
            "market": "Mercado Recomendado"
        }

        # Format columns if present
        cols_present = [c for c in column_mapping.keys() if c in df.columns]
        display_df = df[cols_present].rename(columns=column_mapping)

        # Apply bold styling to Mercado Recomendado column
        def bold_market(val):
            return 'font-weight: bold; color: #38bdf8; background-color: rgba(56, 189, 248, 0.15);'

        if "Mercado Recomendado" in display_df.columns:
            if hasattr(display_df.style, "map"):
                styled_df = display_df.style.map(bold_market, subset=["Mercado Recomendado"])
            else:
                styled_df = display_df.style.applymap(bold_market, subset=["Mercado Recomendado"])
            st.dataframe(styled_df, width="stretch")
        else:
            st.dataframe(display_df, width="stretch")

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
