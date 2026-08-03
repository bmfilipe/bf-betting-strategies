---
name: bf-betting-architecture
description: Arquitetura completa do sistema BF Analista de Futebol, motores de ingestão, Web Scraping e esquema SQLite.
---

# Arquitetura do Sistema & Diretivas (v3.0.0)

## 🗄️ Esquema da Base de Dados SQLite (`database/bfbetting.db`)

O sistema utiliza a base de dados relacional `bfbetting.db` com as seguintes tabelas indexadas:

1. `matches`: Jogos pré-jogo descarregados dos provedores de odds (The Odds API, OddsPortal, Gemini).
2. `live_matches`: Partidas a decorrer em tempo real (In-Play) com pontuação, minuto e odds ao vivo.
3. `team_h2h_history`: Histórico de confrontos diretos e métricas comparativas recolhidas por Web Scraping.
4. `team_stats_cache`: Cache estatística de equipas individuais.
5. `evaluations`: Resultados das análises estatísticas de Poisson 7x7 e cálculo de Valor Esperado (+EV).
6. `bet_slips`: Boletins combinados e simples gerados pelo sistema.
7. `app_settings`: Vault seguro de credenciais, chaves de API e definições da aplicação.
8. `ingestion_logs`: Histórico de execuções e registo de logs de ingestão de dados.

## 🕷️ Motores de Ingestão & Scraping (`services/`)

- `live_matches_service.py`: Captação em tempo real via API-Football (`live=all`) ou engine de dados desportivos open-source fallback com gravação em `live_matches`.
- `h2h_scraper.py`: Motor de Web Scraping e estatística comparativa entre duas equipas com gravação em `team_h2h_history`.
- `db.py`: Gestor SQL relacional com auto-migração de colunas, backup/restauro do ficheiro `.db` e exportação para CSV e JSON.

## 🔄 Regra de Atualização de Versões
Sempre que forem adicionadas novas funcionalidades ou alterações estruturais ao projeto:
1. Incrementar a versão em `versions.txt` com o respetivo changelog.
2. Atualizar o número de versão na área restrita (`ui/tab_admin.py` -> Separador "Sobre").
3. Manter a documentação em `.agents` e no `README.md` sincronizada.
