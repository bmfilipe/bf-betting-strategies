import streamlit as st
import pandas as pd
import math
import plotly.express as px
import plotly.graph_objects as go
from models.poisson import PoissonEngine

def render_tab_analysis():
    """Render Tab 2: Análise Estatística Quantitativa, Estratégia & H2H."""
    st.subheader("📊 Motor Estatístico de Poisson, Estratégias & +EV")
    st.write("Análise quantitativa completa dos mercados principais (1X2, Total de Golos, Ambas Marcam) com base na distribuição de Poisson 7x7, Critério de Kelly e Histórico H2H.")

    matches = st.session_state.get("matches_data", [])
    if not matches:
        st.info("💡 **Nenhum jogo em memória de momento.** Por favor, acede à aba 'Obter Jogos' e clica em **'Pesquisar Jogos de Hoje'**.")
        return

    engine = PoissonEngine()

    def safe_f(val, default=1.0):
        if val is None: return default
        try: return float(val)
        except (ValueError, TypeError): return default

    def safe_s(val, default=""):
        if val is None: return default
        return str(val)

    # Multi-market evaluation per match
    evaluated_markets = []
    matches_meta = {}

    for m in matches:
        home = safe_s(m.get("home"), "Casa")
        away = safe_s(m.get("away"), "Fora")
        match_name = f"{home} vs. {away}"
        country = safe_s(m.get("country"), "Geral")
        league = safe_s(m.get("league"), "Geral")

        h_xg = safe_f(m.get("h_xg"), 1.5)
        a_xg = safe_f(m.get("a_xg"), 1.0)
        h_xga = safe_f(m.get("h_xga"), 1.0)
        a_xga = safe_f(m.get("a_xga"), 1.5)

        base_res = engine.analyze_match(
            home=home, away=away, h_xg=h_xg, a_xg=a_xg, h_xga=h_xga, a_xga=a_xga,
            odd=safe_f(m.get("odd"), 1.50), market=safe_s(m.get("market"), "Vitória Casa (1)"),
            country=country, league=league
        )

        matches_meta[match_name] = {
            "meta": base_res,
            "home_form": safe_s(m.get("home_form"), "V-E-V-D-V"),
            "away_form": safe_s(m.get("away_form"), "E-D-V-V-D"),
            "h2h_summary": safe_s(m.get("h2h_summary"), "Sem histórico recente registrado.")
        }

        # Defined core and advanced market odds
        odd_1_val = safe_f(m.get("odd_1"), safe_f(m.get("odd"), 1.60))
        odd_x_val = safe_f(m.get("odd_x"), 3.80)
        odd_2_val = safe_f(m.get("odd_2"), 4.50)

        market_odds_list = [
            ("Resultado Final (1X2)", "Vitória Casa (1)", odd_1_val),
            ("Resultado Final (1X2)", "Empate (X)", odd_x_val),
            ("Resultado Final (1X2)", "Vitória Fora (2)", odd_2_val),
            ("Dupla Hipótese", "Dupla Hipótese (1X)", safe_f(m.get("odd_1x"), round(1.0 / ((1.0/odd_1_val) + (1.0/odd_x_val)), 2))),
            ("Dupla Hipótese", "Dupla Hipótese (X2)", safe_f(m.get("odd_x2"), round(1.0 / ((1.0/odd_x_val) + (1.0/odd_2_val)), 2))),
            ("Total de Golos", "Total +0.5 Golos", safe_f(m.get("odd_o05"), 1.06)),
            ("Total de Golos", "Total +1.5 Golos", safe_f(m.get("odd_o15"), 1.25)),
            ("Total de Golos", "Total +2.5 Golos", safe_f(m.get("odd_o25"), 1.80)),
            ("Total de Golos", "Total +3.5 Golos", safe_f(m.get("odd_o35"), 2.90)),
            ("Ambas Marcam", "Ambas Marcam (Sim)", safe_f(m.get("odd_btts_yes"), 1.75)),
            ("Ambas Marcam", "Ambas Marcam (Não)", safe_f(m.get("odd_btts_no"), 1.95)),
            ("Empate Anula", "Empate Anula Casa (DNB 1)", safe_f(m.get("odd_dnb1"), round(odd_1_val * 0.75, 2))),
            ("Empate Anula", "Empate Anula Fora (DNB 2)", safe_f(m.get("odd_dnb2"), round(odd_2_val * 0.75, 2))),
            ("Handicap Asiático", "Handicap Asiático Casa (AH -0.5)", odd_1_val),
            ("Handicap Asiático", "Handicap Asiático Fora (AH +0.5)", safe_f(m.get("odd_x2"), round(1.0 / ((1.0/odd_x_val) + (1.0/odd_2_val)), 2))),
            ("Handicap Asiático", "Handicap Asiático Casa (AH +0.5)", safe_f(m.get("odd_1x"), round(1.0 / ((1.0/odd_1_val) + (1.0/odd_x_val)), 2))),
            ("Handicap Asiático", "Handicap Asiático Fora (AH -0.5)", odd_2_val)
        ]

        m_map = base_res["MarketMap"]

        for group, market_name, odd_val in market_odds_list:
            if odd_val <= 1.0 or math.isnan(odd_val):
                continue  # Prevent 0-odd or invalid lines

            prob_est = m_map.get(market_name, 50.0)
            prob_imp = engine.calculate_implied_prob(odd_val)
            ev = engine.calculate_ev(prob_est, odd_val)

            evaluated_markets.append({
                "País": country,
                "Liga": league,
                "Jogo": match_name,
                "EstratégiaGrupo": group,
                "Mercado": market_name,
                "Odd": round(odd_val, 2),
                "Prob. Implícita (%)": round(prob_imp, 1),
                "Prob. Estimada (%)": round(prob_est, 1),
                "Expected Value (+EV) (%)": ev,
                "ExpGoalsHome": base_res["ExpGoalsHome"],
                "ExpGoalsAway": base_res["ExpGoalsAway"]
            })

    # Interactive Filter Controls
    with st.container(border=True):
        st.markdown("#### 🎛️ Filtros de Análise, Estratégias & Gestão de Banca")

        with st.expander("ℹ️ Como Interpretar as Métricas (xG, +EV e Critério de Kelly)"):
            st.markdown(r"""
            - **Exp. Golos Casa / Fora (xG Ajustado)**: Expectativa matemática de golos a marcar com base no poder ofensivo ($xG$) da equipa e nas concessões defensivas ($xGA$) do adversário.
            - **Expected Value (+EV %)**: Vantagem matemática em relação à odd da casa de apostas.
              - **$+EV > 0\%$**: Aposta com valor positivo. A probabilidade estimada pelo modelo é superior à probabilidade implícita da odd. A longo prazo gera lucro.
              - **$-EV < 0\%$**: Aposta sem valor. A odd oferecida pela casa é demasiado baixa para o risco envolvido.
            - **KellyStake (%) & Stake Recomendada (€)**: Fórmula matemática de John Kelly para dimensionamento ótimo de capital.
              - Se $+EV \le 0\%$, a stake recomendada é **0.00 €** (não apostar).
              - Se $+EV > 0\%$, calcula a percentagem exata da tua banca a arriscar em função da margem de vantagem.
            - **Forma Recente (Últimos 5 jogos)**: Ordenada da esquerda para a direita, sendo a letra da **extrema-direita a partida mais recente**.
            """)

        col_t1, col_t2, col_t3, col_t4 = st.columns(4)

        with col_t1:
            predefined_countries = [
                "Todos",
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
            ]
            actual_countries = list(set(m["País"] for m in evaluated_markets))
            for c in sorted(actual_countries):
                if c not in predefined_countries:
                    predefined_countries.append(c)
            sel_country = st.selectbox("Filtrar por País / Região:", predefined_countries)

        with col_t2:
            strategy_options = [
                "Todas as Estratégias",
                "Resultado Final (1X2)",
                "Total de Golos (+0.5, +1.5, +2.5)",
                "Ambas Marcam (BTTS Sim / Não)",
                "Apostas Apenas +EV (EV > 0%)"
            ]
            sel_strategy = st.selectbox("Filtrar por Estratégia de Mercado:", strategy_options)

        with col_t3:
            min_ev_filter = st.slider("EV Mínimo (+EV %):", min_value=-20.0, max_value=30.0, value=0.0, step=1.0)

        with col_t4:
            user_bankroll = st.number_input("Tua Banca Total (€):", value=100.0, step=10.0, min_value=10.0)

    # Recalculate Kelly stakes and calculate Retorno/Lucro based on user bankroll
    for item in evaluated_markets:
        k_pct, k_eur = engine.calculate_kelly_stake(
            prob_estimated_pct=item["Prob. Estimada (%)"],
            odd=item["Odd"],
            bankroll=user_bankroll,
            fraction=0.25
        )
        retorno_bruto = round(k_eur * item["Odd"], 2)
        lucro_liquido = round(retorno_bruto - k_eur, 2)

        item["KellyStake (%)"] = k_pct
        item["Stake Recomendada (€)"] = k_eur
        item["Retorno (se acertar) (€)"] = retorno_bruto
        item["Lucro Líquido (€)"] = lucro_liquido

    # Filtered dataset
    filtered_list = evaluated_markets
    if sel_country != "Todos":
        filtered_list = [m for m in filtered_list if m["País"] == sel_country]

    if sel_strategy == "Resultado Final (1X2)":
        filtered_list = [m for m in filtered_list if m["EstratégiaGrupo"] == "Resultado Final (1X2)"]
    elif sel_strategy == "Total de Golos (+0.5, +1.5, +2.5)":
        filtered_list = [m for m in filtered_list if m["EstratégiaGrupo"] == "Total de Golos"]
    elif sel_strategy == "Ambas Marcam (BTTS Sim / Não)":
        filtered_list = [m for m in filtered_list if m["EstratégiaGrupo"] == "Ambas Marcam"]
    elif sel_strategy == "Apostas Apenas +EV (EV > 0%)":
        filtered_list = [m for m in filtered_list if m["Expected Value (+EV) (%)"] > 0]

    filtered_list = [m for m in filtered_list if m["Expected Value (+EV) (%)"] >= min_ev_filter]

    # Save filtered matches to session state for Tab 3 consistency
    st.session_state["analysed_results"] = filtered_list if filtered_list else evaluated_markets

    # Controls bar above the table: Search input, Show count, and Total Metric
    col_search, col_show, col_metric = st.columns([2, 1, 1])

    with col_search:
        search_query = st.text_input("🔍 Pesquisar em jogos encontrados (equipa, liga, mercado...):", "", key="search_analysis_tbl")

    with col_show:
        show_option = st.selectbox("Mostrar partidas:", options=[20, 50, 100, "Tudo"], index=0, key="show_analysis_tbl")

    with col_metric:
        st.metric("Total Jogos", f"{len(filtered_list)}")

    # Apply search query filter
    searched_list = filtered_list
    if search_query:
        q = search_query.lower()
        searched_list = [
            m for m in filtered_list
            if q in str(m.get("País", "")).lower()
            or q in str(m.get("Liga", "")).lower()
            or q in str(m.get("Jogo", "")).lower()
            or q in str(m.get("Mercado", "")).lower()
        ]

    # Apply limit
    if show_option != "Tudo":
        limit = int(show_option)
        display_list = searched_list[:limit]
    else:
        display_list = searched_list

    # Construct DataFrame for summary display
    df_summary = pd.DataFrame(display_list if display_list else (filtered_list if filtered_list else evaluated_markets))
    display_cols = [
        "País", "Liga", "Jogo", "Mercado", "Odd",
        "Prob. Implícita (%)", "Prob. Estimada (%)",
        "Expected Value (+EV) (%)", "KellyStake (%)", "Stake Recomendada (€)",
        "Retorno (se acertar) (€)", "Lucro Líquido (€)"
    ]

    # Visual Table Header & Collapsible Guide
    st.write(f"### 📈 Tabela Quantitativa de Valor Esperado ({len(display_list)} de {len(filtered_list)} exibidos)")

    with st.expander("📖 Guia de Leitura da Tabela (O que representa cada coluna?)", expanded=False):
        st.markdown(r"""
        - **Odd**: Cotação oferecida pela casa de apostas.
        - **Prob. Implícita (%)**: A probabilidade teórica atribuída pela casa ($100 / \text{Odd}$).
        - **Prob. Estimada (%)**: A probabilidade estatística real calculada pelo modelo de Poisson 7x7.
        - **Expected Value (+EV %)**: A tua vantagem matemática. Se for **verde (+EV > 0%)**, a aposta tem lucro esperado no longo prazo!
        - **KellyStake (%)**: Percentagem da tua banca total a arriscar recomendada pelo Critério de Kelly Fracionado (1/4 Kelly).
        - **Stake Recomendada (€)**: O montante em Euros a apostar com base na tua Banca Total (ex: de uma banca de 100€).
        - **Retorno (se acertar) (€)**: O valor bruto total pago pela casa em caso de vitória ($\text{Stake} \times \text{Odd}$).
        - **Lucro Líquido (€)**: O teu ganho limpo/líquido em caso de acerto ($\text{Retorno} - \text{Stake}$).
        """)

    def color_ev(val):
        if val > 0:
            return 'background-color: rgba(16, 185, 129, 0.25); color: #10b981; font-weight: bold;'
        else:
            return 'background-color: rgba(239, 68, 68, 0.15); color: #ef4444;'

    if hasattr(df_summary[display_cols].style, "map"):
        styled_df = df_summary[display_cols].style.map(color_ev, subset=['Expected Value (+EV) (%)'])
    else:
        styled_df = df_summary[display_cols].style.applymap(color_ev, subset=['Expected Value (+EV) (%)'])

    # Interactive DataFrame with multi-row selection
    st.info("💡 **Dica:** Podes selecionar linhas específicas na tabela abaixo clicando nas caixas de seleção. Os totais de Stake, Retorno e Lucro são recalculados dinamicamente para as linhas selecionadas.")

    event = st.dataframe(
        styled_df,
        width="stretch",
        on_select="rerun",
        selection_mode="multi-row"
    )

    # Extract selected rows
    selected_rows = []
    if hasattr(event, "selection") and isinstance(event.selection, dict):
        selected_rows = event.selection.get("rows", [])

    if selected_rows:
        active_list = [display_list[i] for i in selected_rows if i < len(display_list)]
    else:
        active_list = display_list

    # Save active selection to session state for Tab 3 consistency
    st.session_state["analysed_results"] = active_list if active_list else evaluated_markets

    # Totals Summary Bar below the table
    tot_stake = sum(item.get("Stake Recomendada (€)", 0) for item in active_list)
    tot_return = sum(item.get("Retorno (se acertar) (€)", 0) for item in active_list)
    tot_profit = sum(item.get("Lucro Líquido (€)", 0) for item in active_list)

    with st.container(border=True):
        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
        with col_sum1:
            st.metric("Seleção Ativa", f"{len(active_list)} de {len(filtered_list)} linhas")
        with col_sum2:
            st.metric("Total Stake Recomendada", f"{tot_stake:.2f} €")
        with col_sum3:
            st.metric("Total Retorno (se acertar)", f"{tot_return:.2f} €")
        with col_sum4:
            st.metric("Total Lucro Líquido", f"{tot_profit:.2f} €")

    st.markdown("---")

    # Detailed Match Visualizer & 7x7 Poisson Heatmap + H2H Inspector
    st.write("### 🧮 Inspetor de Partida, H2H e Matriz 7x7 de Poisson")

    match_titles = list(matches_meta.keys())
    selected_match_name = st.selectbox("Seleciona uma partida para inspecionar H2H e Matriz de Poisson:", match_titles)

    if selected_match_name and selected_match_name in matches_meta:
        m_info = matches_meta[selected_match_name]
        sel_match = m_info["meta"]

        with st.container(border=True):
            st.markdown(f"#### ⚔️ Desempenho Recente & Confronto Direto (H2H): {selected_match_name}")
            col_f1, col_f2 = st.columns(2)

            with col_f1:
                st.write(f"**Forma {sel_match['HomeTeam']} (Últimos 5 jogos):** `{m_info['home_form']}`")
            with col_f2:
                st.write(f"**Forma {sel_match['AwayTeam']} (Últimos 5 jogos):** `{m_info['away_form']}`")

            st.info(f"**Histórico H2H:** {m_info['h2h_summary']}")

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Exp. Golos Casa", f"{sel_match['ExpGoalsHome']:.2f}")
        with col_m2:
            st.metric("Exp. Golos Fora", f"{sel_match['ExpGoalsAway']:.2f}")
        with col_m3:
            st.metric("Expected Value (+EV Principal)", f"{sel_match['Expected Value (+EV) (%)']:+.2f}%")

        # Radar Chart Comparison
        categories = ['Ataque (xG)', 'Prob. Vitória 1X2', 'Dupla Hipótese', 'Empate Anula (DNB)']
        m_map = sel_match["MarketMap"]

        r_home = [
            min(100.0, sel_match['ExpGoalsHome'] * 35.0),
            m_map.get('Vitória Casa (1)', 40.0),
            m_map.get('Dupla Hipótese (1X)', 60.0),
            m_map.get('Empate Anula Casa (DNB 1)', 50.0)
        ]
        r_away = [
            min(100.0, sel_match['ExpGoalsAway'] * 35.0),
            m_map.get('Vitória Fora (2)', 30.0),
            m_map.get('Dupla Hipótese (X2)', 50.0),
            m_map.get('Empate Anula Fora (DNB 2)', 40.0)
        ]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=r_home, theta=categories, fill='toself', name=sel_match['HomeTeam'], line_color='#10b981'))
        fig_radar.add_trace(go.Scatterpolar(r=r_away, theta=categories, fill='toself', name=sel_match['AwayTeam'], line_color='#ef4444'))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title=f"📊 Gráfico Radar Comparativo: {sel_match['HomeTeam']} vs. {sel_match['AwayTeam']}",
            height=450
        )

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.plotly_chart(fig_radar, width="stretch")

        with col_v2:
            # Plotly Heatmap
            matrix = sel_match["ProbMatrix"] * 100.0  # convert to percentages
            fig = px.imshow(
                matrix,
                labels=dict(x="Golos Equipa Fora", y="Golos Equipa Casa", color="Probabilidade (%)"),
                x=[str(i) for i in range(7)],
                y=[str(i) for i in range(7)],
                color_continuous_scale="Viridis",
                text_auto=".2f"
            )
            fig.update_layout(
                title=f"🎲 Matriz 7x7 Result. Exato: {selected_match_name}",
                height=450
            )
            st.plotly_chart(fig, width="stretch")
