# ⚽ BF Analista de Futebol

> **Sistema Quantitativo de Análise Preditiva (+EV), Matrizes Estatísticas de Poisson & Geração Dinâmica de Boletins de Apostas Desportivas em Tempo Real.**

[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.60.0-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-Proprietary-blue?style=for-the-badge)](LICENSE)

---

## 📌 Visão Geral

O **BF Analista de Futebol** é um ecossistema quantitativo concebido para análise preditiva, identificação de apostas com **Valor Esperado Positivo (+EV)**, dimensionamento ótimo de capital através do **Critério de Kelly Fracionado** e geração automática de boletins de apostas desportivas sem duplicação de eventos.

A aplicação combina ingestão de dados em tempo real através de múltiplos provedores de odds (The Odds API, API-Football v3, OddsPortal e Google Gemini 2.5 Flash), armazenamento relacional local em **SQLite (`database/bfbetting.db`)** e uma interface responsiva construída em **Streamlit**.

---

## 🚀 Principais Funcionalidades

### 1. 🔍 Ingestão & Captação em Tempo Real
- **Múltiplos Provedores de Dados:**
  - **The Odds API:** Odds de consenso global em tempo real (1X2, Over/Under, BTTS).
  - **API-Football (v3 - api-sports.io):** Dados detalhados de ligas mundiais, fixtures, jogos ao vivo e cotações.
  - **OddsPortal Feed:** Extração dinâmica de odds e tendências de mercado.
  - **Gemini 2.5 Flash (Web Grounding):** Pesquisa inteligente de partidas do dia via IA generativa da Google.
- **Filtros por Países e Competições:** Suporte a mais de 20 ligas (Primeira Liga, Premier League, La Liga, Serie A, Bundesliga, Champions League, Brasileirão, etc.).

### 2. 🔴 Jogos ao Vivo em Tempo Real (Live Scores)
- **Acompanhamento In-Play:** Partidas a decorrer no momento com indicação do minuto de jogo, resultado atual e odds ao vivo.
- **Leitura & Gravação em SQLite:** Gravação e consulta instantânea de partidas na tabela `live_matches` da base de dados local.
- **Cronologia de Eventos & xG Ao Vivo:** Leitura de golos, cartões e expectativa de golos acumulada no decorrer da partida.

### 3. ⚔️ Comparador de Equipas & Confronto Direto (H2H WebScraping)
- **Motor de Web Scraping:** Análise comparativa entre duas equipas (Equipa A vs Equipa B) com extração de histórico recente e métricas de desempenho.
- **Estatísticas Comparativas:** Guia de forma (últimos 5 jogos), média de golos marcados/sofridos, xG esperado, Clean Sheets %, Over 2.5 % e BTTS %.
- **Gráficos Interativos (Plotly):** Comparação visual de ataque vs defesa e gráfico circular de histórico H2H.
- **Matriz de Poisson H2H:** Simulação probabilística entre as duas equipas analisadas.

### 4. 📊 Motor Quantitativo de Poisson & +EV
- **Matriz de Poisson 7x7:** Cálculo da distribuição de probabilidades de golos com base nas métricas de golos esperados a favor ($xG$) e contra ($xGA$).
- **Apuramento de Valor Esperado (+EV):** Identificação matemática de oportunidades onde a probabilidade estimativa do modelo supera a probabilidade implícita oferecida pelas casas de apostas:
  $$\text{EV (\%)} = (\text{Prob. Estimada} \times \text{Odd}) - 1$$
- **Dimensionamento de Banca por Critério de Kelly (1/4 Kelly):** Recomendação de stake ótima para mitigar a volatilidade e proteger a banca contra séries negativas.

### 5. 🎫 Gerador Combinatório de Boletins & Exportação Multi-Formato
- **Algoritmo Anti-Duplicação:** Agrupamento inteligente de apostas sem sobreposição de partidas no mesmo boletim.
- **Estratégias Configuráveis:** Perfis Conservador (+EV de alta probabilidade), Equilibrado e Agressivo.
- **Exportação Multiformato:** PDF Profissional (FPDF2), TXT e tabelas CSV.

### 6. 🏛️ Base de Dados Relacional SQLite (`database/bfbetting.db`) & Gestão Admin
- Armazenamento relacional completo (`matches`, `evaluations`, `bet_slips`, `live_matches`, `team_h2h_history`, `team_stats_cache`, `app_settings`, `ingestion_logs`).
- **Separador Base de Dados no Administrador:**
  - Estatísticas e saúde de cada tabela em tempo real.
  - Limpeza total ou de tabelas específicas.
  - Download e upload do ficheiro `bfbetting.db` para backup e reposição.
  - Exportação de dados de qualquer tabela para formatos `.csv` ou `.json`.

