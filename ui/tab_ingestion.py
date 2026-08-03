import streamlit as st
import pandas as pd
import datetime
from services.gemini_ingestion import GeminiIngestionService
from services.odds_api_ingestion import OddsApiService
from services.oddsportal_ingestion import OddsPortalIngestionService
from services.api_football_ingestion import ApiFootballIngestionService
from config import DEFAULT_MOCK_MATCHES

import unicodedata
from config import get_matches_for_selected_leagues, infer_country_and_league, normalize_team_name, deduplicate_matches_by_teams

def _strip_accents(text: str) -> str:
    """Normalize and strip accents for fuzzy keyword matching."""
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn').lower().strip()

def filter_matches_by_selection(matches: list, selected_countries: list, max_matches: int) -> tuple[list, str]:
    """
    Filter matches strictly by selected countries/leagues and cap at max_matches.
    Ensures matches cover selected leagues, belong strictly to TODAY'S DATE,
    and applies strict team uniqueness so no team plays more than one match per day.
    """
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    today_fmt = datetime.date.today().strftime("%d/%m/%Y")

    is_all = not selected_countries or "Todas as Ligas/Países" in selected_countries

    country_keywords_map = {
        "Portugal (Primeira Liga / Segunda Liga)": ["portugal", "betclic", "liga portugal", "primeira liga", "segunda liga", "benfica", "porto", "sporting", "braga"],
        "Inglaterra (Premier League / Championship / League 1)": ["inglaterra", "england", "premier league", "championship", "league 1"],
        "Espanha (La Liga / Segunda División)": ["espanha", "spain", "la liga", "segunda"],
        "Itália (Serie A / Serie B)": ["itália", "italy", "serie a", "serie b"],
        "Alemanha (Bundesliga / 2. Bundesliga)": ["alemanha", "germany", "bundesliga"],
        "França (Ligue 1 / Ligue 2)": ["frança", "france", "ligue 1", "ligue 2"],
        "Europa (UEFA Champions / Europa League / Conference League)": ["europa", "uefa", "champions", "europa league", "conference"],
        "Brasil (Brasileirão Serie A / Serie B)": ["brasil", "brazil", "brasileirão", "serie a", "serie b"],
        "Países Baixos (Eredivisie / Eerste Divisie)": ["paises baixos", "netherlands", "eredivisie", "holanda"],
        "Bélgica (Pro League / Challenger Pro League)": ["belgica", "belgium", "pro league"],
        "Turquia (Süper Lig / 1. Lig)": ["turquia", "turkey", "super lig"],
        "Argentina (Liga Profesional)": ["argentina", "liga profesional"],
        "EUA / América do Norte (MLS)": ["eua", "usa", "mls"],
        "Escócia (Premiership)": ["escocia", "scotland", "premiership", "celtic", "rangers", "hearts", "hibernian", "aberdeen"],
        "Suécia (Allsvenskan / Superettan)": ["suecia", "sweden", "allsvenskan"],
        "Noruega (Eliteserien / OBOS-ligaen)": ["noruega", "norway", "eliteserien"],
        "Dinamarca (Superliga / 1st Division)": ["dinamarca", "denmark", "superliga"],
        "Suíça (Super League / Challenge League)": ["suica", "switzerland", "swiss", "super league", "young boys", "basel", "servette", "zurich", "lugano", "st. gallen"],
        "Áustria (Bundesliga / 2. Liga)": ["austria", "austrian", "bundesliga", "salzburg", "sturm graz", "rapid wien"],
        "Polónia (Ekstraklasa / 1. Liga)": ["polonia", "poland", "ekstraklasa"],
        "Finlândia (Veikkausliiga / Ykkösliiga)": ["finlandia", "finland", "veikkausliiga", "ykkosliiga", "hjk", "kups", "sjk"],
        "Grécia (Super League 1 / Super League 2)": ["grecia", "greece", "super league", "olympiacos", "panathinaikos", "aek", "paok"],
        "República Checa (Chance Liga / FNL)": ["checa", "czech", "slavia", "sparta", "viktoria"],
        "Roménia (SuperLiga / Liga II)": ["romenia", "romania", "superliga", "fcsb", "cluj"],
        "Croácia (HNL / Prva NL)": ["croacia", "croatia", "hnl", "dinamo zagreb", "hajduk"],
        "Sérvia (SuperLiga / Prva Liga)": ["servia", "serbia", "estrela vermelha", "partizan"],
        "Japão (J1 League / J2 League)": ["japao", "japan", "j1 league", "j2 league", "vissel kobe"],
        "México (Liga MX / Liga de Expansión)": ["mexico", "liga mx", "club america", "tigres"],
        "Colômbia (Categoría Primera A / Primera B)": ["colombia", "primera a", "atletico nacional", "millonarios"]
    }

    active_kws = []
    if not is_all:
        for item in selected_countries:
            if item in country_keywords_map:
                active_kws.extend([_strip_accents(k) for k in country_keywords_map[item]])
            else:
                active_kws.append(_strip_accents(item))

    def match_belongs_to_selection(m):
        if is_all:
            return True
        match_norm = _strip_accents(f"{m.get('country', '')} {m.get('league', '')} {m.get('home', '')} {m.get('away', '')}")
        return any(kw in match_norm for kw in active_kws)

    valid_today_matches = []
    seen_teams = set()

    # 1. Enforce today's date strictly & filter input matches for selected countries
    if matches:
        for m in matches:
            m_raw_date = str(m.get("date", "")).strip()
            m_fmt_date = str(m.get("date_formatted", "")).strip()

            # Strict date checking: match MUST belong to TODAY's date
            if m_raw_date:
                m_date_clean = m_raw_date[:10]
                if m_date_clean != today_str and m_fmt_date != today_fmt:
                    continue  # Discard matches from future or past days

            c, l = infer_country_and_league(
                str(m.get("home", "")), str(m.get("away", "")),
                raw_league=str(m.get("league", "")),
                raw_country=str(m.get("country", ""))
            )
            m["country"] = c
            m["league"] = l

            if match_belongs_to_selection(m):
                m["date"] = today_str
                m["date_formatted"] = today_fmt
                home = str(m.get("home", "")).strip()
                away = str(m.get("away", "")).strip()
                h_norm = normalize_team_name(home)
                a_norm = normalize_team_name(away)
                if not h_norm or not a_norm or h_norm == a_norm:
                    continue
                if h_norm in seen_teams or a_norm in seen_teams:
                    continue

                # Coherence Guard for 1X2 Odds: ensure odd_1 belongs to Home and odd_2 to Away
                try:
                    o1_val = float(m.get("odd_1", 2.0) or 2.0)
                    o2_val = float(m.get("odd_2", 2.0) or 2.0)
                    h_xg_val = float(m.get("h_xg", 1.5) or 1.5)
                    a_xg_val = float(m.get("a_xg", 1.0) or 1.0)
                    if (h_xg_val >= a_xg_val + 0.3) and (o1_val >= o2_val + 0.8):
                        m["odd_1"] = o2_val
                        m["odd_2"] = o1_val
                    elif (a_xg_val >= h_xg_val + 0.3) and (o2_val >= o1_val + 0.8):
                        m["odd_1"] = o2_val
                        m["odd_2"] = o1_val
                except Exception:
                    pass

                seen_teams.add(h_norm)
                seen_teams.add(a_norm)
                valid_today_matches.append(m)

    final_matches = valid_today_matches[:max_matches]

    sel_str = ", ".join(selected_countries) if selected_countries else "Todas as Ligas/Países"
    if not final_matches:
        return [], f"Aviso: Nenhuma partida encontrada para as ligas selecionadas ({sel_str}) na data de HOJE ({today_fmt})."

    if is_all:
        info_str = f"Mapeadas {len(final_matches)} partidas de HOJE ({today_fmt}) (limite: {max_matches} jogos)."
    else:
        info_str = f"Mapeadas {len(final_matches)} partidas de HOJE ({today_fmt}) cobrindo as ligas selecionadas: {sel_str} (limite: {max_matches} jogos)."

    return final_matches, info_str

