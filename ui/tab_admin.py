import streamlit as st
from config import ADMIN_PASSWORD_HASH
from services import ColabNotebookGenerator

def render_tab_admin():
    """Render Tab 4: Área Restrita do Administrador & Vault de Chaves & Gerador Colab."""
    st.subheader("🔑 Painel de Autenticação & Configurações de Administrador")

    if not st.session_state.get("is_admin", False):
        st.info("Esta área é restrita a administradores do sistema. Introduz a palavra-passe mestre para aceder.")

        with st.form("admin_login_form"):
            admin_pass_input = st.text_input("Palavra-passe de Administrador", type="password", placeholder="Insere a chave mestre...")
            submit_login = st.form_submit_button("🔓 Entrar no Painel Restrito", type="primary")

            if submit_login:
                if admin_pass_input == ADMIN_PASSWORD_HASH:
                    st.session_state["is_admin"] = True
                    st.success("Autenticação efetuada com sucesso!")
                    st.rerun()
                else:
                    st.error("Palavra-passe incorreta. Acesso negado.")
    else:
        st.success("🟢 Sessão de Administrador Ativa (RBAC Autenticado)")

        col_logout, _ = st.columns([1, 4])
        with col_logout:
            if st.button("🔒 Encerrar Sessão"):
                st.session_state["is_admin"] = False
                st.rerun()

        st.markdown("---")

        # Colab Notebook Generator Box
        with st.container(border=True):
            st.markdown("### ⚡ Exportação para Google Colab (.ipynb)")
            st.write("Gera o notebook Jupyter `.ipynb` pronto a ser executado diretamente no Google Colab com toda a estrutura de código, dependências e túnel Ngrok.")

            try:
                colab_json = ColabNotebookGenerator.generate_ipynb_notebook()
                st.download_button(
                    label="🚀 Descarregar Notebook Google Colab (.ipynb)",
                    data=colab_json,
                    file_name="BF_Analista_Futebol_Colab.ipynb",
                    mime="application/x-ipynb+json",
                    type="primary",
                    width="stretch"
                )
            except Exception as e:
                st.error(f"Erro ao gerar notebook Colab: {str(e)}")

        st.markdown("---")

        # Settings Form
        st.subheader("⚙️ Configurações das Chaves de API & Integrações")

        with st.form("admin_settings_form"):
            provider_options = [
                "The Odds API (the-odds-api.com)",
                "API-Football (v3 - api-sports.io)",
                "OddsPortal Feed (www.oddsportal.com)",
                "Gemini 2.5 Flash (Google Search Grounding)"
            ]
            current_provider = st.session_state.get("odds_provider", provider_options[0])
            provider_index = provider_options.index(current_provider) if current_provider in provider_options else 0

            new_odds_provider = st.selectbox(
                "🎯 Provedor Ativo para Captação de Odds & Jogos (Combolist):",
                options=provider_options,
                index=provider_index,
                help="Seleciona a API pretendida para captação das odds e partidas em tempo real."
            )

            new_odds_key = st.text_input(
                "The Odds API Key (www.the-odds-api.com)",
                value=st.session_state.get("odds_api_key", ""),
                type="password",
                help="Chave de API do serviço The Odds API para cotações realistas em tempo real."
            )

            new_api_football_key = st.text_input(
                "API-Football Key (v3 - api-sports.io / RapidAPI)",
                value=st.session_state.get("api_football_key", ""),
                type="password",
                help="Chave de API da API-Football para fixtures, odds e métricas em tempo real."
            )

            new_gemini = st.text_input("Gemini API Key (Modelo gemini-2.5-flash)", value=st.session_state.get("gemini_key", ""), type="password")
            new_ngrok = st.text_input("Ngrok Auth Token (Acesso Externo Público)", value=st.session_state.get("ngrok_key", ""), type="password")

            st.markdown("---")
            st.subheader("📧 Configurações SMTP (Envio de E-mails)")
            new_sender = st.text_input("E-mail Remetente (Gmail)", value=st.session_state.get("email_sender", ""), placeholder="exemplo@gmail.com")
            new_pass = st.text_input("Palavra-passe de Aplicação SMTP", value=st.session_state.get("email_password", ""), type="password")

            save_submit = st.form_submit_button("💾 Guardar Definições no Vault", type="primary")

            if save_submit:
                st.session_state["odds_provider"] = new_odds_provider
                st.session_state["odds_api_key"] = new_odds_key.strip()
                st.session_state["api_football_key"] = new_api_football_key.strip()
                st.session_state["gemini_key"] = new_gemini.strip()
                st.session_state["ngrok_key"] = new_ngrok.strip()
                st.session_state["email_sender"] = new_sender.strip()
                st.session_state["email_password"] = new_pass.strip()

                try:
                    from database.db import save_setting
                    save_setting("odds_provider", new_odds_provider, "SETTINGS")
                    save_setting("odds_api_key", new_odds_key.strip(), "VAULT")
                    save_setting("api_football_key", new_api_football_key.strip(), "VAULT")
                    save_setting("gemini_key", new_gemini.strip(), "VAULT")
                    save_setting("ngrok_key", new_ngrok.strip(), "VAULT")
                    save_setting("email_sender", new_sender.strip(), "SETTINGS")
                except Exception:
                    pass

                if new_ngrok.strip():
                    try:
                        import os
                        token_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".ngrok_token")
                        with open(token_path, "w", encoding="utf-8") as f:
                            f.write(new_ngrok.strip())
                    except Exception:
                        pass

                st.success(f"Configurações atualizadas com sucesso! Provedor ativo: {new_odds_provider}")

        # JSON Backup Export and Import Box
        st.markdown("---")
        with st.container(border=True):
            st.markdown("### 📦 Backup & Repositório de Configurações (JSON)")
            st.write("Exporta todas as chaves e parâmetros do aplicativo num único ficheiro `.json`, ou importa uma configuração prévia para restaurar o sistema.")

            col_exp, col_imp = st.columns(2)

            with col_exp:
                st.markdown("#### 📥 Exportar Configurações")
                try:
                    import datetime
                    from database.db import export_settings_json
                    json_export_data = export_settings_json()
                    st.download_button(
                        label="💾 Descarregar Backup JSON (bfbetting_config.json)",
                        data=json_export_data,
                        file_name=f"bfbetting_config_{datetime.date.today().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        type="primary",
                        width="stretch"
                    )
                except Exception as json_err:
                    st.error(f"Erro ao gerar exportação JSON: {json_err}")

            with col_imp:
                st.markdown("#### 📤 Importar Configurações")
                uploaded_json = st.file_uploader("Carregar ficheiro .json de configuração:", type=["json"], key="json_config_uploader")
                if uploaded_json is not None:
                    if st.button("⚡ Aplicar Configurações do Ficheiro", type="primary", width="stretch"):
                        try:
                            from database.db import import_settings_json, load_settings
                            json_content = uploaded_json.read().decode("utf-8")
                            success, msg = import_settings_json(json_content)
                            if success:
                                new_settings = load_settings()
                                for k, v in new_settings.items():
                                    st.session_state[k] = v
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        except Exception as imp_err:
                            st.error(f"Erro ao processar ficheiro: {imp_err}")
