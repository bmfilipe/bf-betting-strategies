import os
import sqlite3
import json
import datetime
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
        ("h_xg", "REAL"),
        ("a_xg", "REAL"),
        ("h_xga", "REAL"),
        ("a_xga", "REAL"),
        ("odd_1", "REAL"),
        ("odd_x", "REAL"),
        ("odd_2", "REAL"),
        ("odd_o05", "REAL"),
        ("odd_o15", "REAL"),
        ("odd_o25", "REAL"),
        ("odd_btts_yes", "REAL"),
        ("odd_btts_no", "REAL"),
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
    """Save or update matches list in relational SQLite database."""
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
            match_key = f"{home}_vs_{away}_{league}".lower().replace(" ", "_")
            data_json = json.dumps(m, ensure_ascii=False)
            
            cursor.execute("""
            INSERT INTO matches (
                match_key, country, league, home_team, away_team,
                h_xg, a_xg, h_xga, a_xga,
                odd_1, odd_x, odd_2, odd_o05, odd_o15, odd_o25,
                odd_btts_yes, odd_btts_no, home_form, away_form, h2h_summary,
                provider, data_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(match_key) DO UPDATE SET
                country=excluded.country,
                league=excluded.league,
                h_xg=excluded.h_xg,
                a_xg=excluded.a_xg,
                h_xga=excluded.h_xga,
                a_xga=excluded.a_xga,
                odd_1=excluded.odd_1,
                odd_x=excluded.odd_x,
                odd_2=excluded.odd_2,
                odd_o25=excluded.odd_o25,
                odd_btts_yes=excluded.odd_btts_yes,
                odd_btts_no=excluded.odd_btts_no,
                data_json=excluded.data_json,
                created_at=excluded.created_at
            """, (
                match_key, country, league, home, away,
                float(m.get("h_xg", 1.5) or 1.5), float(m.get("a_xg", 1.0) or 1.0),
                float(m.get("h_xga", 1.0) or 1.0), float(m.get("a_xga", 1.5) or 1.5),
                float(m.get("odd_1", 1.5) or 1.5), float(m.get("odd_x", 3.5) or 3.5), float(m.get("odd_2", 4.0) or 4.0),
                float(m.get("odd_o05", 1.05) or 1.05), float(m.get("odd_o15", 1.25) or 1.25), float(m.get("odd_o25", 1.8) or 1.8),
                float(m.get("odd_btts_yes", 1.75) or 1.75), float(m.get("odd_btts_no", 1.95) or 1.95),
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
    """Retrieve all stored matches from SQLite database."""
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM matches ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        
        matches = []
        for r in rows:
            try:
                matches.append(json.loads(r["data_json"]))
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
        """, (key, str(value), category, datetime.datetime.now().isoformat()))
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
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Error clearing database: {e}")
        return False