def render_tab_ingestion():
    """Render Tab 1: Ingestão de Dados via Provedor Selecionado (The Odds API / OddsPortal / Gemini)."""
    # Sanitize session state matches to ensure no legacy 'Internacional' strings remain
    if "matches_data" in st.session_state and st.session_state["matches_data"]:
        for m in st.session_state["matches_data"]:
            c, l = infer_country_and_league(
                m.get("home", ""), m.get("away", ""),
                raw_league=m.get("league", ""),
                raw_country=m.get("country", "")
            )
            m["country"] = c
            m["league"] = l

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
<<<<<<< HEAD
                options=country_options,
=======
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
                    "Países Baixos (Eredivisie / Eerste Divisie)",
                    "Bélgica (Pro League / Challenger Pro League)",
                    "Turquia (Süper Lig / 1. Lig)",
                    "Argentina (Liga Profesional)",
                    "EUA / América do Norte (MLS)",
                    "Escócia (Premiership)",
                    "Suécia (Allsvenskan / Superettan)",
                    "Noruega (Eliteserien / OBOS-ligaen)",
                    "Dinamarca (Superliga / 1st Division)",
                    "Suíça (Super League / Challenge League)",
                    "Áustria (Bundesliga / 2. Liga)",
                    "Polónia (Ekstraklasa / 1. Liga)",
                    "Finlândia (Veikkausliiga / Ykkösliiga)",
                    "Grécia (Super League 1 / Super League 2)",
                    "República Checa (Chance Liga / FNL)",
                    "Roménia (SuperLiga / Liga II)",
                    "Croácia (HNL / Prva NL)",
                    "Sérvia (SuperLiga / Prva Liga)",
                    "Japão (J1 League / J2 League)",
                    "México (Liga MX / Liga de Expansión)",
                    "Colômbia (Categoría Primera A / Primera B)"
                ],
