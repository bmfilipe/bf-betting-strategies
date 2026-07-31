import streamlit as st
import random
from services.exporter import ReportExporter
from services.email_service import EmailService

def render_tab_slips():
    """Render Tab 3: Gerador de Boletins Combinatórios por Estratégia sem Duplicados."""
    st.subheader("🎫 Algoritmo Combinatório de Boletins por Estratégia de Mercado")
    st.write("Gera boletins múltiplos customizados garantindo que **cada boletim contém partidas estritamente distintas (zero jogos repetidos no mesmo bilhete)**.")

    analysed_results = st.session_state.get("analysed_results", [])
    if not analysed_results:
        st.info("Ainda não foram processadas análises estatísticas. Por favor, acede à aba 'Análise & Probabilidades'.")
        return

    # Configuration controls
    with st.container(border=True):
        st.markdown("#### ⚙️ Configurações & Modo de Estratégia dos Boletins")
        col_cfg1, col_cfg2, col_cfg3, col_cfg4 = st.columns(4)

        with col_cfg1:
            n_games = st.selectbox("Jogos por Boletim (Múltipla):", options=[2, 3, 4, 5], index=1)

        with col_cfg2:
            num_boletins = st.slider("Quantidade de Boletins a Gerar:", min_value=1, max_value=10, value=5)

        with col_cfg3:
            global_stake = st.number_input("Stake Padrão (€) por Boletim:", value=10.0, step=1.0, min_value=1.0)

            # Synchronize individual slip stakes dynamically whenever global_stake changes
            if st.session_state.get("prev_global_stake") != global_stake:
                st.session_state["prev_global_stake"] = global_stake
                for i in range(15):
                    st.session_state[f"stake_{i}"] = float(global_stake)

        with col_cfg4:
            strategy_options = [
                "⚽ Resultado Final (1X2)",
                "🛡️ Dupla Hipótese (1X / X2)",
                "🔥 Ambas Marcam (BTTS)",
                "⚡ Total +0.5 Golos",
                "🎯 Total +1.5 Golos",
                "🚀 Total +2.5 Golos",
                "⚽ Total +3.5 Golos",
                "🥅 Empate Anula (DNB)",
                "🛡️ Handicap Asiático (AH)"
            ]
            selected_strategies = st.multiselect(
                "Estratégia(s) dos Boletins:",
                options=strategy_options,
                default=strategy_options
            )

    # Filter pool by selected strategies
    if not selected_strategies:
        st.warning("⚠️ Por favor, seleciona pelo menos uma estratégia no filtro acima para gerar boletins.")
        return

    pool = []
    for item in analysed_results:
        grp = item.get("EstratégiaGrupo", "")
        merc = item.get("Mercado", "")

        is_match = False
        if "⚽ Resultado Final (1X2)" in selected_strategies and (grp == "Resultado Final (1X2)" or "Vitória" in merc or "Empate" in merc):
            is_match = True
        elif "🛡️ Dupla Hipótese (1X / X2)" in selected_strategies and (grp == "Dupla Hipótese" or "Dupla Hipótese" in merc):
            is_match = True
        elif "🔥 Ambas Marcam (BTTS)" in selected_strategies and (grp == "Ambas Marcam" or "Ambas Marcam" in merc):
            is_match = True
        elif "⚡ Total +0.5 Golos" in selected_strategies and "+0.5" in merc:
            is_match = True
        elif "🎯 Total +1.5 Golos" in selected_strategies and "+1.5" in merc:
            is_match = True
        elif "🚀 Total +2.5 Golos" in selected_strategies and "+2.5" in merc:
            is_match = True
        elif "⚽ Total +3.5 Golos" in selected_strategies and "+3.5" in merc:
            is_match = True
        elif "🥅 Empate Anula (DNB)" in selected_strategies and (grp == "Empate Anula" or "Empate Anula" in merc):
            is_match = True
        elif "🛡️ Handicap Asiático (AH)" in selected_strategies and (grp == "Handicap Asiático" or "AH" in merc or "Handicap" in merc):
            is_match = True

        if is_match:
            pool.append(item)

    if not pool:
        st.warning("Não foram encontradas apostas correspondentes às estratégias selecionadas. A utilizar a seleção geral.")
        pool = analysed_results

    # Group items by distinct match title to guarantee NO repeating games in a single slip
    match_dict = {}
    for item in pool:
        m_title = item['Jogo']
        if m_title not in match_dict:
            match_dict[m_title] = []
        match_dict[m_title].append(item)

    unique_match_titles = list(match_dict.keys())
    total_unique_matches = len(unique_match_titles)

    if total_unique_matches < n_games:
        st.error(f"⚠️ Atenção: Apenas existem {total_unique_matches} partidas distintas para a estratégia selecionada, mas definiste {n_games} jogos por boletim. Reduz o número de jogos por boletim ou adiciona mais partidas na Aba 1.")
        return

    strat_names = ", ".join(selected_strategies)
    st.info(f"📍 **Estratégias Ativas ({len(selected_strategies)}):** {strat_names} | **{total_unique_matches} partidas distintas** disponíveis (zero jogos repetidos por bilhete).")
    st.markdown("---")

    boletins_generated = []

    for b_idx in range(num_boletins):
        st.markdown(f"#### 🎫 Boletim #{b_idx + 1}")

        # Deterministic rotation of distinct matches per slip
        start_idx = (b_idx * n_games) % total_unique_matches
        selected_titles = [unique_match_titles[(start_idx + i) % total_unique_matches] for i in range(n_games)]

        col_b1, col_b2 = st.columns([3, 1])

        with col_b1:
            jogos_detalhe = []
            odd_total = 1.0
            for title in selected_titles:
                available_items = match_dict[title]
                # Pick best EV item for this match in the strategy pool
                item = sorted(available_items, key=lambda x: x["Expected Value (+EV) (%)"], reverse=True)[0]
                odd_total *= item["Odd"]
                detalhe_str = f"[{item['País']} - {item['Liga']}] {item['Jogo']} | Mercado: **{item['Mercado']}** (Odd: {item['Odd']:.2f} | +EV: {item['Expected Value (+EV) (%)']:+.1f}%)"
                jogos_detalhe.append(detalhe_str)
                st.markdown(f"- {detalhe_str}")

        with col_b2:
            key_stake = f"stake_{b_idx}"
            if key_stake not in st.session_state:
                st.session_state[key_stake] = float(global_stake)
            stake_b = st.number_input(f"Stake Boletim #{b_idx + 1} (€)", min_value=0.1, step=1.0, key=key_stake)
            odd_total = round(odd_total, 2)
            retorno = round(odd_total * stake_b, 2)
            st.metric(label="Odd Total", value=f"{odd_total:.2f}")
            st.metric(label="Ganho Potencial", value=f"{retorno:.2f} €")

        boletins_generated.append({
            "boletim_id": b_idx + 1,
            "jogos_detalhe": jogos_detalhe,
            "odd_total": odd_total,
            "stake": stake_b,
            "retorno": retorno
        })
        st.markdown("---")

    # Summary Totals
    total_investment = sum(b["stake"] for b in boletins_generated)
    total_return_potential = sum(b["retorno"] for b in boletins_generated)

    col_tot1, col_tot2, col_tot3 = st.columns(3)
    with col_tot1:
        st.metric("Total de Boletins", f"{len(boletins_generated)}")
    with col_tot2:
        st.metric("Investimento Total (Stake)", f"{total_investment:.2f} €")
    with col_tot3:
        st.metric("Retorno Potencial Acumulado", f"{total_return_potential:.2f} €")

    st.markdown("---")
    st.subheader("📤 Exportação & Notificação de Boletins (TXT / PDF / CSV / E-mail)")

    txt_report = ReportExporter.generate_txt_report(boletins_generated)
    csv_report = ReportExporter.generate_csv_report(boletins_generated)

    col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)

    with col_exp1:
        st.download_button(
            label="📄 Relatório .TXT",
            data=txt_report,
            file_name="boletins_bf_analista.txt",
            mime="text/plain",
            width="stretch"
        )

    with col_exp2:
        try:
            pdf_bytes = ReportExporter.generate_pdf_report(boletins_generated)
            st.download_button(
                label="📕 Relatório .PDF",
                data=pdf_bytes,
                file_name="boletins_bf_analista.pdf",
                mime="application/pdf",
                width="stretch"
            )
        except Exception as e:
            st.error(f"Erro PDF: {str(e)}")

    with col_exp3:
        st.download_button(
            label="📊 Tabela .CSV (Excel)",
            data=csv_report,
            file_name="boletins_bf_analista.csv",
            mime="text/csv",
            width="stretch"
        )

    with col_exp4:
        dest_email = st.text_input("E-mail Destinatário", placeholder="exemplo@gmail.com")
        if st.button("📧 Enviar por E-mail", type="primary", width="stretch"):
            if dest_email:
                try:
                    pdf_b = ReportExporter.generate_pdf_report(boletins_generated)
                    success, msg = EmailService.send_report_email(
                        sender_email=st.session_state.get("email_sender", ""),
                        sender_password=st.session_state.get("email_password", ""),
                        recipient_email=dest_email,
                        subject="Boletins BF Analista de Futebol +EV",
                        body_text=txt_report,
                        pdf_bytes=pdf_b,
                        txt_content=txt_report
                    )
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                except Exception as ex:
                    st.error(f"Erro no envio: {str(ex)}")
            else:
                st.warning("Introduz um e-mail válido.")
