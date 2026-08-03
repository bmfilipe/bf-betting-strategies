# Regras de Negócio - Área de Administrador & Vault (`ui/tab_admin.py`)

Este documento especifica as regras de autenticação RBAC, gestão do Vault de chaves de API, backup/restauração em JSON, gerador de notebooks Google Colab e o leitor de versões da **Área Restrita do Administrador**.

---

## 1. Autenticação & Controlo de Acesso (RBAC)

- **Variável de Sessão**: `st.session_state["is_admin"]` (booleano, predefinição: `False`).
- **Palavra-Passe Mestre**: `ADMIN_PASSWORD_HASH = "Admin#1976"` (definida em `config.py`).
- **Fluxo de Login**:
  - Se `is_admin == False`: Exibe formulário com campo de texto do tipo `password` (`admin_pass_input`) e botão `🔓 Entrar no Painel Restrito`.
  - Se a palavra-passe coincidir com `ADMIN_PASSWORD_HASH`: Define `is_admin = True`, exibe mensagem de sucesso e executa `st.rerun()`.
  - Se incorreta: Exibe mensagem de erro de acesso negado.
- **Encerramento de Sessão**:
  - Quando autenticado, o cabeçalho apresenta o botão `🔒 Encerrar Sessão`, que define `is_admin = False` e recarrega a página.

---

## 2. Sub-Abas do Painel de Administração

### 2.1 Sub-Aba 1: `⚙️ Vault & Chaves de API`
Permite definir e atualizar as credenciais e o provedor ativo do sistema.

#### Campos de Configuração:
1. `Provedor Ativo para Captação de Odds & Jogos` (`new_odds_provider`):
   - Opções: `The Odds API (the-odds-api.com)`, `API-Football (v3 - api-sports.io)`, `OddsPortal Feed (www.oddsportal.com)`, `Gemini 2.5 Flash (Google Search Grounding)`.
2. `The Odds API Key` (`new_odds_key`): Chave do serviço The Odds API.
3. `API-Football Key` (`new_api_football_key`): Chave da API-Football (api-sports.io / RapidAPI).
4. `Gemini API Key` (`new_gemini`): Chave Google Gemini (modelo `gemini-2.5-flash`).
5. `Ngrok Auth Token` (`new_ngrok`): Token de autenticação Ngrok para criação de túnel HTTP público.
6. `E-mail Remetente (Gmail)` (`new_sender`): Endereço remetente para notificações SMTP.
7. `Palavra-passe de Aplicação SMTP` (`new_pass`): Palavra-passe de aplicação do Gmail/SMTP.

#### Ação do Botão `💾 Guardar Definições no Vault`:
- Atualiza as respetivas chaves em `st.session_state`.
- Persiste as definições na tabela SQLite `app_settings` via `database.db.save_setting(...)`.
- Se `new_ngrok` contiver um token, escreve o valor no ficheiro local `.ngrok_token`.

---

### 2.2 Sub-Aba 2: `📦 Backup & Importação (JSON)`

#### Exportação:
- Botão `💾 Descarregar Backup JSON (bfbetting_config.json)`:
  - Invoca `database.db.export_settings_json()`, gerando um payload JSON estruturado com a versão do sistema, data de exportação e o dicionário completo de definições.

#### Importação:
- File Uploader: Permite carregar um ficheiro `.json`.
- Botão `⚡ Aplicar Configurações do Ficheiro`:
  - Lê o conteúdo JSON e invoca `database.db.import_settings_json(json_content)`.
  - Atualiza as definições na SQLite e recarrega `st.session_state` executando `st.rerun()`.

---

### 2.3 Sub-Aba 3: `⚡ Google Colab (.ipynb)`

- Botão `🚀 Descarregar Notebook Google Colab (.ipynb)`:
  - Invoca `services.colab_generator.ColabNotebookGenerator.generate_ipynb_notebook()`.
  - Gera um ficheiro de notebook Jupyter `.ipynb` pronto a ser executado na nuvem do Google Colab com os seguintes blocos automatizados:
    1. Instalação de dependências (`streamlit`, `pyngrok`, `pandas`, `fpdf2`, `plotly`, `google-genai`).
    2. Clonagem do repositório ou criação de ficheiros da app.
    3. Inicialização do túnel Ngrok para disponibilizar um URL público de acesso.
    4. Execução do servidor Streamlit.

---

### 2.4 Sub-Aba 4: `ℹ️ Sobre o Aplicativo`

- **Informações do Sistema**: Exibe a versão atual (`v2.5.0`), framework (Python 3.14 + Streamlit 1.60.0), base de dados (`bfbetting.db`) e tecnologias integradas.
- **Histórico de Alterações (Changelog)**: Leitor automático do ficheiro `versions.txt` localizado na raiz do projeto, exibido num bloco formatado de código (`st.code`).
