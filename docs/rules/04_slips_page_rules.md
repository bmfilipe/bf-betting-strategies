# Regras de Negócio - Aba 3: Gerador de Boletins & Exportação (`ui/tab_slips.py`)

Este documento especifica o funcionamento, algoritmos combinatórios sem partidas duplicadas, perfis de risco, sincronização de stakes, relatórios e envio de e-mails da página de **Geração de Boletins**.

---

## 1. Definições & Parâmetros de Entrada

A geração de boletins baseia-se na lista `st.session_state["analysed_results"]` selecionada na Aba 2.

### 1.1 Controlos de Configuração
- **`Jogos por Boletim (Múltipla)`** (`n_games`): Selectbox com opções `2`, `3`, `4`, `5` (Predefinição: `3`).
- **`Perfil de Risco do Boletim`** (`risk_profile`):
  - `🟢 Risco Baixo (Odds Baixas / Favoritos)`: Prioriza as menores odds / seleções mais conservadoras.
  - `🟡 Risco Médio (Odds Equilibradas / +EV)`: Prioriza os maiores valores de $+EV$.
  - `🔴 Risco Alto (Odds Elevadas / Retorno Alto)`: Prioriza as maiores odds para maximizar o retorno potencial.
- **`Quantidade de Boletins a Gerar`** (`num_boletins`): Slider de `1` a `10` (Predefinição: `5`).
- **`Stake Padrão (€) por Boletim`** (`global_stake`): Number input com predefinição `10.0 €`.
  - **Sincronização Dinâmica**: Quando o utilizador altera a `global_stake`, o sistema atualiza automaticamente o valor das variáveis individuais `st.session_state[f"stake_{i}"]` para cada boletim de 0 a 14.
- **`Estratégia(s) dos Boletins`** (`selected_strategies`): Multiselect com 9 opções:
  1. `⚽ Resultado Final (1X2)`
  2. `🛡️ Dupla Hipótese (1X / X2)`
  3. `🔥 Ambas Marcam (BTTS)`
  4. `⚡ Total +0.5 Golos`
  5. `🎯 Total +1.5 Golos`
  6. `🚀 Total +2.5 Golos`
  7. `⚽ Total +3.5 Golos`
  8. `🥅 Empate Anula (DNB)`
  9. `🛡️ Handicap Asiático (AH)`

---

## 2. Algoritmo Combinatório sem Jogos Duplicados

O motor garante estritamente que **num mesmo boletim não existem partidas repetidas**.

### 2.1 Passos do Algoritmo:
1. **Filtragem do Pool**: Seleciona as apostas da análise cujas estratégias/mercados correspondem a pelo menos uma das opções em `selected_strategies`.
2. **Agrupamento por Partida Única**: Mapeia as apostas num dicionário de jogos únicos por título (`Jogo`):
   $$\text{match\_dict}[\text{m\_title}] = [\text{item}_1, \text{item}_2, \dots]$$
3. **Validação de Quantidade Mínima**:
   - Se o número de partidas distintas $T < n\_games$, o sistema exibe um aviso de erro bloqueando a geração e solicita ao utilizador reduzir $n\_games$ ou captar mais partidas.
4. **Rotação Determinística de Partidas**:
   Para cada boletim $b\_idx$ de $0$ a $num\_boletins - 1$:
   $$\text{start\_idx} = (b\_idx \times n\_games) \pmod T$$
   São selecionadas as $n\_games$ partidas contíguas a partir de $\text{start\_idx}$ com wrap-around circular.
5. **Seleção da Aposta conforme Perfil de Risco**:
   Dentro de cada partida selecionada, escolhe-se o mercado específico com base na ordenação do perfil de risco:
   - **Risco Baixo**: Ordena por `(Odd, -EV%)` ascendente $\rightarrow$ escolhe o 1º elemento.
   - **Risco Alto**: Ordena por `(Odd, EV%)` descendente $\rightarrow$ escolhe o 1º elemento.
   - **Risco Médio**: Ordena por `EV%` descendente $\rightarrow$ escolhe o 1º elemento.
6. **Cálculo da Odd Total e Payout do Boletim**:
   $$\text{Odd}_{\text{Total}} = \prod_{i=1}^{n\_games} \text{Odd}_i$$
   $$\text{Ganho Potencial}(€) = \text{Odd}_{\text{Total}} \times \text{Stake}_{\text{Boletim}}$$

---

## 3. Resumo Acumulado dos Boletins

Apresenta as métricas globais dos boletins gerados:
- `Total de Boletins`: Número total de bilhetes gerados.
- `Investimento Total (Stake)`: $\sum \text{Stake}_i$
- `Retorno Potencial Acumulado`: $\sum \text{Ganho Potencial}_i$

---

## 4. Módulos de Exportação & Envio (`services/exporter.py` & `services/email_service.py`)

O utilizador dispõe de 4 canais de exportação:

### 4.1 Descarregar Relatório `.TXT` (`ReportExporter.generate_txt_report`)
- Gera um ficheiro de texto simples contendo o cabeçalho, parâmetros, lista detalhada dos boletins com odds e ganhos potenciais, e o resumo de investimento total.

### 4.2 Descarregar Relatório `.PDF` (`ReportExporter.generate_pdf_report`)
- Utiliza a biblioteca `FPDF2` para gerar um documento PDF formal e estilizado com tabela de jogos por boletim e métricas consolidadas.

### 4.3 Descarregar Tabela `.CSV` (`ReportExporter.generate_csv_report`)
- Exporta uma estrutura CSV compatível com Microsoft Excel contendo todas as colunas dos boletins e seleções individuais.

### 4.4 Envio de Notificação por E-mail (SMTP)
- **Campo**: `dest_email` (Input de texto do endereço destinatário).
- **Botão `📧 Enviar por E-mail`**:
  - Utiliza o serviço `EmailService.send_report_email(...)` com o remetente `email_sender` e palavra-passe SMTP `email_password` (configurados no Vault da Administração).
  - Anexa o documento PDF gerado e insere o texto do relatório no corpo da mensagem.