### 7. 🎨 Interface Responsiva & Seletor Dark / Light
- **Navegação por Barra Lateral Esquerda:** Acesso rápido às 5 páginas principais e ao Painel de Administrador.
- **Alternador de Tema no Topo:** Suporte a **Modo Escuro (Dark)** e **Modo Claro (Light)** com transições de fundo suaves e contraste de 100% em botões e fontes.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Função no Projeto |
| :--- | :--- |
| **Python 3.14+** | Linguagem principal de desenvolvimento backend e estatística. |
| **Streamlit 1.60.0** | Framework web interativo para renderização da UI. |
| **SQLite 3** | Base de Dados relacional embutida (`database/bfbetting.db`). |
| **Plotly Express** | Visualização de gráficos interativos de comparação H2H e estatísticas. |
| **Google Gemini 2.5 Flash** | Inteligência Artificial generativa para busca e estruturação de jogos. |
| **The Odds API & API-Football** | APIs REST para captação de odds e fixtures ao vivo. |
| **Pandas & NumPy** | Manipulação, filtragem e agregação de dados matriciais. |
| **SciPy (Poisson)** | Cálculo estatístico da distribuição de probabilidade de golos. |
| **FPDF2** | Geração dinâmica de boletins e relatórios em PDF. |

---

## 💻 Instalação & Execução Local

### Passo a Passo

1. **Clonar o Repositório:**
   ```bash
   git clone https://github.com/bmfilipe/bf-betting-strategies.git
   cd bf-betting-strategies
   ```

2. **Criar e Ativar Ambiente Virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Iniciar a Aplicação:**
   ```bash
   python run.py
   ```
   *A aplicação iniciará automaticamente no navegador em `http://localhost:8501`.*

---

## 📁 Estrutura do Projeto

```text
bf-betting-strategies/
<<<<<<< HEAD
├── .agents/                    # Skills e diretivas de desenvolvimento Streamlit
│   └── rules/                  # Regras detalhadas por página (filtros, botões, base de dados e matemática)
│       ├── 01_landing_and_nav_rules.md
│       ├── 02_ingestion_page_rules.md
│       ├── 03_analysis_page_rules.md
│       ├── 04_slips_page_rules.md
│       ├── 05_admin_page_rules.md
│       └── 06_database_and_math_rules.md
├── app.py                      # Ponto de entrada da aplicação Streamlit
=======
├── .agents/                    # Skills e diretivas de desenvolvimento Streamlit e arquitetura
├── .streamlit/                 # Definições de tema e segredos local (config.toml, secrets.toml)
├── database/                   # Módulo e armazenamento SQLite
│   ├── bfbetting.db            # Ficheiro de base de dados relacional
│   └── db.py                   # Gestor SQL (tabelas, índices, exportação CSV/JSON)
├── models/                     # Motores estatísticos (poisson.py, etc.)
├── services/                   # Integrações externas e scraping
│   ├── api_football_ingestion.py
│   ├── live_matches_service.py # Ingestão e monitorização de Jogos ao Vivo
│   ├── h2h_scraper.py          # Motor de Web Scraping de Confronto Direto H2H
│   ├── gemini_ingestion.py
│   ├── odds_api_ingestion.py
│   ├── oddsportal_ingestion.py
│   ├── exporter.py
│   └── colab_generator.py
├── ui/                         # Componentes e páginas da interface web
│   ├── styles.py               # CSS customizado e alternador Dark/Light
│   ├── tab_ingestion.py        # Página 1: Captação de jogos pré-jogo
│   ├── tab_live.py             # Página 2: Jogos ao vivo em tempo real
│   ├── tab_h2h.py              # Página 3: Comparador de Equipas H2H
│   ├── tab_analysis.py         # Página 4: Análise quantitativa Poisson & +EV
│   ├── tab_slips.py            # Página 5: Gerador de boletins e exportações
│   └── tab_admin.py            # Painel Admin (Vault, BD SQLite, Backup JSON, Colab, Sobre)
├── app.py                      # Ponto de entrada da aplicação Streamlit com navegação
>>>>>>> bcd5ae0ad2a3dcc5840cd7d5d3acfe89ef908fe4
├── config.py                   # Inicialização de estado e segredos
├── requirements.txt            # Lista de dependências Python
├── run.py                      # Script de arranque local com túnel Ngrok
├── versions.txt                # Histórico oficial de alterações (Changelog)
└── README.md                   # Documentação oficial do projeto
```

---

## 📜 Licença & Termos

Este projeto é de uso privado e proprietário. Todos os direitos reservadas.

*Aviso: As análises estatísticas fornecidas pelo sistema têm fins puramente informativos e probabilísticos. Aposte com responsabilidade.*
