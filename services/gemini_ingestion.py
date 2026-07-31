import json
import re
import datetime
import math
from google import genai
from google.genai import types
from config import DEFAULT_MOCK_MATCHES

class GeminiIngestionService:
    """
    Ingestion service to fetch today's real football matches with xG / xGA metrics
    and market odds from Gemini 2.5 Flash using official google-genai SDK
    with real-time Google Search grounding and dynamic date injection.
    """

    @staticmethod
    def _safe_float(val, default: float = 1.5) -> float:
        """Safely convert value to float, ensuring a positive valid number > 0.0."""
        if val is None:
            return default
        try:
            res = float(val)
            return res if (not math.isnan(res) and res > 0.0) else default
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _safe_str(val, default: str = "Geral") -> str:
        """Safely convert value to string, handling None or null values."""
        if val is None:
            return default
        s = str(val).strip()
        return s if s else default

    @classmethod
    def fetch_today_matches(
        cls,
        api_key: str,
        selected_countries: list[str] = None,
        max_matches: int = 20
    ) -> tuple[list[dict], str]:
        """
        Fetch real-time matches for today's date from Gemini API with Google Search grounding,
        targeted country/league filters and max matches limit.
        Returns (matches_list, status_message).
        """
        if not api_key:
            return DEFAULT_MOCK_MATCHES, "Aviso: Gemini API Key não configurada. A utilizar dados de demonstração."

        today_str = datetime.date.today().strftime("%Y-%m-%d")
        today_formatted = datetime.date.today().strftime("%d de %B de %Y")

        if selected_countries and "Todas as Ligas/Países" not in selected_countries:
            countries_joined = ", ".join(selected_countries)
            country_filter_str = f"Foca a pesquisa ESTRITAMENTE nas partidas pertencentes às seguintes regiões/competições: {countries_joined}."
        else:
            country_filter_str = "Procura jogos das principais ligas mundiais (Liga Portugal, Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Brasileirão, UEFA Europa League, UEFA Champions League, UEFA Conference League, etc.)."

        try:
            client = genai.Client(api_key=api_key)

            prompt = f"""
            IMPORTANTE: A data de HOJE é EXATAMENTE {today_str} ({today_formatted}).
            Pesquisa na web em tempo real os jogos de futebol REAIS agendados para a data de HOJE ({today_str}).
            {country_filter_str}
            Tenta obter até {max_matches} partidas reais agendadas para a data de hoje.

            Para cada jogo real encontrado para HOJE ({today_str}), extrai/estima:
            - country: País ou Região da competição
            - league: Nome oficial da Liga / Competição
            - home: Equipa da Casa
            - away: Equipa Visitante
            - h_xg: Média estimada de Golos Esperados da Equipa da Casa (ex: 1.8)
            - a_xg: Média estimada de Golos Esperados da Equipa Visitante (ex: 1.1)
            - h_xga: Golos Esperados Concedidos pela Casa (ex: 0.9)
            - a_xga: Golos Esperados Concedidos pelos Visitantes (ex: 1.6)
            - odd_1: Odd real para Vitória da Casa (1) (ex: 1.65)
            - odd_x: Odd real para Empate (X) (ex: 3.80)
            - odd_2: Odd real para Vitória Fora (2) (ex: 5.00)
            - odd_1x: Odd real para Dupla Hipótese Casa ou Empate (1X) (ex: 1.18)
            - odd_x2: Odd real para Dupla Hipótese Empate ou Fora (X2) (ex: 2.10)
            - odd_o05: Odd para Total +0.5 Golos (ex: 1.05)
            - odd_o15: Odd para Total +1.5 Golos (ex: 1.25)
            - odd_o25: Odd para Total +2.5 Golos (ex: 1.80)
            - odd_o35: Odd para Total +3.5 Golos (ex: 2.90)
            - odd_btts_yes: Odd para Ambas Marcam Sim (ex: 1.75)
            - odd_btts_no: Odd para Ambas Marcam Não (ex: 1.95)
            - odd_dnb1: Odd para Empate Anula Casa (DNB 1) (ex: 1.25)
            - odd_dnb2: Odd para Empate Anula Fora (DNB 2) (ex: 3.50)
            - home_form: Forma recente nos ÚLTIMOS 5 JOGOS OFICIAIS da Casa em qualquer competição, ordenados do mais antigo para o MAIS RECENTE à direita (ex: "V-D-V-D-V")
            - away_form: Forma recente nos ÚLTIMOS 5 JOGOS OFICIAIS de Fora em qualquer competição, ordenados do mais antigo para o MAIS RECENTE à direita (ex: "D-D-D-V-E")
            - h2h_summary: Resumo dos confrontos diretos H2H exclusivamente entre estas 2 equipas nos últimos anos (ex: "Últimos 3 jogos diretos: 2 Vitórias Casa, 1 Empate")
            - odd: Odd do mercado principal recomendado (ex: 1.65)
            - market: Mercado principal recomendado (ex: "Vitória Casa (1)")

            Responde EXCLUSIVAMENTE num array JSON válido (nunca uses valores nulos ou zeros nas odds):
            [
                {{
                    "country": "Europa",
                    "league": "Liga Europa",
                    "home": "Benfica",
                    "away": "St. Gallen",
                    "h_xg": 2.1,
                    "a_xg": 0.9,
                    "h_xga": 0.8,
                    "a_xga": 1.8,
                    "odd_1": 1.45,
                    "odd_x": 4.50,
                    "odd_2": 6.50,
                    "odd_1x": 1.12,
                    "odd_x2": 2.50,
                    "odd_o05": 1.05,
                    "odd_o15": 1.22,
                    "odd_o25": 1.62,
                    "odd_o35": 2.60,
                    "odd_btts_yes": 1.75,
                    "odd_btts_no": 2.00,
                    "odd_dnb1": 1.15,
                    "odd_dnb2": 4.20,
                    "home_form": "V-D-V-D-V",
                    "away_form": "D-E-V-D-E",
                    "h2h_summary": "Últimos 3 jogos: 2 Vitórias Benfica, 1 Empate",
                    "odd": 1.45,
                    "market": "Vitória Casa (1)"
                }}
            ]
            NÃO inventes partidas fictícias. Apenas jogos REAIS agendados para {today_str}.
            """

            # Attempt content generation with Google Search grounding enabled
            try:
                config = types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                    response_mime_type="application/json"
                )
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=config
                )
            except Exception:
                try:
                    config = types.GenerateContentConfig(
                        tools=[{"google_search": {}}]
                    )
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=config
                    )
                except Exception:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )

            raw_text = response.text if hasattr(response, 'text') else str(response)

            # Strip markdown codeblocks
            clean_str = raw_text.replace("```json", "").replace("```", "").strip()

            parsed_data = None
            try:
                parsed_data = json.loads(clean_str)
            except Exception:
                json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
                if json_match:
                    try:
                        parsed_data = json.loads(json_match.group(0))
                    except Exception:
                        pass

            if isinstance(parsed_data, list) and len(parsed_data) > 0:
                cleaned = []
                for item in parsed_data:
                    if isinstance(item, dict) and item.get("home") and item.get("away"):
                        odd_1_val = cls._safe_float(item.get("odd_1"), 1.60)
                        odd_x_val = cls._safe_float(item.get("odd_x"), 3.80)
                        odd_2_val = cls._safe_float(item.get("odd_2"), 4.80)

                        cleaned.append({
                            "country": cls._safe_str(item.get("country"), "Geral"),
                            "league": cls._safe_str(item.get("league"), "Geral"),
                            "home": cls._safe_str(item.get("home"), "Equipa Casa"),
                            "away": cls._safe_str(item.get("away"), "Equipa Fora"),
                            "h_xg": cls._safe_float(item.get("h_xg"), 1.5),
                            "a_xg": cls._safe_float(item.get("a_xg"), 1.0),
                            "h_xga": cls._safe_float(item.get("h_xga"), 1.0),
                            "a_xga": cls._safe_float(item.get("a_xga"), 1.5),
                            "odd_1": odd_1_val,
                            "odd_x": odd_x_val,
                            "odd_2": odd_2_val,
                            "odd_1x": cls._safe_float(item.get("odd_1x"), round(1.0 / ((1.0/odd_1_val) + (1.0/odd_x_val)), 2)),
                            "odd_x2": cls._safe_float(item.get("odd_x2"), round(1.0 / ((1.0/odd_x_val) + (1.0/odd_2_val)), 2)),
                            "odd_o05": cls._safe_float(item.get("odd_o05"), 1.06),
                            "odd_o15": cls._safe_float(item.get("odd_o15"), 1.25),
                            "odd_o25": cls._safe_float(item.get("odd_o25"), 1.80),
                            "odd_o35": cls._safe_float(item.get("odd_o35"), 2.90),
                            "odd_btts_yes": cls._safe_float(item.get("odd_btts_yes"), 1.75),
                            "odd_btts_no": cls._safe_float(item.get("odd_btts_no"), 1.95),
                            "odd_dnb1": cls._safe_float(item.get("odd_dnb1"), round(odd_1_val * 0.75, 2)),
                            "odd_dnb2": cls._safe_float(item.get("odd_dnb2"), round(odd_2_val * 0.75, 2)),
                            "home_form": cls._safe_str(item.get("home_form"), "V-E-V-D-V"),
                            "away_form": cls._safe_str(item.get("away_form"), "E-D-V-V-D"),
                            "h2h_summary": cls._safe_str(item.get("h2h_summary"), "Sem histórico recente registrado."),
                            "odd": cls._safe_float(item.get("odd"), odd_1_val),
                            "market": cls._safe_str(item.get("market"), "Vitória Casa (1)")
                        })

                if cleaned:
                    return cleaned, f"Sucesso: {len(cleaned)} jogos reais obtidos em tempo real para a data de hoje ({today_str}) via Gemini Flash!"

            return DEFAULT_MOCK_MATCHES, f"Aviso: Não foram encontrados dados JSON na resposta de hoje ({today_str}). A carregar dados de demonstração."

        except Exception as e:
            return DEFAULT_MOCK_MATCHES, f"Erro na comunicação com a API Gemini ({str(e)}). A utilizar dados de demonstração."
