---
name: developing-with-streamlit
description: Diretivas e padrões de desenvolvimento para a interface Streamlit do aplicativo BF Analista de Futebol.
---

# Diretivas de Desenvolvimento Streamlit (v3.0.0)

## 🎨 Design & Estilização
- Manter o tema adaptativo **Dark / Light** de alto contraste via `ui/styles.py`.
- Utilizar botões de largura total (`width="stretch"`) em formulários e barras laterais.
- Destacar métricas principais com cartões `st.container(border=True)` ou `st.metric`.
- Renderizar gráficos interativos via **Plotly Express / Plotly Graph Objects** em modo escuro/claro adaptativo.

## ⚡ Performance
- Utilizar `@st.fragment` para tabelas e componentes interativos com filtragem local sem forçar o recarregamento global da página.
- Guardar estados pesados em `st.session_state` e sincronizar sempre com a base de dados SQLite (`database/bfbetting.db`).

## 🗂️ Estrutura de Páginas
1. `ui/tab_ingestion.py`: Ingestão pré-jogo.
2. `ui/tab_live.py`: Jogos ao vivo (In-Play) com minuto e odds em direto.
3. `ui/tab_h2h.py`: Comparador de Equipas (H2H) com Web Scraping.
4. `ui/tab_analysis.py`: Análise quantitativa de Poisson e +EV.
5. `ui/tab_slips.py`: Gerador combinatório de boletins de apostas.
6. `ui/tab_admin.py`: Área restrita do administrador com gestão de BD SQLite, Vault e exportações.
