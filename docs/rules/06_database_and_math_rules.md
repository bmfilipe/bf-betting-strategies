# Regras de Negócio - Base de Dados SQLite & Arquitetura Matemática (`database/db.py` & `models/poisson.py`)

Este documento especifica o esquema relacional da base de dados SQLite (`bfbetting.db`), regras de migração automática, índices de pesquisa, estrutura de payload JSON e o resumo unificado das fórmulas matemáticas.

---

## 1. Arquitetura da Base de Dados SQLite (`database/db.py`)

- **Ficheiro de Base de Dados**: `database/bfbetting.db`
- **Modo de Conexão**: `sqlite3.connect` com `check_same_thread=False` e `row_factory = sqlite3.Row`.

---

## 2. Tabelas Relacionais & Esquemas

### 2.1 Tabela `matches` (Jogos Mapeados)
Armazena as partidas brutas captadas das APIs/scrapers:

```sql
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_key TEXT UNIQUE NOT NULL,
    country TEXT,
    league TEXT,
    home_team TEXT,
    away_team TEXT,
    h_xg REAL,
    a_xg REAL,
    h_xga REAL,
    a_xga REAL,
    odd_1 REAL,
    odd_x REAL,
    odd_2 REAL,
    odd_o05 REAL,
    odd_o15 REAL,
    odd_o25 REAL,
    odd_btts_yes REAL,
    odd_btts_no REAL,
    home_form TEXT,
    away_form TEXT,
    h2h_summary TEXT,
    provider TEXT,
    data_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- **Constraint de Chave Única**: `match_key` (formato em minusculas: `{home}_vs_{away}_{league}`).
- **Regra de Inserção / Atualização (`save_matches_to_db`)**:
  - Utiliza `ON CONFLICT(match_key) DO UPDATE SET ...` para atualizar odds e métricas existentes sem duplicar linhas.
- **Índices de Pesquisa Criados**:
  - `idx_matches_teams`: Indexa `(home_team, away_team)`.
  - `idx_matches_league`: Indexa `(country, league)`.

---

### 2.2 Tabela `evaluations` (Avaliações Quantitativas +EV)
Armazena os cálculos estatísticos e de valor esperado para cada mercado individual:

```sql
CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_key TEXT NOT NULL,
    match_name TEXT,
    country TEXT,
    league TEXT,
    strategy_group TEXT,
    market TEXT,
    odd REAL,
    implied_prob REAL,
    estimated_prob REAL,
    ev_percent REAL,
    exp_goals_home REAL,
    exp_goals_away REAL,
    data_json TEXT NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(match_key, market)
);
```

- **Constraint de Chave Única**: `(match_key, market)`.
- **Regra de Inserção / Atualização (`save_analysis_to_db`)**:
  - Atualiza odd, prob. implícita, prob. estimada, $+EV$ e payload JSON ao reavaliar uma partida.
- **Índices de Pesquisa Criados**:
  - `idx_eval_ev`: Indexa `ev_percent` para filtragem ultra-rápida de apostas $+EV$.
  - `idx_eval_strategy`: Indexa `strategy_group`.

---

### 2.3 Tabela `bet_slips` (Boletins Gerados)
Armazena o histórico de boletins múltiplos gerados no sistema:

```sql
CREATE TABLE IF NOT EXISTS bet_slips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slip_name TEXT,
    strategy_type TEXT,
    total_odd REAL,
    matches_count INTEGER,
    data_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 2.4 Tabela `app_settings` (Vault de Configurações)
Armazena chaves de API, credenciais e definições globais da aplicação:

```sql
CREATE TABLE IF NOT EXISTS app_settings (
    key_name TEXT PRIMARY KEY,
    key_value TEXT,
    category TEXT DEFAULT 'GENERAL',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- **Regras de Leitura/Escrita (`save_setting`, `load_settings`)**:
  - `save_setting`: Insere ou atualiza via `ON CONFLICT(key_name) DO UPDATE`.
  - `export_settings_json`: Gera backup em string JSON contendo todas as chaves e valores.
  - `import_settings_json`: Lê o ficheiro JSON e restaura as chaves no banco SQLite com a categoria `'IMPORTED'`.

---

### 2.5 Tabela `ingestion_logs`
Regista os eventos de captação de partidas via API ou scraper:

```sql
CREATE TABLE IF NOT EXISTS ingestion_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT,
    status TEXT,
    message TEXT,
    matches_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Resumo Completo dos Algoritmos Matemáticos

| Conceito | Fórmula Matemática | Finalidade |
| :--- | :--- | :--- |
| **xG Ajustado Casa** | $ExpGoals_{Home} = \frac{h\_xg + a\_xga}{2}$ | Expectativa de golos marcados pela casa |
| **xG Ajustado Fora** | $ExpGoals_{Away} = \frac{a\_xg + h\_xga}{2}$ | Expectativa de golos marcados pela visita |
| **Poisson PMF** | $P(X=k) = \frac{\lambda^k e^{-\lambda}}{k!}$ | Probabilidade de $k$ golos com média $\lambda$ |
| **Dixon-Coles $\tau$** | Ajuste em $(0,0), (1,0), (0,1), (1,1)$ com $\rho=-0.13$ | Corrige a independência em pontuações baixas |
| **Prob. Implícita** | $P_{imp} = \left(\frac{1}{Odd}\right) \times 100$ | Probabilidade percentual implícita na odd |
| **Valor Esperado (+EV)**| $+EV(\%) = \left(\frac{P_{est}}{100} \cdot Odd - 1\right) \times 100$ | Lucro esperado em % por unidade apostada |
| **1/4 Kelly Stake** | $Kelly\% = \max\left(0, \frac{p \cdot (Odd-1) - (1-p)}{Odd-1}\right) \times 25\%$ | Dimensionamento ótimo e seguro da banca |
| **Stake Recomendada** | $Stake(€) = Banca(€) \times \left(\frac{Kelly\%}{100}\right)$ | Montante em Euros a apostar |
| **Retorno Bruto** | $Retorno(€) = Stake(€) \times Odd$ | Ganho total se a aposta for ganha |
| **Lucro Líquido** | $Lucro(€) = Retorno(€) - Stake(€)$ | Ganho limpo após subtrair o valor apostado |
| **Odd Total Boletim** | $Odd_{Total} = \prod_{i=1}^N Odd_i$ | Multiplicação das odds das pernas do bilhete |
