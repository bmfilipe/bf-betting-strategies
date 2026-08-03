# Regras de Negócio - Aba 2: Análise Estatística, Probabilidades & +EV (`ui/tab_analysis.py`)

Este documento especifica o funcionamento, motores estatísticos de Poisson 7x7, fórmulas matemáticas, filtros de análise, seleção dinâmica de tabela, radar charts e matrizes da página de **Análise Quantitativa & +EV**.

---

## 1. Motor Estatístico de Poisson & Fórmulas Matemáticas (`models/poisson.py`)

O processamento das odds e probabilidade de cada jogo baseia-se num motor quantitativo rigoroso:

### 1.1 Expectativa de Golos Ajustada (xG Ajustado)
Para cada partida entre Equipa Casa e Equipa Fora:
$$\text{ExpGoals}_{\text{Home}} = \frac{h\_xg + a\_xga}{2}$$
$$\text{ExpGoals}_{\text{Away}} = \frac{a\_xg + h\_xga}{2}$$

### 1.2 Matriz 7x7 de Dixon-Coles Poisson
Gera uma matriz joint de pontuações $7 \times 7$ (de 0 a 6 golos por equipa) com o fator de correção de Dixon-Coles ($\rho = -0.13$) para resultados de baixas pontuações:
$$\text{base\_p}(h, a) = \text{PoissonPMF}(\text{ExpGoals}_{\text{Home}}, h) \times \text{PoissonPMF}(\text{ExpGoals}_{\text{Away}}, a)$$

**Fator de Correção Dixon-Coles $\tau(h, a)$**:
- Se $h=0, a=0$: $\tau = \max(0, 1 - \lambda \cdot \mu \cdot \rho)$
- Se $h=1, a=0$: $\tau = \max(0, 1 + \mu \cdot \rho)$
- Se $h=0, a=1$: $\tau = \max(0, 1 + \lambda \cdot \rho)$
- Se $h=1, a=1$: $\tau = \max(0, 1 - \rho)$
- Para qualquer outro resultado: $\tau = 1.0$

A matriz final é re-normalizada dividindo pelo somatório total de todas as probabilidades da matriz para garantir que $\sum P(h,a) = 1.0$.

### 1.3 Probabilidade Implícita de Mercado (%)
$$\text{ProbImplícita}(\%) = \left(\frac{1.0}{\text{Odd}}\right) \times 100$$

### 1.4 Valor Esperado / Advantage (+EV %)
$$\text{EV}(\%) = \left(\left(\frac{\text{ProbEstimada}(\%)}{100} \times \text{Odd}\right) - 1.0\right) \times 100$$

### 1.5 Critério de Kelly Fracionado (1/4 Kelly)
Determina o dimensionamento ótimo de capital para maximizar o crescimento da banca minimizando o risco de ruína:
$$b = \text{Odd} - 1.0$$
$$p = \frac{\text{ProbEstimada}(\%)}{100}, \quad q = 1.0 - p$$
$$\text{FullKelly} = \frac{p \cdot b - q}{b} \quad (\text{se } b > 0 \text{ senão } 0)$$
$$\text{KellyStake}(\%) = \max(0.0, \text{FullKelly}) \times 0.25 \times 100$$
$$\text{StakeRecomendada}(€) = \text{BancaTotal}(€) \times \left(\frac{\text{KellyStake}(\%)}{100}\right)$$

### 1.6 Métricas de Retorno e Lucro
$$\text{Retorno Bruto}(€) = \text{StakeRecomendada}(€) \times \text{Odd}$$
$$\text{Lucro Líquido}(€) = \text{Retorno Bruto}(€) - \text{StakeRecomendada}(€)$$

---

## 2. Mapeamento de 21 Mercados Calculados por Jogo

Cada partida avaliada gera estimativas de probabilidades para 21 mercados principais:
1. `Vitória Casa (1)`: $\sum_{h > a} P(h,a)$
2. `Empate (X)`: $\sum_{h = a} P(h,a)$
3. `Vitória Fora (2)`: $\sum_{h < a} P(h,a)$
4. `Dupla Hipótese (1X)`: $P_1 + P_X$
5. `Dupla Hipótese (X2)`: $P_2 + P_X$
6. `Dupla Hipótese (12)`: $P_1 + P_2$
7. `Total +0.5 Golos`: $\sum_{h+a > 0.5} P(h,a)$
8. `Total +1.5 Golos`: $\sum_{h+a > 1.5} P(h,a)$
9. `Total +2.5 Golos`: $\sum_{h+a > 2.5} P(h,a)$
10. `Total +3.5 Golos`: $\sum_{h+a > 3.5} P(h,a)$
11. `Total -2.5 Golos`: $1.0 - P(+2.5)$
12. `Ambas Marcam (Sim)`: $\sum_{h \ge 1, a \ge 1} P(h,a)$
13. `Ambas Marcam (Não)`: $1.0 - P(\text{BTTS Sim})$
14. `Empate Anula Casa (DNB 1)`: $\frac{P_1}{P_1 + P_2}$
15. `Empate Anula Fora (DNB 2)`: $\frac{P_2}{P_1 + P_2}$
16. `Handicap Asiático Casa (AH -0.5)`: $P_1$
17. `Handicap Asiático Fora (AH +0.5)`: $P_{X2}$
18. `Handicap Asiático Casa (AH +0.5)`: $P_{1X}$
19. `Handicap Asiático Fora (AH -0.5)`: $P_2$
20. `Handicap Asiático Casa (AH -1.0)`: $P(h-a \ge 2) + 0.5 \times P(h-a = 1)$
21. `Handicap Asiático Fora (AH +1.0)`: $P_{X2} + 0.5 \times P(h-a = 1)$

