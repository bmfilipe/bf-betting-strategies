# Regras de Negócio - Aba 1: Obter Jogos / Ingestão de Dados (`ui/tab_ingestion.py`)

Este documento especifica o funcionamento, filtros, botões, colunas de tabelas, integrações de API e persistência de dados da página de **Ingestão de Jogos em Tempo Real**.

---

## 1. Visão Geral & Provedor Ativo

- **Função Principal**: Captar jogos de futebol do dia corrente (data do sistema `dd/mm/aaaa`) com odds de mercado completas (1X2, Golos, BTTS).
- **Provedor Ativo**: Definido pela variável de sessão `st.session_state["odds_provider"]` (predefinição: `"The Odds API (the-odds-api.com)"`).
- **Fontes de Dados Disponíveis**:
  1. `The Odds API (the-odds-api.com)`: Usa a chave `odds_api_key` para buscar odds reais em tempo real.
  2. `API-Football (v3 - api-sports.io)`: Usa a chave `api_football_key` para fixtures e odds reais.
  3. `OddsPortal Feed (www.oddsportal.com)`: Extrai cotações dinâmicas via scraper.
  4. `Gemini 2.5 Flash (Google Search Grounding)`: Pesquisa na web via IA Gemini 2.5 Flash usando a chave `gemini_key`.
- **Origem das Odds**: Média de consenso das principais casas reguladas (Betfair Exchange, Pinnacle, Betano, Betclic, 1xBet e OddsPortal).

---

## 2. Filtros de Pesquisa & Parâmetros

### 2.1 Multiselect: `Filtrar por Países / Competições Alvo`
- **Variável**: `selected_countries`
- **Regra de Ordenação**: O primeiro elemento é fixo (`Todas as Ligas/Países`), seguido de todas as competições/países ordenados estritamente por **ordem alfabética**.
- **Opções Disponíveis**:
  - `Todas as Ligas/Países` (Predefinição)
  - `Alemanha (Bundesliga / 2. Bundesliga)`
  - `Argentina (Liga Profesional)`
  - `Áustria (Bundesliga)`
  - `Bélgica (Pro League)`
  - `Brasil (Brasileirão Serie A / Serie B)`
  - `Dinamarca (Superliga)`
  - `Escócia (Premiership)`
  - `Espanha (La Liga / Segunda División)`
  - `EUA / América do Norte (MLS)`
  - `Europa (UEFA Champions / Europa League / Conference League)`
  - `França (Ligue 1 / Ligue 2)`
  - `Inglaterra (Premier League / Championship / League 1)`
  - `Islandia (Primeira Liga / Segunda Liga)`
  - `Itália (Serie A / Serie B)`
  - `Noruega (Eliteserien)`
  - `Países Baixos (Eredivisie)`
  - `Portugal (Primeira Liga / Segunda Liga)`
  - `Suécia (Allsvenskan)`
  - `Suíça (Super League)`
  - `Turquia (Süper Lig)`

*Nota: A opção "Outras Ligas Internacionais" foi removida para evitar duplicação de dados exportados.*

### 2.2 Slider: `Quantidade de Jogos a Mapear`
- **Variável**: `max_matches`
- **Intervalo**: Mínimo `5`, Máximo `50`, Valor por defeito `20`, Passo `5`.

---

## 3. Botões & Ações

### 3.1 Botão `🔎 Pesquisar Jogos via <Provedor>` (Botão Primário)
- **Ação**:
  - Dispara o spinner de carregamento específico do provedor ativo.
  - Executa a função `fetch_today_matches(...)` do serviço correspondente.
  - **Filtro de Estado de Jogos (NEW)**: Considera apenas os jogos que se encontrem **por realizar (agendados)** ou **a decorrer (ao vivo)**. Partidas que tenham terminado (status `FINISHED`, `FT`, `Terminado`) são automaticamente descartadas e não aparecem na lista.
  - Atualiza a sessão com os jogos retornados (`st.session_state["matches_data"] = matches`).
  - Atualiza o log de estado (`st.session_state["last_ingestion_log"] = msg`).
  - **Persistência em Base de Dados**: Se a lista `matches` contiver dados, chama automaticamente `database.db.save_matches_to_db(matches)` para armazenar na tabela SQLite `matches`.
  - Exibe mensagem de feedback (`st.success`, `st.warning` ou `st.error`).

