# Regras de Negócio - Landing Page & Navegação Principal

Este documento descreve o funcionamento, regras de estado, temas visuais, layout e navegação da **Landing Page (Página Inicial)** e da **Barra de Navegação Superior** do **BF Analista de Futebol**.

---

## 1. Estado da Aplicação & Landing Page (`app.py`)

### 1.1 Controlo de Estado Inicial (`app_started`)
- **Variável de Sessão**: `st.session_state["app_started"]` (booleano, predefinição: `False`).
- **Comportamento**:
  - Se `app_started == False`: É renderizada a **Landing Page (Página Inicial)**.
  - Se `app_started == True`: É renderizado o **Dashboard Principal** da aplicação.

### 1.2 Alternador de Tema Visual (`theme_mode`)
- **Variável de Sessão**: `st.session_state["theme_mode"]` (string, valores: `"dark"` ou `"light"`, predefinição: `"dark"`).
- **Elemento UI**: Botão no topo direito (`☀️ Claro` se dark / `🌙 Escuro` se light).
- **Regra de Ação**:
  - Ao clicar, inverte a variável `theme_mode` e executa `st.rerun()`.
  - **Paleta Modo Claro (Light)**:
    - Fundo Hero Banner: `linear-gradient(135deg, #e2e8f0 0%, #ffffff 100%)`
    - Cor do Título: `#0284c7`
    - Cor do Texto: `#334155`
    - Borda: `1px solid #cbd5e1`
    - Sombra: `0 10px 30px rgba(0, 0, 0, 0.08)`
  - **Paleta Modo Escuro (Dark)**:
    - Fundo Hero Banner: `linear-gradient(135deg, #0f172a 0%, #1e293b 100%)`
    - Cor do Título: `#38bdf8`
    - Cor do Texto: `#94a3b8`
    - Borda: `1px solid #334155`
    - Sombra: `0 10px 30px rgba(0, 0, 0, 0.5)`

### 1.3 Hero Banner & Cards de Destaque
- **Hero Title**: "BF Analista de Futebol" com subtítulo explicativo da arquitetura quantitativa.
- **Grid de 4 Colunas (Cards de Funcionalidades)**:
  1. `🔍 Tempo Real`: Explicação da captação via The Odds API e Gemini 2.5 Flash.
  2. `📊 Poisson 7x7`: Explicação do modelo estatístico e apuramento de $+EV$.
  3. `💰 Gestão Kelly`: Dimensionamento de stake via fração de Kelly (1/4 Kelly).
  4. `🎫 Boletins +EV`: Geração combinatória e exportação em PDF, TXT e CSV.
- **Botão Principal de Ação**:
  - `🚀 Iniciar Aplicação`: Define `st.session_state["app_started"] = True` e `st.session_state["confirm_exit"] = False`, executando `st.rerun()` para carregar o Dashboard.

---

## 2. Dashboard Principal & Barra de Navegação Superior

### 2.1 Cabeçalho Superior do Dashboard
Renderizado quando `app_started == True`.
- **Logótipo & Título**: Exibe o logótipo ⚽ e descrição sucinta do sistema.
- **Botão Alternador de Tema**: Altera o tema `light` / `dark` a qualquer momento.
- **Botão `🔒 Área de Administrador`**:
  - Define `st.session_state["active_tab"] = "🔒 Área de Administrador"`.
  - Executa `st.rerun()` para mudar a visão para o painel de administração restrito.
- **Botão `🚪 Sair da Aplicação`**:
  - Define `st.session_state["confirm_exit"] = True`.
  - Exibe um container de aviso com confirmação:
    - `✅ Sim, Sair` (botão primário): Reseta `app_started = False` e `confirm_exit = False`, retornando à Landing Page.
    - `❌ Cancelar`: Define `confirm_exit = False` e fecha o aviso.

### 2.2 Estrutura das Abas Principais (`st.tabs`)
O aplicativo principal divide-se em 3 abas principais navegáveis:
1. `🔍 Obter Jogos (Odds API / OddsPortal / Gemini)` -> Chama `render_tab_ingestion()`
2. `📊 Análise & Probabilidades (+EV)` -> Chama `render_tab_analysis()`
3. `🎫 Gerador de Boletins & Exportação` -> Chama `render_tab_slips()`

Quando o utilizador acede à Área de Administrador, a vista das abas é temporariamente substituída pelo painel `render_tab_admin()`, fornecendo o botão `⬅️ Voltar ao Dashboard` para retornar à navegação normal.