>>>>>>> bcd5ae0ad2a3dcc5840cd7d5d3acfe89ef908fe4
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

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Search and Clear Action Buttons inside the Container
        col_btn, col_clear = st.columns([2, 1])

<<<<<<< HEAD
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
=======
        with col_btn:
            btn_label = f"🔎 Pesquisar Jogos via {active_provider.split(' ')[0]}"
            if st.button(btn_label, type="primary", width="stretch"):
                if "The Odds API" in active_provider:
                    with st.spinner(f"A obter cotações reais via The Odds API para até {max_matches} jogos..."):
                        odds_key = st.session_state.get("odds_api_key", "")
                        raw_matches, msg = OddsApiService.fetch_today_matches(
                            odds_key,
                            selected_countries=selected_countries,
                            max_matches=max_matches
                        )
                elif "API-Football" in active_provider:
                    with st.spinner(f"A obter jogos via API-Football para até {max_matches} jogos..."):
                        api_f_key = st.session_state.get("api_football_key", "")
                        raw_matches, msg = ApiFootballIngestionService.fetch_today_matches(
                            api_f_key,
                            selected_countries=selected_countries,
                            max_matches=max_matches
                        )
                elif "OddsPortal" in active_provider:
                    with st.spinner(f"A extrair cotações do OddsPortal Feed para até {max_matches} jogos..."):
                        raw_matches, msg = OddsPortalIngestionService.fetch_today_matches(
                            selected_countries=selected_countries,
                            max_matches=max_matches
                        )
                else:
                    with st.spinner(f"A pesquisar na Web com Gemini 2.5 Flash até {max_matches} jogos..."):
                        raw_matches, msg = GeminiIngestionService.fetch_today_matches(
                            st.session_state.get("gemini_key", ""),
                            selected_countries=selected_countries,
                            max_matches=max_matches
                        )
                
                # Apply strict filtering by selected countries and limit by max_matches
                matches, filter_info = filter_matches_by_selection(raw_matches, selected_countries, max_matches)
>>>>>>> bcd5ae0ad2a3dcc5840cd7d5d3acfe89ef908fe4

                st.session_state["matches_data"] = matches
                st.session_state["last_ingestion_log"] = f"{msg} | {filter_info}"

                if matches:
                    try:
                        from database.db import save_matches_to_db
                        save_matches_to_db(matches)
                    except Exception as db_err:
                        print(f"[DB ERROR] Erro ao guardar em SQLite: {db_err}")

                if "Sucesso" in msg:
                    st.success(f"{msg} ({filter_info})")
                elif "Aviso" in msg:
                    st.warning(f"{msg} ({filter_info})")
                else:
                    st.error(f"{msg} ({filter_info})")

        with col_clear:
            if st.button("🗑️ Limpar Dados em Memória", width="stretch"):
                st.session_state["matches_data"] = []
                st.session_state["analysed_results"] = []
                st.session_state["last_ingestion_log"] = "Dados de memória e base de dados SQLite limpos."
                try:
                    from database.db import clear_db
                    clear_db()
                except Exception as db_err:
<<<<<<< HEAD
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
=======
                    print(f"[DB ERROR] Erro ao limpar SQLite: {db_err}")
                st.info("Memória de dados e base de dados SQLite limpas com sucesso.")
                st.rerun()
>>>>>>> bcd5ae0ad2a3dcc5840cd7d5d3acfe89ef908fe4

    if st.session_state.get("last_ingestion_log"):
        st.info(f"**Último Estado:** {st.session_state['last_ingestion_log']}")

    st.markdown("---")

    # Display matches
    matches = st.session_state.get("matches_data", [])
    if not matches:
