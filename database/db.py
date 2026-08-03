import os
import sqlite3
import json
import datetime
import csv
import io
from typing import List, Dict, Any, Tuple, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
DB_PATH = os.path.join(DB_DIR, "bfbetting.db")

def get_connection():
    """Establish and return connection to SQLite database."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize relational SQLite database schema with indexes."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Matches Table
    cursor.execute("""
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
    )
    """)
    
    # Auto-migration for existing database tables missing columns
    cursor.execute("PRAGMA table_info(matches)")
    existing_cols = [row["name"] for row in cursor.fetchall()]
    cols_to_add = [
        ("country", "TEXT"),
        ("league", "TEXT"),
        ("home_team", "TEXT"),
        ("away_team", "TEXT"),
        ("match_date", "TEXT"),
        ("date_formatted", "TEXT"),
        ("h_xg", "REAL"),
        ("a_xg", "REAL"),
        ("h_xga", "REAL"),
        ("a_xga", "REAL"),
        ("odd_1", "REAL"),
        ("odd_x", "REAL"),
        ("odd_2", "REAL"),
        ("odd_1x", "REAL"),
        ("odd_x2", "REAL"),
        ("odd_o05", "REAL"),
        ("odd_o15", "REAL"),
        ("odd_o25", "REAL"),
        ("odd_o35", "REAL"),
        ("odd_btts_yes", "REAL"),
        ("odd_btts_no", "REAL"),
        ("odd_dnb1", "REAL"),
        ("odd_dnb2", "REAL"),
        ("market", "TEXT"),
        ("odd", "REAL"),
        ("home_form", "TEXT"),
        ("away_form", "TEXT"),
        ("h2h_summary", "TEXT"),
        ("provider", "TEXT")
    ]
    for col_name, col_type in cols_to_add:
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE matches ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass

    # Indexes for fast search
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches(home_team, away_team)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_league ON matches(country, league)")

    # 2. Evaluations Table (+EV Analysis)
    cursor.execute("""
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
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_eval_ev ON evaluations(ev_percent)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_eval_strategy ON evaluations(strategy_group)")

    # 3. Bet Slips Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bet_slips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slip_name TEXT,
        strategy_type TEXT,
        total_odd REAL,
        matches_count INTEGER,
        data_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 4. App Settings Vault Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_settings (
        key_name TEXT PRIMARY KEY,
        key_value TEXT,
        category TEXT DEFAULT 'GENERAL',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 5. Ingestion Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingestion_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT,
        status TEXT,
        message TEXT,
        matches_count INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 6. Live Matches Table (In-Play)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS live_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_key TEXT UNIQUE NOT NULL,
        country TEXT,
        league TEXT,
        home_team TEXT NOT NULL,
        away_team TEXT NOT NULL,
        score_home INTEGER DEFAULT 0,
        score_away INTEGER DEFAULT 0,
        minute INTEGER DEFAULT 0,
        status TEXT DEFAULT '1H',
        odd_1 REAL,
        odd_x REAL,
        odd_2 REAL,
        provider TEXT DEFAULT 'API-Football Live',
        data_json TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_live_status ON live_matches(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_live_teams ON live_matches(home_team, away_team)")

    # 7. Team H2H History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS team_h2h_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        h2h_key TEXT UNIQUE NOT NULL,
        team_a TEXT NOT NULL,
        team_b TEXT NOT NULL,
        total_matches INTEGER DEFAULT 0,
        team_a_wins INTEGER DEFAULT 0,
        team_b_wins INTEGER DEFAULT 0,
        draws INTEGER DEFAULT 0,
        avg_goals REAL DEFAULT 0.0,
        data_json TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_h2h_key ON team_h2h_history(h2h_key)")

    # 8. Team Stats Cache Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS team_stats_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_name TEXT UNIQUE NOT NULL,
        country TEXT,
        league TEXT,
        data_json TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Backward compatibility fallback tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_key TEXT UNIQUE,
        data_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def save_matches_to_db(matches: List[Dict[str, Any]], provider: str = "The Odds API") -> bool:
    """Save or update matches list in relational SQLite database with strict team uniqueness per date."""
    if not matches:
        return False
    
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    today_fmt = datetime.date.today().strftime("%d/%m/%Y")
    
    try:
        from config import normalize_team_name
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        
        seen_teams_by_date = {}

        for m in matches:
            home = str(m.get("home", "")).strip()
            away = str(m.get("away", "")).strip()
            country = str(m.get("country", "")).strip()
            league = str(m.get("league", "")).strip()
            match_date = str(m.get("date", today_str)).strip() or today_str
            date_formatted = str(m.get("date_formatted", today_fmt)).strip() or today_fmt

            if not home or not away:
                continue

            h_norm = normalize_team_name(home)
            a_norm = normalize_team_name(away)

            if not h_norm or not a_norm or h_norm == a_norm:
                continue

            if match_date not in seen_teams_by_date:
                seen_teams_by_date[match_date] = set()

            seen_set = seen_teams_by_date[match_date]

            if h_norm in seen_set or a_norm in seen_set:
                continue

            seen_set.add(h_norm)
            seen_set.add(a_norm)

            m["date"] = match_date
            m["date_formatted"] = date_formatted

            match_key = f"{home}_vs_{away}_{league}".lower().replace(" ", "_")
            data_json = json.dumps(m, ensure_ascii=False)
            
            cursor.execute("""
            INSERT INTO matches (
                match_key, country, league, home_team, away_team,
                match_date, date_formatted,
                h_xg, a_xg, h_xga, a_xga,
                odd_1, odd_x, odd_2, odd_1x, odd_x2,
                odd_o05, odd_o15, odd_o25, odd_o35,
                odd_btts_yes, odd_btts_no, odd_dnb1, odd_dnb2,
                market, odd, home_form, away_form, h2h_summary,
                provider, data_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(match_key) DO UPDATE SET
                country=excluded.country,
                league=excluded.league,
                match_date=excluded.match_date,
                date_formatted=excluded.date_formatted,
                h_xg=excluded.h_xg,
                a_xg=excluded.a_xg,
                h_xga=excluded.h_xga,
                a_xga=excluded.a_xga,
                odd_1=excluded.odd_1,
                odd_x=excluded.odd_x,
                odd_2=excluded.odd_2,
                odd_1x=excluded.odd_1x,
                odd_x2=excluded.odd_x2,
                odd_o25=excluded.odd_o25,
                odd_o35=excluded.odd_o35,
                odd_btts_yes=excluded.odd_btts_yes,
                odd_btts_no=excluded.odd_btts_no,
                odd_dnb1=excluded.odd_dnb1,
                odd_dnb2=excluded.odd_dnb2,
                market=excluded.market,
                odd=excluded.odd,
                data_json=excluded.data_json,
                created_at=excluded.created_at
            """, (
                match_key, country, league, home, away,
                match_date, date_formatted,
                float(m.get("h_xg", 1.5) or 1.5), float(m.get("a_xg", 1.0) or 1.0),
                float(m.get("h_xga", 1.0) or 1.0), float(m.get("a_xga", 1.5) or 1.5),
                float(m.get("odd_1", 1.5) or 1.5), float(m.get("odd_x", 3.5) or 3.5), float(m.get("odd_2", 4.0) or 4.0),
                float(m.get("odd_1x", 1.25) or 1.25), float(m.get("odd_x2", 1.85) or 1.85),
                float(m.get("odd_o05", 1.05) or 1.05), float(m.get("odd_o15", 1.25) or 1.25), float(m.get("odd_o25", 1.8) or 1.8),
                float(m.get("odd_o35", 3.0) or 3.0),
                float(m.get("odd_btts_yes", 1.75) or 1.75), float(m.get("odd_btts_no", 1.95) or 1.95),
                float(m.get("odd_dnb1", 1.2) or 1.2), float(m.get("odd_dnb2", 3.0) or 3.0),
                str(m.get("market", "")), float(m.get("odd", 1.5) or 1.5),
                str(m.get("home_form", "")), str(m.get("away_form", "")), str(m.get("h2h_summary", "")),
                provider, data_json, datetime.datetime.now().isoformat()
            ))
            
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Error saving matches: {e}")
        return False

def load_matches_from_db() -> List[Dict[str, Any]]:
    """Retrieve stored matches from SQLite database with strict team uniqueness per date."""
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    today_fmt = datetime.date.today().strftime("%d/%m/%Y")
    try:
        from config import normalize_team_name
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM matches ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        
        matches = []
        seen_teams_by_date = {}

        for r in rows:
            try:
                m = json.loads(r["data_json"])
                home = str(m.get("home", "")).strip()
                away = str(m.get("away", "")).strip()
                m_date = str(m.get("date", today_str)).strip() or today_str
                m_fmt = str(m.get("date_formatted", today_fmt)).strip() or today_fmt

                # Strict date checking: only load matches belonging to TODAY
                if m_date[:10] != today_str and m_fmt != today_fmt:
                    continue

                if not home or not away:
                    continue

                h_norm = normalize_team_name(home)
                a_norm = normalize_team_name(away)

                if not h_norm or not a_norm or h_norm == a_norm:
                    continue

                if m_date not in seen_teams_by_date:
                    seen_teams_by_date[m_date] = set()

                seen_set = seen_teams_by_date[m_date]

                if h_norm in seen_set or a_norm in seen_set:
                    continue

                seen_set.add(h_norm)
                seen_set.add(a_norm)

                m["date"] = today_str
                m["date_formatted"] = today_fmt
                matches.append(m)
            except Exception:
                pass
        return matches
    except Exception as e:
        print(f"[DB ERROR] Error loading matches: {e}")
        return []

def save_analysis_to_db(analysed_results: List[Dict[str, Any]]) -> bool:
    """Save or update predictive analysis results in relational SQLite database."""
    if not analysed_results:
        return False
    
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        
        for a in analysed_results:
            match_name = str(a.get("Jogo", "")).strip()
            market = str(a.get("Mercado", "")).strip()
            strategy_group = str(a.get("EstratégiaGrupo", "")).strip()
            country = str(a.get("País", "")).strip()
            league = str(a.get("Liga", "")).strip()
            match_key = f"{match_name}_{league}".lower().replace(" ", "_")
            data_json = json.dumps(a, ensure_ascii=False)
            
            cursor.execute("""
            INSERT INTO evaluations (
                match_key, match_name, country, league, strategy_group, market,
                odd, implied_prob, estimated_prob, ev_percent,
                exp_goals_home, exp_goals_away, data_json, evaluated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(match_key, market) DO UPDATE SET
                odd=excluded.odd,
                implied_prob=excluded.implied_prob,
                estimated_prob=excluded.estimated_prob,
                ev_percent=excluded.ev_percent,
                data_json=excluded.data_json,
                evaluated_at=excluded.evaluated_at
            """, (
                match_key, match_name, country, league, strategy_group, market,
                float(a.get("Odd", 1.0) or 1.0),
                float(a.get("Prob. Implícita (%)", 50.0) or 50.0),
                float(a.get("Prob. Estimada (%)", 50.0) or 50.0),
                float(a.get("Expected Value (+EV) (%)", 0.0) or 0.0),
                float(a.get("ExpGoalsHome", 1.5) or 1.5),
                float(a.get("ExpGoalsAway", 1.0) or 1.0),
                data_json, datetime.datetime.now().isoformat()
            ))

            # Also save to legacy analysis table for backward compatibility
            cursor.execute("""
            INSERT INTO analysis (match_key, data_json, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(match_key) DO UPDATE SET
                data_json=excluded.data_json,
                created_at=excluded.created_at
            """, (f"{match_key}_{market}", data_json, datetime.datetime.now().isoformat()))
            
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Error saving analysis: {e}")
        return False

def load_analysis_from_db() -> List[Dict[str, Any]]:
    """Retrieve all stored analysis results from SQLite database."""
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM evaluations ORDER BY id ASC")
        rows = cursor.fetchall()
        if not rows:
            cursor.execute("SELECT data_json FROM analysis ORDER BY id ASC")
            rows = cursor.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            try:
                results.append(json.loads(r["data_json"]))
            except Exception:
                pass
        return results
    except Exception as e:
        print(f"[DB ERROR] Error loading analysis: {e}")
        return []

def save_setting(key: str, value: str, category: str = "GENERAL") -> bool:
    """Save an application configuration setting into SQLite app_settings table."""
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO app_settings (key_name, key_value, category, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(key_name) DO UPDATE SET
            key_value=excluded.key_value,
            category=excluded.category,
            updated_at=excluded.updated_at
        """, (key, value, category, datetime.datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Error saving setting '{key}': {e}")
        return False

def load_settings() -> Dict[str, str]:
    """Retrieve all settings stored in SQLite app_settings table."""
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT key_name, key_value FROM app_settings")
        rows = cursor.fetchall()
        conn.close()
        return {r["key_name"]: r["key_value"] for r in rows}
    except Exception as e:
        print(f"[DB ERROR] Error loading settings: {e}")
        return {}

def export_settings_json() -> str:
    """Export complete application configuration into a JSON string."""
    init_db()
    settings = load_settings()
    export_payload = {
        "app": "BF Analista de Futebol",
        "version": "2.5.0",
        "exported_at": datetime.datetime.now().isoformat(),
        "settings": settings
    }
    return json.dumps(export_payload, indent=2, ensure_ascii=False)

def import_settings_json(json_str: str) -> Tuple[bool, str]:
    """Import application configuration from a JSON string into SQLite app_settings."""
    try:
        data = json.loads(json_str)
        if not isinstance(data, dict) or "settings" not in data:
            return False, "Formato JSON inválido. Ficheiro deve conter a chave 'settings'."
        
        settings = data["settings"]
        if not isinstance(settings, dict):
            return False, "Estrutura 'settings' deve ser um dicionário de chave-valor."

        count = 0
        for k, v in settings.items():
            save_setting(k, str(v), category="IMPORTED")
            count += 1

        return True, f"Configurações importadas com sucesso! {count} definições restauradas."
    except Exception as e:
        return False, f"Erro ao importar JSON: {str(e)}"

def clear_db() -> bool:
    """Clear stored matches, evaluations, and analysis records from SQLite database."""
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM matches")
        cursor.execute("DELETE FROM evaluations")
        cursor.execute("DELETE FROM analysis")
        cursor.execute("DELETE FROM bet_slips")
        cursor.execute("DELETE FROM live_matches")
        cursor.execute("DELETE FROM team_h2h_history")
        cursor.execute("DELETE FROM team_stats_cache")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Error clearing database: {e}")
        return False

def save_live_matches_to_db(matches: List[Dict[str, Any]], provider: str = "API-Football Live") -> bool:
    """Save or update live (in-play) matches in SQLite database."""
    if not matches:
        return False
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        for m in matches:
            home = str(m.get("home", "")).strip()
            away = str(m.get("away", "")).strip()
            country = str(m.get("country", "")).strip()
            league = str(m.get("league", "")).strip()
            match_key = f"live_{home}_vs_{away}_{league}".lower().replace(" ", "_")
            data_json = json.dumps(m, ensure_ascii=False)
            
            cursor.execute("""
            INSERT INTO live_matches (
                match_key, country, league, home_team, away_team,
                score_home, score_away, minute, status,
                odd_1, odd_x, odd_2, provider, data_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(match_key) DO UPDATE SET
                score_home=excluded.score_home,
                score_away=excluded.score_away,
                minute=excluded.minute,
                status=excluded.status,
                odd_1=excluded.odd_1,
                odd_x=excluded.odd_x,
                odd_2=excluded.odd_2,
                data_json=excluded.data_json,
                updated_at=excluded.updated_at
            """, (
                match_key, country, league, home, away,
                int(m.get("score_home", 0) or 0), int(m.get("score_away", 0) or 0),
                int(m.get("minute", 0) or 0), str(m.get("status", "1H")),
                float(m.get("odd_1", 2.0) or 2.0), float(m.get("odd_x", 3.0) or 3.0), float(m.get("odd_2", 3.5) or 3.5),
                provider, data_json, datetime.datetime.now().isoformat()
            ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Error saving live matches: {e}")
        return False

def load_live_matches_from_db() -> List[Dict[str, Any]]:
    """Retrieve all stored live matches from SQLite database."""
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM live_matches ORDER BY minute DESC, id DESC")
        rows = cursor.fetchall()
        conn.close()
        results = []
        for r in rows:
            try:
                results.append(json.loads(r["data_json"]))
            except Exception:
                pass
        return results
    except Exception as e:
        print(f"[DB ERROR] Error loading live matches: {e}")
        return []

def save_h2h_history_to_db(h2h_data: Dict[str, Any]) -> bool:
    """Save team comparison and H2H history data into SQLite database."""
    if not h2h_data or "team_a" not in h2h_data or "team_b" not in h2h_data:
        return False
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        
        team_a = str(h2h_data["team_a"]).strip()
        team_b = str(h2h_data["team_b"]).strip()
        h2h_key = f"h2h_{team_a}_vs_{team_b}".lower().replace(" ", "_")
        data_json = json.dumps(h2h_data, ensure_ascii=False)
        
        cursor.execute("""
        INSERT INTO team_h2h_history (
            h2h_key, team_a, team_b, total_matches,
            team_a_wins, team_b_wins, draws, avg_goals, data_json, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(h2h_key) DO UPDATE SET
            total_matches=excluded.total_matches,
            team_a_wins=excluded.team_a_wins,
            team_b_wins=excluded.team_b_wins,
            draws=excluded.draws,
            avg_goals=excluded.avg_goals,
            data_json=excluded.data_json,
            updated_at=excluded.updated_at
        """, (
            h2h_key, team_a, team_b,
            int(h2h_data.get("total_matches", 0)),
            int(h2h_data.get("team_a_wins", 0)),
            int(h2h_data.get("team_b_wins", 0)),
            int(h2h_data.get("draws", 0)),
            float(h2h_data.get("avg_goals", 0.0)),
            data_json, datetime.datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Error saving H2H history: {e}")
        return False

def load_h2h_history_from_db(team_a: str, team_b: str) -> Optional[Dict[str, Any]]:
    """Retrieve H2H history for a pair of teams from SQLite database."""
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        key1 = f"h2h_{team_a.strip()}_vs_{team_b.strip()}".lower().replace(" ", "_")
        key2 = f"h2h_{team_b.strip()}_vs_{team_a.strip()}".lower().replace(" ", "_")
        
        cursor.execute("SELECT data_json FROM team_h2h_history WHERE h2h_key IN (?, ?) ORDER BY id DESC LIMIT 1", (key1, key2))
        row = cursor.fetchone()
        conn.close()
        if row and row["data_json"]:
            return json.loads(row["data_json"])
        return None
    except Exception as e:
        print(f"[DB ERROR] Error loading H2H history: {e}")
        return None

def get_db_tables_stats() -> Dict[str, int]:
    """Get total row counts for all tables in bfbetting.db."""
    tables = ["matches", "evaluations", "bet_slips", "live_matches", "team_h2h_history", "team_stats_cache", "app_settings", "ingestion_logs"]
    stats = {}
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        for t in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as cnt FROM {t}")
                res = cursor.fetchone()
                stats[t] = res["cnt"] if res else 0
            except Exception:
                stats[t] = 0
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] Error fetching table stats: {e}")
    return stats

def clear_specific_table(table_name: str) -> bool:
    """Clear all records from a specific table in SQLite database."""
    allowed_tables = ["matches", "evaluations", "bet_slips", "live_matches", "team_h2h_history", "team_stats_cache", "ingestion_logs"]
    if table_name not in allowed_tables:
        return False
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Error clearing table {table_name}: {e}")
        return False

def export_table_to_csv(table_name: str) -> str:
    """Export a database table contents as a CSV formatted string."""
    allowed_tables = ["matches", "evaluations", "bet_slips", "live_matches", "team_h2h_history", "team_stats_cache", "app_settings", "ingestion_logs"]
    if table_name not in allowed_tables:
        return ""
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        if not rows:
            conn.close()
            return f"Tabela '{table_name}' está vazia."
        
        output = io.StringIO()
        columns = rows[0].keys()
        writer = csv.writer(output)
        writer.writerow(columns)
        for r in rows:
            writer.writerow([r[c] for c in columns])
        conn.close()
        return output.getvalue()
    except Exception as e:
        print(f"[DB ERROR] Error exporting table {table_name} to CSV: {e}")
        return ""

def export_table_to_json(table_name: str) -> str:
    """Export a database table contents as a JSON string."""
    allowed_tables = ["matches", "evaluations", "bet_slips", "live_matches", "team_h2h_history", "team_stats_cache", "app_settings", "ingestion_logs"]
    if table_name not in allowed_tables:
        return "{}"
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        conn.close()
        
        result_list = []
        for r in rows:
            row_dict = {}
            for col in r.keys():
                val = r[col]
                row_dict[col] = val
            result_list.append(row_dict)
            
        export_payload = {
            "table": table_name,
            "exported_at": datetime.datetime.now().isoformat(),
            "count": len(result_list),
            "rows": result_list
        }
        return json.dumps(export_payload, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[DB ERROR] Error exporting table {table_name} to JSON: {e}")
        return "{}"

def restore_db_file(file_bytes: bytes) -> Tuple[bool, str]:
    """Replace current SQLite database file with uploaded bytes."""
    try:
        if not file_bytes or len(file_bytes) < 100:
            return False, "Ficheiro inválido ou demasiado pequeno."
        
        # Verify SQLite header signature
        if not file_bytes.startswith(b"SQLite format 3"):
            return False, "O ficheiro fornecido não é uma base de dados SQLite3 válida."

        db_dir = os.path.dirname(DB_PATH)
        os.makedirs(db_dir, exist_ok=True)
        with open(DB_PATH, "wb") as f:
            f.write(file_bytes)
        
        init_db()
        return True, "Base de dados bfbetting.db restaurada com sucesso!"
    except Exception as e:
        return False, f"Erro ao restaurar base de dados: {str(e)}"

