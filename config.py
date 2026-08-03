import streamlit as st
import datetime
import math
import json
import os
import unicodedata
from typing import List, Optional, Tuple, Dict, Any

ADMIN_PASSWORD_HASH = "Admin#1976"

<<<<<<< HEAD
DEFAULT_MOCK_MATCHES = [
    {
        "country": "Europa",
        "league": "Liga Europa",
        "home": "Benfica",
        "away": "St. Gallen",
        "h_xg": 2.15,
        "a_xg": 0.90,
        "h_xga": 0.80,
        "a_xga": 1.85,
        "odd_1": 1.45,
        "odd_x": 4.50,
        "odd_2": 6.50,
        "odd_o05": 1.05,
        "odd_o15": 1.22,
        "odd_o25": 1.62,
        "odd_btts_yes": 1.75,
        "odd_btts_no": 2.00,
        "home_form": "V-D-V-D-V",
        "away_form": "D-E-V-D-E",
        "h2h_summary": "Últimos 3 confrontos: 2 Vitórias Benfica, 1 Empate (Média 3.3 golos/jogo)",
        "odd": 1.45,
        "market": "Vitória Casa (1)",
        "date": "03/08/2026 21:00",
        "result": "1-0 (Ao Vivo)",
        "status": "LIVE"
    },
    {
        "country": "Europa",
        "league": "Liga Europa",
        "home": "Anderlecht",
        "away": "Hammarby",
        "h_xg": 1.90,
        "a_xg": 0.95,
        "h_xga": 0.90,
        "a_xga": 1.40,
        "odd_1": 1.68,
        "odd_x": 3.80,
        "odd_2": 4.80,
        "odd_o05": 1.08,
        "odd_o15": 1.28,
        "odd_o25": 1.85,
        "odd_btts_yes": 1.80,
        "odd_btts_no": 1.95,
        "home_form": "V-E-V-V-D",
        "away_form": "E-V-D-E-V",
        "h2h_summary": "Primeiro confronto direto oficial registrado.",
        "odd": 1.68,
        "market": "Vitória Casa (1)",
        "date": "03/08/2026 20:30",
        "result": "Por iniciar",
        "status": "SCHEDULED"
=======
LEAGUE_TEAMS_DATABASE = {
    "Portugal (Primeira Liga / Segunda Liga)": {
        "country": "Portugal",
        "league": "Liga Portugal Betclic",
        "pairs": [
            ("Benfica", "Porto", 1.50, 4.20, 6.00, 2.15, 0.90),
            ("Sporting CP", "Braga", 1.65, 3.90, 4.80, 1.95, 1.20),
            ("Vitória SC", "Boavista", 1.75, 3.60, 4.50, 1.70, 1.00),
            ("Famalicão", "Gil Vicente", 2.10, 3.20, 3.50, 1.40, 1.30),
            ("Rio Ave", "Moreirense", 2.30, 3.10, 3.10, 1.25, 1.25),
            ("Estoril", "Arouca", 2.40, 3.30, 2.80, 1.50, 1.60)
        ]
    },
    "Inglaterra (Premier League / Championship / League 1)": {
        "country": "Inglaterra",
        "league": "Premier League",
        "pairs": [
            ("Arsenal", "Chelsea", 1.70, 3.90, 4.60, 2.05, 1.15),
            ("Liverpool", "Manchester City", 2.45, 3.50, 2.70, 2.20, 2.10),
            ("Manchester United", "Tottenham", 2.30, 3.60, 2.85, 1.80, 1.90),
            ("Aston Villa", "Newcastle", 2.15, 3.40, 3.20, 1.75, 1.65),
            ("Brighton", "West Ham", 1.90, 3.70, 3.80, 1.90, 1.45)
        ]
>>>>>>> bcd5ae0ad2a3dcc5840cd7d5d3acfe89ef908fe4
    },
    "Espanha (La Liga / Segunda División)": {
        "country": "Espanha",
        "league": "La Liga",
        "pairs": [
            ("Real Madrid", "Atletico Madrid", 2.05, 3.30, 3.60, 1.85, 1.30),
            ("Barcelona", "Sevilla", 1.45, 4.50, 6.50, 2.30, 0.90),
            ("Athletic Bilbao", "Real Sociedad", 2.20, 3.10, 3.40, 1.40, 1.20),
            ("Villarreal", "Valencia", 1.85, 3.50, 4.10, 1.80, 1.35)
        ]
    },
    "Itália (Serie A / Serie B)": {
        "country": "Itália",
        "league": "Serie A",
        "pairs": [
            ("Inter de Milão", "AC Milan", 2.10, 3.30, 3.40, 1.75, 1.40),
            ("Juventus", "Roma", 2.00, 3.20, 3.80, 1.50, 1.10),
            ("Napoli", "Lazio", 1.95, 3.40, 3.90, 1.65, 1.25),
            ("Atalanta", "Fiorentina", 1.80, 3.70, 4.20, 2.10, 1.50)
        ]
    },
    "Alemanha (Bundesliga / 2. Bundesliga)": {
        "country": "Alemanha",
        "league": "Bundesliga",
        "pairs": [
            ("Bayern Munique", "Bayer Leverkusen", 2.15, 3.80, 3.00, 2.40, 2.10),
            ("Borussia Dortmund", "RB Leipzig", 2.25, 3.70, 2.80, 2.10, 1.95),
            ("Eintracht Frankfurt", "VfB Stuttgart", 2.40, 3.50, 2.70, 1.70, 1.85)
        ]
    },
    "França (Ligue 1 / Ligue 2)": {
        "country": "França",
        "league": "Ligue 1",
        "pairs": [
            ("PSG", "Marseille", 1.50, 4.40, 5.80, 2.50, 1.05),
            ("Monaco", "Lille", 2.20, 3.40, 3.20, 1.80, 1.50),
            ("Lyon", "Rennes", 2.10, 3.40, 3.40, 1.65, 1.55)
        ]
    },
    "Europa (UEFA Champions / Europa League / Conference League)": {
        "country": "Europa",
        "league": "UEFA Champions League",
        "pairs": [
            ("Real Madrid", "Bayern Munique", 2.30, 3.60, 2.85, 2.05, 1.85),
            ("PSG", "Inter de Milão", 2.00, 3.40, 3.70, 1.80, 1.35),
            ("Barcelona", "Manchester City", 2.55, 3.60, 2.55, 2.15, 2.15)
        ]
    },
    "Brasil (Brasileirão Serie A / Serie B)": {
        "country": "Brasil",
        "league": "Brasileirão Série A",
        "pairs": [
            ("Flamengo", "Palmeiras", 2.20, 3.10, 3.30, 1.55, 1.35),
            ("São Paulo", "Corinthians", 2.10, 3.00, 3.70, 1.45, 1.15),
            ("Botafogo", "Fluminense", 1.95, 3.20, 4.00, 1.60, 1.20)
        ]
    },
    "Escócia (Premiership)": {
        "country": "Escócia",
        "league": "Scottish Premiership",
        "pairs": [
            ("Celtic", "Rangers", 2.05, 3.50, 3.30, 2.10, 1.70),
            ("Hearts", "Hibernian", 2.15, 3.30, 3.20, 1.60, 1.45),
            ("Aberdeen", "Motherwell", 1.85, 3.50, 4.00, 1.75, 1.25),
            ("Dundee United", "St. Mirren", 2.30, 3.10, 3.10, 1.35, 1.35),
            ("Kilmarnock", "Ross County", 1.90, 3.40, 3.90, 1.50, 1.15)
        ]
    },
    "Suíça (Super League / Challenge League)": {
        "country": "Suíça",
        "league": "Swiss Super League",
        "pairs": [
            ("Young Boys", "Basel", 1.95, 3.60, 3.50, 2.15, 1.65),
            ("Servette", "Zurich", 2.10, 3.30, 3.30, 1.70, 1.50),
            ("Lugano", "St. Gallen", 2.20, 3.40, 3.00, 1.80, 1.75),
            ("Luzern", "Lausanne-Sport", 2.00, 3.40, 3.50, 1.85, 1.40),
            ("Winterthur", "Grasshopper", 2.35, 3.20, 2.90, 1.45, 1.55)
        ]
    },
    "Áustria (Bundesliga / 2. Liga)": {
        "country": "Áustria",
        "league": "Austrian Bundesliga",
        "pairs": [
            ("Red Bull Salzburg", "Sturm Graz", 1.80, 3.80, 4.00, 2.25, 1.45),
            ("Rapid Wien", "LASK", 2.15, 3.40, 3.10, 1.75, 1.60),
            ("Austria Wien", "Wolfsberger AC", 1.95, 3.50, 3.60, 1.70, 1.35),
            ("TSV Hartberg", "SCR Altach", 2.05, 3.20, 3.50, 1.45, 1.25),
            ("Austria Klagenfurt", "BW Linz", 2.25, 3.10, 3.10, 1.35, 1.35)
        ]
    },
    "Países Baixos (Eredivisie / Eerste Divisie)": {
        "country": "Países Baixos",
        "league": "Eredivisie",
        "pairs": [
            ("Ajax", "PSV Eindhoven", 2.40, 3.70, 2.60, 2.20, 2.10),
            ("Feyenoord", "AZ Alkmaar", 1.85, 3.75, 3.80, 2.10, 1.45)
        ]
    },
    "Bélgica (Pro League / Challenger Pro League)": {
        "country": "Bélgica",
        "league": "Belgian Pro League",
        "pairs": [
            ("Club Brugge", "Anderlecht", 2.05, 3.40, 3.40, 1.85, 1.50),
            ("Gent", "Genk", 2.20, 3.50, 2.90, 1.95, 1.75)
        ]
    },
    "Turquia (Süper Lig / 1. Lig)": {
        "country": "Turquia",
        "league": "Turkish Süper Lig",
        "pairs": [
            ("Galatasaray", "Fenerbahçe", 2.25, 3.40, 2.95, 1.90, 1.80),
            ("Beşiktaş", "Trabzonspor", 2.10, 3.30, 3.30, 1.75, 1.55)
        ]
    },
    "Argentina (Liga Profesional)": {
        "country": "Argentina",
        "league": "Liga Profesional",
        "pairs": [
            ("Boca Juniors", "River Plate", 2.45, 2.95, 2.95, 1.15, 1.15),
            ("Racing Club", "Independiente", 2.10, 3.00, 3.50, 1.35, 1.15)
        ]
    },
    "EUA / América do Norte (MLS)": {
        "country": "EUA",
        "league": "Major League Soccer",
        "pairs": [
            ("Inter Miami", "LA Galaxy", 1.85, 3.90, 3.60, 2.30, 1.80),
            ("LAFC", "Columbus Crew", 2.10, 3.50, 3.10, 1.90, 1.65)
        ]
    },
    "Suécia (Allsvenskan / Superettan)": {
        "country": "Suécia",
        "league": "Allsvenskan",
        "pairs": [
            ("Malmö FF", "AIK", 1.75, 3.60, 4.40, 1.85, 1.20),
            ("Djurgården", "Hammarby", 2.15, 3.30, 3.20, 1.70, 1.55)
        ]
    },
    "Noruega (Eliteserien / OBOS-ligaen)": {
        "country": "Noruega",
        "league": "Eliteserien",
        "pairs": [
            ("Bodø/Glimt", "Molde", 2.05, 3.60, 3.20, 2.15, 1.70),
            ("Rosenborg", "Vålerenga", 1.90, 3.50, 3.70, 1.80, 1.40)
        ]
    },
    "Dinamarca (Superliga / 1st Division)": {
        "country": "Dinamarca",
        "league": "Danish Superliga",
        "pairs": [
            ("FC Copenhagen", "Midtjylland", 2.10, 3.40, 3.25, 1.75, 1.60),
            ("Brøndby", "Nordsjælland", 2.00, 3.50, 3.40, 1.85, 1.55)
        ]
    },
    "Polónia (Ekstraklasa / 1. Liga)": {
        "country": "Polónia",
        "league": "Ekstraklasa",
        "pairs": [
            ("Legia Warsaw", "Lech Poznań", 2.15, 3.30, 3.20, 1.65, 1.50),
            ("Raków Częstochowa", "Jagiellonia", 1.95, 3.40, 3.70, 1.70, 1.35)
        ]
    },
    "Finlândia (Veikkausliiga / Ykkösliiga)": {
        "country": "Finlândia",
        "league": "Veikkausliiga",
        "pairs": [
            ("HJK Helsinki", "KuPS", 2.00, 3.40, 3.50, 1.75, 1.30),
            ("SJK", "Inter Turku", 2.20, 3.30, 3.10, 1.60, 1.50),
            ("TPS", "FF Jaro", 2.10, 3.20, 3.30, 1.50, 1.40)
        ]
    },
    "Grécia (Super League 1 / Super League 2)": {
        "country": "Grécia",
        "league": "Greek Super League",
        "pairs": [
            ("Olympiacos", "Panathinaikos", 2.05, 3.30, 3.40, 1.70, 1.35),
            ("AEK Atenas", "PAOK", 2.10, 3.20, 3.30, 1.65, 1.45),
            ("Aris", "Kalamata", 1.80, 3.50, 4.20, 1.80, 1.10)
        ]
    },
    "República Checa (Chance Liga / FNL)": {
        "country": "República Checa",
        "league": "Czech First League",
        "pairs": [
            ("Slavia Praga", "Sparta Praga", 2.10, 3.40, 3.20, 1.80, 1.55),
            ("Viktoria Plzen", "Banik Ostrava", 1.90, 3.50, 3.80, 1.85, 1.30)
        ]
    },
    "Roménia (SuperLiga / Liga II)": {
        "country": "Roménia",
        "league": "Romanian SuperLiga",
        "pairs": [
            ("FCSB", "CFR Cluj", 2.15, 3.20, 3.25, 1.60, 1.40),
            ("Universitatea Craiova", "Rapid Bucareste", 2.05, 3.30, 3.35, 1.65, 1.45)
        ]
    },
    "Croácia (HNL / Prva NL)": {
        "country": "Croácia",
        "league": "Croatian HNL",
        "pairs": [
            ("Dinamo Zagreb", "Hajduk Split", 1.95, 3.40, 3.60, 1.85, 1.30),
            ("Rijeka", "Osijek", 2.10, 3.30, 3.25, 1.65, 1.45)
        ]
    },
    "Sérvia (SuperLiga / Prva Liga)": {
        "country": "Sérvia",
        "league": "Serbian SuperLiga",
        "pairs": [
            ("Estrela Vermelha", "Partizan", 1.85, 3.60, 3.90, 2.00, 1.20),
            ("Vojvodina", "TSC Backa Topola", 2.25, 3.20, 3.00, 1.50, 1.60)
        ]
    },
    "Japão (J1 League / J2 League)": {
        "country": "Japão",
        "league": "J1 League",
        "pairs": [
            ("Vissel Kobe", "Yokohama F. Marinos", 2.20, 3.40, 3.00, 1.85, 1.70),
            ("Kawasaki Frontale", "Urawa Red Diamonds", 2.10, 3.30, 3.20, 1.70, 1.50)
        ]
    },
    "México (Liga MX / Liga de Expansión)": {
        "country": "México",
        "league": "Liga MX",
        "pairs": [
            ("Club América", "Guadalajara", 1.95, 3.40, 3.60, 1.80, 1.35),
            ("Tigres UANL", "CF Monterrey", 2.15, 3.30, 3.20, 1.65, 1.50)
        ]
    },
    "Colômbia (Categoría Primera A / Primera B)": {
        "country": "Colômbia",
        "league": "Categoría Primera A",
        "pairs": [
            ("Atlético Nacional", "Millonarios", 2.10, 3.10, 3.40, 1.50, 1.30),
            ("Junior Barranquilla", "América de Cali", 2.00, 3.20, 3.60, 1.60, 1.25)
        ]
    }
}


def infer_country_and_league(home: str, away: str, raw_league: str = "", raw_country: str = "") -> tuple[str, str]:
    """
    Infer accurate country and normalized league name for any match.
    Ensures 'Europa' is ONLY assigned to UEFA international competitions
    (Champions League, Europa League, Conference League, Nations League).
    Domestic teams (e.g. Basel, Servette, Young Boys) are accurately mapped to their actual country (e.g. Suíça).
    """
    home_clean = (home or "").strip().lower()
    away_clean = (away or "").strip().lower()
    league_clean = (raw_league or "").strip().lower()
    country_clean = (raw_country or "").strip().lower()

    # 1. Check if it's explicitly a European UEFA Competition
    if any(k in league_clean for k in ["uefa", "champions league", "europa league", "conference league", "nations league"]):
        return "Europa", raw_league or "UEFA Champions League"

    # 2. Match against LEAGUE_TEAMS_DATABASE by team names or league keywords
    for lkey, ldata in LEAGUE_TEAMS_DATABASE.items():
        cname = str(ldata["country"])
        lname = str(ldata["league"])
        pairs = ldata["pairs"]

        if cname.lower() == country_clean or lname.lower() in league_clean or cname.lower() in league_clean:
            return cname, lname

        if isinstance(pairs, list):
            for p in pairs:
                if len(p) >= 2:
                    h_team, a_team = p[0], p[1]
                    h_norm = h_team.lower()
                    a_norm = a_team.lower()
                    if (h_norm in home_clean or home_clean in h_norm or
                        a_norm in away_clean or away_clean in a_norm):
                        return cname, lname

    # 3. Specific Keyword Matching for countries
    country_kw_map = {
        "Portugal": ["portugal", "betclic", "primeira liga", "segunda liga", "benfica", "porto", "sporting"],
        "Inglaterra": ["inglaterra", "england", "premier league", "championship", "league 1", "epl"],
        "Espanha": ["espanha", "spain", "la liga", "segunda division"],
        "Itália": ["itália", "italy", "serie a", "serie b"],
        "Alemanha": ["alemanha", "germany", "bundesliga"],
        "França": ["frança", "france", "ligue 1", "ligue 2"],
        "Brasil": ["brasil", "brazil", "brasileirão", "brasileirao"],
        "Escócia": ["escócia", "scotland", "scottish", "premiership"],
        "Suíça": ["suíça", "suica", "switzerland", "swiss", "challenge league"],
        "Áustria": ["áustria", "austria", "austrian"],
        "Países Baixos": ["países baixos", "paises baixos", "netherlands", "eredivisie", "holanda"],
        "Bélgica": ["bélgica", "belgica", "belgium", "pro league"],
        "Turquia": ["turquia", "turkey", "süper lig", "super lig"],
        "Argentina": ["argentina", "liga profesional"],
        "EUA": ["eua", "usa", "mls", "major league soccer"],
        "Suécia": ["suécia", "suecia", "sweden", "allsvenskan"],
        "Noruega": ["noruega", "norway", "eliteserien"],
        "Dinamarca": ["dinamarca", "denmark", "superliga"],
        "Polónia": ["polónia", "polonia", "poland", "ekstraklasa"],
        "Finlândia": ["finlândia", "finlandia", "finland", "veikkausliiga"],
        "Grécia": ["grécia", "grecia", "greece"],
        "República Checa": ["república checa", "republica checa", "czech", "chance liga"],
        "Roménia": ["roménia", "romenia", "romania"],
        "Croácia": ["croácia", "croacia", "croatia", "hnl"],
        "Sérvia": ["sérvia", "servia", "serbia"],
        "Japão": ["japão", "japao", "japan", "j1 league"],
        "México": ["méxico", "mexico", "liga mx"],
        "Colômbia": ["colômbia", "colombia", "primera a"]
    }

    combined_text = f"{country_clean} {league_clean} {home_clean} {away_clean}"
    for cname, kws in country_kw_map.items():
        if any(kw in combined_text for kw in kws):
            return cname, raw_league or f"Liga ({cname})"

    if raw_country and raw_country.lower() not in ["world", "internacional", "international", "europa", ""]:
        return raw_country.title(), raw_league or "Liga Desportiva"

    return "Europa", raw_league or "Competição Europeia"

def normalize_team_name(name: str) -> str:
    """
    Normalize team name for strict deduplication across different spellings and providers.
    Strips accents, converts to lowercase, and removes common football noise words/prefixes.
    """
    if not name:
        return ""
    text = unicodedata.normalize('NFD', name)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn').lower().strip()
    
    # Common football noise words & acronyms
    noise_words = {
        "fc", "f.c.", "sl", "s.l.", "cp", "c.p.", "sc", "s.c.", "ac", "a.c.",
        "cd", "c.d.", "cf", "c.f.", "afc", "vfb", "tsv", "fk", "bk", "rb", "ss",
        "club", "clube", "deportivo", "deportes", "sp", "ud", "sd"
    }
    words = text.split()
    filtered = [w for w in words if w not in noise_words]
    if filtered:
        return " ".join(filtered)
    return text


def deduplicate_matches_by_teams(matches: list) -> list:
    """
    Filter matches strictly so that no team (home or away) appears in more than ONE match on the same date.
    Ensures real-world football schedule validity and eliminates duplicate/inverted fixtures.
    """
    if not matches:
        return []

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    today_fmt = datetime.date.today().strftime("%d/%m/%Y")
    
    seen_teams_by_date = {}
    clean_matches = []

    for m in matches:
        if not isinstance(m, dict):
            continue
        home = str(m.get("home", "")).strip()
        away = str(m.get("away", "")).strip()
        m_date = str(m.get("date", today_str)).strip() or today_str

        if not home or not away:
            continue

        h_norm = normalize_team_name(home)
        a_norm = normalize_team_name(away)

        if not h_norm or not a_norm or h_norm == a_norm:
            continue

        if m_date not in seen_teams_by_date:
            seen_teams_by_date[m_date] = set()

        seen_set = seen_teams_by_date[m_date]

        # If either home or away team is ALREADY scheduled on this date, skip match
        if h_norm in seen_set or a_norm in seen_set:
            continue

        seen_set.add(h_norm)
        seen_set.add(a_norm)

        m["date"] = m_date
        if not m.get("date_formatted"):
            m["date_formatted"] = today_fmt

        clean_matches.append(m)

    return clean_matches


def get_matches_for_selected_leagues(selected_countries: Optional[List[str]] = None, max_matches: int = 20) -> list:
    """
    Generate realistic matches strictly for TODAY'S DATE
    covering all selected countries/leagues evenly up to max_matches,
    with strict team uniqueness per date.
    """
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    today_formatted = datetime.date.today().strftime("%d/%m/%Y")

    selected_list = selected_countries or []
    is_all = not selected_countries or "Todas as Ligas/Países" in selected_countries

    if is_all:
        active_keys = list(LEAGUE_TEAMS_DATABASE.keys())
    else:
        active_keys = [c for c in selected_list if c in LEAGUE_TEAMS_DATABASE]
        if not active_keys:
            return []

    raw_matches = []
    per_league_target = max(1, math.ceil(max_matches / len(active_keys)))

    for lkey in active_keys:
        ldata = LEAGUE_TEAMS_DATABASE[lkey]
        cname = str(ldata["country"])
        lname = str(ldata["league"])
        pairs = ldata["pairs"]

        if isinstance(pairs, list):
            for p in pairs[:per_league_target]:
                if len(p) >= 7:
                    home, away = p[0], p[1]
                    o1, ox, o2 = p[2], p[3], p[4]
                    hxg, axg = p[5], p[6]

                    o25 = round(max(1.45, min(2.50, 1.85 - ((hxg + axg - 2.5) * 0.15))), 2)
                    btts = round(max(1.45, min(2.20, 1.80 - (min(hxg, axg) * 0.10))), 2)

                    raw_matches.append({
                        "date": today_str,
                        "date_formatted": today_formatted,
                        "country": cname,
                        "league": lname,
                        "home": home,
                        "away": away,
                        "h_xg": hxg,
                        "a_xg": axg,
                        "h_xga": axg,
                        "a_xga": hxg,
                        "odd_1": o1,
                        "odd_x": ox,
                        "odd_2": o2,
                        "odd_1x": round(1.0 / (1/o1 + 1/ox), 2),
                        "odd_x2": round(1.0 / (1/ox + 1/o2), 2),
                        "odd_o05": 1.05,
                        "odd_o15": 1.25,
                        "odd_o25": o25,
                        "odd_o35": 3.00,
                        "odd_btts_yes": btts,
                        "odd_btts_no": round(1.0 / max(0.01, 1 - 1/btts), 2),
                        "odd_dnb1": round(o1 * 0.75, 2),
                        "odd_dnb2": round(o2 * 0.75, 2),
                        "home_form": "V-E-V-D-V",
                        "away_form": "V-D-V-E-E",
                        "h2h_summary": f"Partida agendada para HOJE ({today_formatted}) na competição {lname}.",
                        "odd": o1 if o1 <= 2.0 else round(1.0 / (1/o1 + 1/ox), 2),
                        "market": "Vitória Casa (1)" if o1 <= 2.0 else "Dupla Hipótese (1X)"
                    })

    # Apply strict team deduplication across all leagues
    clean_matches = deduplicate_matches_by_teams(raw_matches)
    return clean_matches[:max_matches]

DEFAULT_MOCK_MATCHES = get_matches_for_selected_leagues(["Todas as Ligas/Países"], 20)


def _get_secret(key_name: str, default_val: str = "") -> str:
    """Retrieve secret from Streamlit Cloud secrets, environment variable, or fallback default."""
    try:
        if hasattr(st, "secrets") and key_name in st.secrets:
            val = str(st.secrets[key_name]).strip()
            if val:
                return val
    except Exception:
        pass
    return os.environ.get(key_name, default_val)

def init_session_state():
    """Ensure all required session state variables exist and load stored SQLite data."""
    try:
        from database.db import load_matches_from_db, load_analysis_from_db, init_db
        init_db()
        stored_matches = load_matches_from_db()
        stored_analysis = load_analysis_from_db()
    except Exception:
        stored_matches = []
        stored_analysis = []

    defaults = {
        "app_started": False,
        "confirm_exit": False,
        "theme_mode": "light",
        "sidebar_color": "Padrão",
        "matches_data": stored_matches,
        "analysed_results": stored_analysis,
        "live_matches_data": [],
        "h2h_active_result": {},
        "filtered_matches": [],
        "gemini_key": _get_secret("GEMINI_API_KEY", ""),
        "odds_provider": "The Odds API (the-odds-api.com)",
        "odds_api_key": _get_secret("ODDS_API_KEY", ""),
        "api_football_key": _get_secret("API_FOOTBALL_KEY", ""),
        "ngrok_key": _get_secret("NGROK_AUTHTOKEN", ""),
        "email_sender": _get_secret("EMAIL_SENDER", ""),
        "email_password": _get_secret("EMAIL_PASSWORD", ""),
        "is_admin": False,
        "active_tab": "🔍 Obter Jogos (Odds API / OddsPortal / Gemini)",
        "last_ingestion_log": f"Carregados {len(stored_matches)} jogos salvos da base de dados SQLite (bfbetting.db)." if stored_matches else ""
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
        elif key == "matches_data" and not st.session_state["matches_data"] and stored_matches:
            st.session_state["matches_data"] = stored_matches
        elif key == "analysed_results" and not st.session_state["analysed_results"] and stored_analysis:
            st.session_state["analysed_results"] = stored_analysis