<<<<<<< HEAD
        st.info("💡 **Nenhum jogo em memória de momento.** Clica no botão **'🔎 Pesquisar Jogos via <Provedor>'** acima para pesquisar partidas reais em tempo real.")
=======
        st.info("💡 **Nenhum jogo em memória de momento.** Clica no botão **'🔎 Pesquisar Jogos'** acima para pesquisar partidas reais em tempo real.")
>>>>>>> bcd5ae0ad2a3dcc5840cd7d5d3acfe89ef908fe4
        return

    @st.fragment
    def render_matches_table_fragment(all_matches):
        col_search, col_show, col_metric = st.columns([2, 1, 1])

        with col_search:
            search_query = st.text_input("🔍 Pesquisar em jogos encontrados (equipa, liga, mercado, data, resultado...):", "", key="ingest_search_query")

        with col_show:
            show_option = st.selectbox("Mostrar partidas:", options=[20, 50, 100, "Tudo"], index=0, key="ingest_show_option")

        with col_metric:
            st.metric("Total Jogos", f"{len(all_matches)}")

<<<<<<< HEAD
        # Ensure default date and result values exist
        for m in all_matches:
            if "date" not in m or not m["date"]:
                m["date"] = f"{today_str} 20:00"
            if "result" not in m or not m["result"]:
                m["result"] = "Por iniciar"

        # Apply search query filter
=======
>>>>>>> bcd5ae0ad2a3dcc5840cd7d5d3acfe89ef908fe4
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

        if show_option != "Tudo":
            limit = int(show_option)
            display_matches = filtered_matches[:limit]
        else:
            display_matches = filtered_matches

        st.write(f"### 📋 Tabela de Jogos Mapeados ({len(display_matches)} de {len(all_matches)} exibidos)")

        df = pd.DataFrame(display_matches)
        if not df.empty:
            column_mapping = {
<<<<<<< HEAD
                "date": "Data Jogo",
=======
                "date_formatted": "Data do Jogo",
>>>>>>> bcd5ae0ad2a3dcc5840cd7d5d3acfe89ef908fe4
                "country": "País",
                "league": "Liga",
                "home": "Equipa Casa",
                "away": "Equipa Fora",
                "odd_1": "Odd (1)",
                "odd_x": "Odd (X)",
                "odd_2": "Odd (2)",
                "odd_1x": "Odd (1X)",
                "odd_x2": "Odd (X2)",
                "odd_o05": "Odd (+0.5)",
                "odd_o15": "Odd (+1.5)",
                "odd_o25": "Odd (+2.5)",
                "odd_o35": "Odd (+3.5)",
                "odd_btts_yes": "Odd (BTTS Sim)",
                "odd_btts_no": "Odd (BTTS Não)",
                "market": "Mercado Recomendado",
                "result": "Resultado"
            }

            cols_present = [c for c in column_mapping.keys() if c in df.columns]
            display_df = df[cols_present].rename(columns=column_mapping)

<<<<<<< HEAD
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
=======
            if "País" in display_df.columns:
                for idx in display_df.index:
                    home_val = str(display_df.at[idx, "Equipa Casa"]) if "Equipa Casa" in display_df.columns else ""
                    away_val = str(display_df.at[idx, "Equipa Fora"]) if "Equipa Fora" in display_df.columns else ""
                    league_val = str(display_df.at[idx, "Liga"]) if "Liga" in display_df.columns else ""
                    country_val = str(display_df.at[idx, "País"]) if "País" in display_df.columns else ""
                    c, l = infer_country_and_league(home_val, away_val, raw_league=league_val, raw_country=country_val)
                    display_df.at[idx, "País"] = c
                    if "Liga" in display_df.columns and l:
                        display_df.at[idx, "Liga"] = l

            def bold_market(val):
                return 'font-weight: bold; color: #38bdf8; background-color: rgba(56, 189, 248, 0.15);'

            if "Mercado Recomendado" in display_df.columns:
                style_fn = getattr(display_df.style, "map", getattr(display_df.style, "applymap", None))
                if style_fn:
                    styled_df = style_fn(bold_market, subset=["Mercado Recomendado"])
                    st.dataframe(styled_df, width="stretch")
                else:
                    st.dataframe(display_df, width="stretch")
            else:
                st.dataframe(display_df, width="stretch")
>>>>>>> bcd5ae0ad2a3dcc5840cd7d5d3acfe89ef908fe4

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