Todas as avaliações quantitativas geradas são armazenadas na sessão (`st.session_state["analysed_results"]`) e automaticamente persistidas na base de dados SQLite (tabela `evaluations` via `save_analysis_to_db`).

---

## 3. Filtros Interativos do Painel

- **`Filtrar por País / Região`** (`sel_country`):
  - Popula dinamicamente os países realmente presentes nas análises mais a lista predefinida. Predefinição: `"Todos"`.
- **`Filtrar por Estratégia de Mercado`** (`sel_strategy`):
  - `Todas as Estratégias` (Predefinição)
  - `Resultado Final (1X2)`
  - `Total de Golos (+0.5, +1.5, +2.5)`
  - `Ambas Marcam (BTTS Sim / Não)`
  - `Apostas Apenas +EV (EV > 0%)`
- **`EV Mínimo (+EV %)`** (`min_ev_filter`):
  - Slider: Mínimo `-20.0`, Máximo `30.0`, Valor por defeito `0.0`, Passo `1.0`.
- **`Tua Banca Total (€)`** (`user_bankroll`):
  - Number input: Predefinição `100.0 €`, Passo `10.0 €`, Mínimo `10.0 €`.
  - Recalcula instantaneamente as colunas `KellyStake (%)`, `Stake Recomendada (€)`, `Retorno (€)` e `Lucro Líquido (€)`.

---

## 4. Tabela Quantitativa & Seleção Dinâmica de Linhas

### 4.1 Colunas Apresentadas na Tabela
`País`, `Liga`, `Jogo`, `Mercado`, `Odd`, `Prob. Implícita (%)`, `Prob. Estimada (%)`, `Expected Value (+EV) (%)`, `KellyStake (%)`, `Stake Recomendada (€)`, `Retorno (se acertar) (€)`, `Lucro Líquido (€)`.

### 4.2 Formatação Condicional de Cores
- **Coluna `Expected Value (+EV) (%)`**:
  - Se $> 0\%$: Destacado a verde fluorescente com texto a verde escuro (`background-color: rgba(16, 185, 129, 0.25); color: #10b981; font-weight: bold;`).
  - Se $\le 0\%$: Destacado a vermelho suave (`background-color: rgba(239, 68, 68, 0.15); color: #ef4444;`).

### 4.3 Seleção Múltipla de Linhas (`on_select="rerun"`)
- O utilizador pode selecionar caixas de verificação diretamente na tabela (`selection_mode="multi-row"`).
- **Barra de Totais Resumo abaixo da tabela**:
  - `Seleção Ativa`: Contagem das linhas selecionadas (ou todas se nenhuma estiver selecionada).
  - `Total Stake Recomendada`: Somatório de `Stake Recomendada (€)` da seleção ativa.
  - `Total Retorno (se acertar)`: Somatório de `Retorno (se acertar) (€)` da seleção ativa.
  - `Total Lucro Líquido`: Somatório de `Lucro Líquido (€)` da seleção ativa.
- **Sincronização com a Aba 3**: A seleção ativa é automaticamente guardada em `st.session_state["analysed_results"]` para servir de pool na geração de boletins.

---

## 5. Inspetor de Partida, Radar Chart & Heatmap 7x7

- **Selectbox de Seleção de Partida**: Escolhe uma das partidas carregadas para inspecionar em detalhe.
- **Cartão de Informação H2H & Forma**:
  - Exibe a forma recente dos últimos 5 jogos da equipa da Casa e Fora.
  - Exibe o resumo histórico H2H da partida.
- **Métricas de Apoio**:
  - `Exp. Golos Casa`, `Exp. Golos Fora`, `Expected Value (+EV Principal)`.
- **Gráfico Radar Comparativo (Plotly)**:
  - Compara Casa (Verde) vs. Fora (Vermelho) através das dimensões: `Ataque (xG)`, `Prob. Vitória 1X2`, `Dupla Hipótese` e `Empate Anula (DNB)`.
- **Heatmap 7x7 da Matriz de Poisson (Plotly)**:
  - Exibe o mapa de calor com a escala de cores `Viridis` para a matriz conjunta de pontuações de 0 a 6 golos.
