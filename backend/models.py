import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

DATABASE_PATH = '../database/ships.db'

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 船只每日数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_ship_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE UNIQUE NOT NULL,
            passed_count INTEGER DEFAULT 0,
            pending_count INTEGER DEFAULT 0,
            source TEXT DEFAULT 'unknown',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 访问记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            user_agent TEXT,
            visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 数据来源记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            source_url TEXT,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully")

def insert_ship_data(date: str, passed: int, pending: int, source: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO daily_ship_data (date, passed_count, pending_count, source)
        VALUES (?, ?, ?, ?)
    ''', (date, passed, pending, source))
    conn.commit()
    conn.close()

def get_latest_data() -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM daily_ship_data 
        ORDER BY date DESC LIMIT 1
    ''')
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_historical_data(days: int = 30) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM daily_ship_data 
        ORDER BY date DESC 
        LIMIT ?
    ''', (days,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def record_visit(ip_address: str, user_agent: str = ''):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO page_views (ip_address, user_agent)
        VALUES (?, ?)
    ''', (ip_address, user_agent))
    conn.commit()
    conn.close()

def get_total_views() -> int:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(DISTINCT ip_address) FROM page_views')
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def get_unique_visitors() -> int:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(DISTINCT ip_address) FROM page_views')
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0