### 3.2 Botão `🗑️ Limpar Dados em Memória`
- **Quadro de Confirmação de Segurança (NEW)**:
  - Ao clicar no botão `🗑️ Limpar Dados em Memória`, o sistema não apaga os dados imediatamente. Em vez disso, ativa uma caixa de confirmação de aviso (`st.warning`) com as opções:
    - `✅ Sim, Limpar Tudo` (botão primário): Reseta `st.session_state["matches_data"] = []`, `st.session_state["analysed_results"] = []` e executa `database.db.clear_db()`, notificando o utilizador e fazendo `st.rerun()`.
    - `❌ Cancelar`: Fecha a caixa de confirmação sem alterar dados e executa `st.rerun()`.

---

## 4. Tabela de Jogos Mapeados (Fragmento `@st.fragment`)

Renderizada quando `st.session_state["matches_data"]` não está vazia.

### 4.1 Controlos Superiores da Tabela
1. **Campo de Pesquisa Rápida (`ingest_search_query`)**:
   - Permite filtrar os jogos em tempo real introduzindo texto.
   - Aplica filtro case-insensitive procurando correspondência parcial nas propriedades: `home`, `away`, `country`, `league`, `market`, `date` e `result`.
2. **Selectbox de Exibição (`ingest_show_option`)**:
   - Opções: `20`, `50`, `100`, `"Tudo"`.
   - Limita a quantidade de linhas apresentadas na tabela.
3. **Métrica `Total Jogos`**:
   - Apresenta o número total de jogos presentes na lista.

### 4.2 Colunas da Tabela
A tabela converte o JSON em `pandas.DataFrame` renomeando os campos conforme a tabela abaixo:

| Campo JSON | Nome da Coluna Exibida | Descrição / Regra |
| :--- | :--- | :--- |
| `date` | `Data Jogo` | Data e hora agendada da partida (ex: `03/08/2026 18:00`) |
| `country` | `País` | País ou continente da partida |
| `league` | `Liga` | Nome da competição |
| `home` | `Equipa Casa` | Nome da equipa mandante |
| `away` | `Equipa Fora` | Nome da equipa visitante |
| `odd_1` | `Odd (1)` | Cotação decimal para Vitória Casa |
| `odd_x` | `Odd (X)` | Cotação decimal para Empate |
| `odd_2` | `Odd (2)` | Cotação decimal para Vitória Fora |
| `odd_o05` | `Odd (+0.5)` | Cotação decimal para Mais de 0.5 Golos |
| `odd_o15` | `Odd (+1.5)` | Cotação decimal para Mais de 1.5 Golos |
| `odd_o25` | `Odd (+2.5)` | Cotação decimal para Mais de 2.5 Golos |
| `odd_btts_yes` | `Odd (BTTS Sim)` | Cotação decimal para Ambas Marcam (Sim) |
| `odd_btts_no` | `Odd (BTTS Não)` | Cotação decimal para Ambas Marcam (Não) |
| `market` | `Mercado Recomendado` | Mercado de maior valor recomendado inicial |
| `result` | `Resultado` | Resultado em tempo real (ex: `"Por iniciar"`, `"1-0 (Ao Vivo)"`) |

### 4.3 Regras de Estilização da Tabela (Pandas Styler)
- **Mercado Recomendado**: Texto em negrito (`font-weight: bold`), cor azul brilhante (`color: #38bdf8`) e fundo azul translúcido (`background-color: rgba(56, 189, 248, 0.15)`).
- **Partidas a Decorrer / Ao Vivo (NEW)**: Se o jogo estiver a decorrer (status `LIVE` ou `result` com indicação de jogo ao vivo), essa linha/célula é destacada numa cor viva diferenciada (fundo âmbar translúcido `rgba(245, 158, 11, 0.2)` e texto a laranja/âmbar `#f59e0b`).

---

## 5. Expander de Edição Manual (JSON)

- Contém uma `st.text_area` com a representação em string JSON dos jogos em memória.
- **Botão `💾 Atualizar Dados da Tabela`**:
  - Tenta converter o texto JSON introduzido (`json.loads`).
  - Se válido, substitui `st.session_state["matches_data"]` e executa `st.rerun()`.
  - Se inválido, exibe mensagem de erro de parse JSON.
