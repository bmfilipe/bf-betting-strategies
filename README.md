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
  - **API-Football (v3 - api-sports.io):** Dados detalhados de ligas mundiais, fixtures e cotações.
  - **OddsPortal Feed:** Extração dinâmica de odds e tendências de mercado.
  - **Gemini 2.5 Flash (Web Grounding):** Pesquisa inteligente de partidas do dia via IA generativa da Google.
- **Filtros por Países e Competições:** Suporte a mais de 20 ligas (Primeira Liga, Premier League, La Liga, Serie A, Bundesliga, Champions League, Brasileirão, etc.).

### 2. 📊 Motor Quantitativo de Poisson & +EV
- **Matriz de Poisson 7x7:** Cálculo da distribuição de probabilidades de golos com base nas métricas de golos esperados a favor ($xG$) e contra ($xGA$).
- **Apuramento de Valor Esperado (+EV):** Identificação matemática de oportunidades onde a probabilidade estimativa do modelo supera a probabilidade implícita oferecida pelas casas de apostas:
  $$\text{EV (\%)} = (\text{Prob. Estimada} \times \text{Odd}) - 1$$
- **Dimensionamento de Banca por Critério de Kelly (1/4 Kelly):** Recomendação de stake ótima para mitigar a volatilidade e proteger a banca contra séries negativas.

### 3. 🎫 Gerador Combinatório de Boletins & Exportação Multi-Formato
- **Algoritmo Anti-Duplicação:** Agrupamento inteligente de apostas sem sobreposição de partidas no mesmo boletim.
- **Estratégias Configuráveis:** Perfis Conservador (+EV de alta probabilidade), Equilibrado e Agressivo.
- **Exportação Multiformato:**
  - **PDF Profissional (FPDF2):** Relatórios formatados e prontos para impressão.
  - **Ficheiros de Texto (TXT):** Resumos rápidos de boletins.
  - **Tabelas CSV:** Dados brutos para integração com Excel ou software de gestão de banca.

### 4. 🏛️ Base de Dados Relacional SQLite (`database/bfbetting.db`)
- Armazenamento em tabelas relacionais indexadas (`matches`, `evaluations`, `bet_slips`, `app_settings`, `ingestion_logs`).
- **Persistência Total:** Os dados pesquisados e analisados não se perdem ao fechar o navegador ou reiniciar a aplicação.
- **Auto-Migração:** Deteção automática e atualização de colunas na base de dados SQLite.

### 5. 🔑 Painel de Administração & Backup JSON
- **Área Restrita (RBAC):** Protegida por palavra-passe mestre.
- **Vault de Chaves de API:** Gestão centralizada e segura das chaves de API e definições SMTP.
- **Backup & Restore em JSON:** Exportação integral das configurações em `bfbetting_config.json` e restauro rápido por upload.
- **Gerador Google Colab (.ipynb):** Exportação de notebooks Jupyter pré-configurados com túnel Ngrok.
- **Separador "Sobre":** Apresentação das tecnologias e leitura dinâmica do ficheiro `versions.txt`.

### 6. 🎨 Interface Responsiva & Seletor Dark / Light
- **Alternador de Tema no Topo:** Suporte a **Modo Escuro (Dark)** e **Modo Claro (Light)** com transições de fundo suaves e contraste de 100% em botões e fontes.
- **Desempenho Otimizado:** Uso de decoradores `@st.fragment` para pesquisas e filtragens na tabela sem recarregamentos globais da página.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Função no Projeto |
| :--- | :--- |
| **Python 3.14+** | Linguagem principal de desenvolvimento backend e estatística. |
| **Streamlit 1.60.0** | Framework web interativo para renderização da UI. |
| **SQLite 3** | Base de Dados relacional embutida (`database/bfbetting.db`). |
| **Google Gemini 2.5 Flash** | Inteligência Artificial generativa para busca e estruturação de jogos. |
| **The Odds API & API-Football** | APIs REST para captação de odds e fixtures desportivas. |
| **Pandas & NumPy** | Manipulação, filtragem e agregação de dados matriciais. |
| **SciPy (Poisson)** | Cálculo estatístico da distribuição de probabilidade de golos. |
| **FPDF2** | Geração dinâmica de boletins e relatórios em PDF. |
| **Pyngrok** | Criação de túneis seguros para acesso remoto em execuções locais. |

---

## 💻 Instalação & Execução Local

### Pré-requisitos
- Python 3.10 ou superior instalado na máquina.
- Git para clonar o repositório.

### Passo a Passo

1. **Clonar o Repositório:**
   ```bash
   git clone https://github.com/bmfilipe/bf-betting-strategies.git
   cd bf-betting-strategies
   ```

2. **Criar e Ativar Ambiente Virtual:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar Chaves de API (Opcional):**
   Crie o ficheiro `.streamlit/secrets.toml` com a seguinte estrutura:
   ```toml
   GEMINI_API_KEY = "SUA_CHAVE_GEMINI"
   ODDS_API_KEY = "SUA_CHAVE_ODDS_API"
   NGROK_AUTHTOKEN = "SEU_TOKEN_NGROK"
   ```

5. **Iniciar a Aplicação:**
   ```bash
   python run.py
   ```
   *A aplicação iniciará automaticamente no navegador em `http://localhost:8501`.*

---

## ☁️ Implantação no Streamlit Cloud

1. Aceda ao [share.streamlit.io](https://share.streamlit.io) e conecte a sua conta GitHub.
2. Selecione o repositório `bf-betting-strategies` e a branch `main`.
3. Defina o **Main module path** como:
   ```text
   run.py
   ```
4. Na secção **Settings -> Secrets**, adicione as suas chaves de API.
5. Clique em **Deploy**!

---

## 📁 Estrutura do Projeto

```text
bf-betting-strategies/
├── .agents/                    # Skills e diretivas de desenvolvimento Streamlit
│   └── rules/                  # Regras detalhadas por página (filtros, botões, base de dados e matemática)
│       ├── 01_landing_and_nav_rules.md
│       ├── 02_ingestion_page_rules.md
│       ├── 03_analysis_page_rules.md
│       ├── 04_slips_page_rules.md
│       ├── 05_admin_page_rules.md
│       └── 06_database_and_math_rules.md
├── app.py                      # Ponto de entrada da aplicação Streamlit
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
