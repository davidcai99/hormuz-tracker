import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

# Use /var/data for persistent storage on Render, fallback to local
RENDER_DISK_PATH = '/var/data'
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'ships.db')

if os.path.exists(RENDER_DISK_PATH) and os.access(RENDER_DISK_PATH, os.W_OK):
    DATABASE_PATH = os.path.join(RENDER_DISK_PATH, 'ships.db')
else:
    DATABASE_PATH = LOCAL_DB_PATH
    os.makedirs(os.path.dirname(LOCAL_DB_PATH), exist_ok=True)

def get_db():
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
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
    """返回总浏览次数（不去重）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM page_views')
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def get_unique_visitors() -> int:
    """返回独立访客数（去重）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(DISTINCT ip_address) FROM page_views')
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def get_data_sources_status() -> List[Dict[str, Any]]:
    """返回数据来源状态列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT source_name, source_url, last_checked, status 
        FROM data_sources 
        ORDER BY last_checked DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_data_source(source_name: str, source_url: str = '', status: str = 'success'):
    """更新数据来源状态"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO data_sources (source_name, source_url, last_checked, status)
        VALUES (?, ?, datetime('now'), ?)
    ''', (source_name, source_url, status))
    conn.commit()
    conn.close()

def get_stats_by_date_range(start_date: str, end_date: str) -> Dict[str, Any]:
    """获取指定日期范围内的统计数据"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取通过船只统计
    cursor.execute('''
        SELECT 
            AVG(passed_count) as avg_passed,
            MAX(passed_count) as max_passed,
            MIN(passed_count) as min_passed,
            AVG(pending_count) as avg_pending,
            MAX(pending_count) as max_pending,
            MIN(pending_count) as min_pending
        FROM daily_ship_data 
        WHERE date BETWEEN ? AND ?
    ''', (start_date, end_date))
    
    stats_row = cursor.fetchone()
    
    # 获取趋势（最近7天 vs 前7天）
    cursor.execute('''
        SELECT AVG(passed_count) as avg_passed FROM daily_ship_data 
        WHERE date >= date('now', '-7 days')
    ''')
    recent_avg = cursor.fetchone()
    
    cursor.execute('''
        SELECT AVG(passed_count) as avg_passed FROM daily_ship_data 
        WHERE date BETWEEN date('now', '-14 days') AND date('now', '-8 days')
    ''')
    previous_avg = cursor.fetchone()
    
    conn.close()
    
    trend = None
    if recent_avg and previous_avg and previous_avg[0]:
        trend = (recent_avg[0] - previous_avg[0]) / previous_avg[0] * 100
    
    return {
        'avg_passed': stats_row[0] if stats_row else None,
        'max_passed': stats_row[1] if stats_row else None,
        'min_passed': stats_row[2] if stats_row else None,
        'avg_pending': stats_row[3] if stats_row else None,
        'max_pending': stats_row[4] if stats_row else None,
        'min_pending': stats_row[5] if stats_row else None,
        'trend_percent': round(trend, 2) if trend else 0
    }
