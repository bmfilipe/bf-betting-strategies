import os
import sqlite3
import json
import datetime
from typing import List, Dict, Any, Tuple

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
    """Initialize database tables for ingested matches and analysis results."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_key TEXT UNIQUE,
        home_team TEXT,
        away_team TEXT,
        league TEXT,
        data_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_key TEXT UNIQUE,
        data_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_type TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def save_matches_to_db(matches: List[Dict[str, Any]]) -> bool:
    """Save or update matches list in SQLite database."""
    if not matches:
        return False
    
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        
        for m in matches:
            home = m.get("home", "")
            away = m.get("away", "")
            league = m.get("league", "")
            match_key = f"{home}_vs_{away}_{league}".lower().replace(" ", "_")
            data_json = json.dumps(m, ensure_ascii=False)
            
            cursor.execute("""
            INSERT INTO matches (match_key, home_team, away_team, league, data_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(match_key) DO UPDATE SET
                data_json=excluded.data_json,
                created_at=excluded.created_at
            """, (match_key, home, away, league, data_json, datetime.datetime.now().isoformat()))
            
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
    """Save or update predictive analysis results in SQLite database."""
    if not analysed_results:
        return False
    
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        
        for a in analysed_results:
            match_info = a.get("match", {})
            home = match_info.get("home", "")
            away = match_info.get("away", "")
            league = match_info.get("league", "")
            match_key = f"{home}_vs_{away}_{league}".lower().replace(" ", "_")
            data_json = json.dumps(a, ensure_ascii=False)
            
            cursor.execute("""
            INSERT INTO analysis (match_key, data_json, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(match_key) DO UPDATE SET
                data_json=excluded.data_json,
                created_at=excluded.created_at
            """, (match_key, data_json, datetime.datetime.now().isoformat()))
            
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

def clear_db() -> bool:
    """Clear stored matches and analysis records from SQLite database."""
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM matches")
        cursor.execute("DELETE FROM analysis")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Error clearing database: {e}")
        return False
