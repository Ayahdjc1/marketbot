# database.py

import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from config import DB_PATH

logger = logging.getLogger(__name__)

def connect_db() -> sqlite3.Connection:
    """Создаёт подключение к SQLite-базе с ожиданием при блокировке"""
    return sqlite3.connect(DB_PATH, timeout=10)


def execute_query(query: str, params: tuple = (), commit: bool = False) -> Optional[List[Tuple]]:
    """Выполняет SQL-запрос с параметрами"""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if commit:
            conn.commit()
        if query.strip().upper().startswith("SELECT"):
            return cursor.fetchall()
        return []
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"SQL error: {e}", exc_info=True)
        raise RuntimeError(f"Database error: {str(e)}") from e
    finally:
        conn.close()

def create_engagement_table() -> None:
    """Создаёт таблицу вовлеченности (если не существует)"""
    query = """
    CREATE TABLE IF NOT EXISTS engagement_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id TEXT NOT NULL UNIQUE,
        likes INTEGER DEFAULT 0 CHECK(likes >= 0),
        comments INTEGER DEFAULT 0 CHECK(comments >= 0),
        shares INTEGER DEFAULT 0 CHECK(shares >= 0),
        date TEXT NOT NULL,
        channel TEXT NOT NULL
    )
    """
    execute_query(query, commit=True)
    logger.info("Таблица engagement_data инициализирована")
    
def create_user_table():
    qery = """
    CREATE TABLE IF NOT EXISTS user_test(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        message TEXT
        );
    """
    execute_query(qery, commit=True)
    logger.info("Таблица user_table инициализирована")
    
def insert_engagement_data(
    post_id: str,
    likes: int,
    comments: int,
    shares: int,
    channel: str,
    date: str = None
) -> None:
    """Вставляет запись о вовлечённости с валидацией"""
    if any(not isinstance(val, int) or val < 0 for val in [likes, comments, shares]):
        raise ValueError("Значения должны быть неотрицательными целыми числами")
    
    date = date or datetime.utcnow().isoformat()
    query = """
    INSERT OR REPLACE INTO engagement_data 
    (post_id, likes, comments, shares, date, channel)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    execute_query(query, (post_id, likes, comments, shares, date, channel), commit=True)
    logger.debug(f"Данные добавлены: post_id={post_id}")

def get_engagement_data_by_range(
    start_date: str, 
    end_date: str, 
    channel: Optional[str] = None
) -> List[Tuple]:
    """
    Возвращает данные за диапазон дат (включительно).
    Формат даты: ISO 8601 (YYYY-MM-DDTHH:MM:SS)
    """
    sql = """
    SELECT id, post_id, likes, comments, shares, date, channel 
    FROM engagement_data 
    WHERE date BETWEEN ? AND ?
    ORDER BY date ASC
    """
    params = [f"{start_date}T00:00:00", f"{end_date}T23:59:59.999"]
    
    if channel:
        sql += " AND channel = ?"
        params.append(channel)
    
    return execute_query(sql, tuple(params))

# database.py (исправленный SQL-запрос)
def get_engagement_data(period: str = "daily", channel: Optional[str] = None) -> List[Tuple]:
    """Возвращает данные за период с возможностью фильтрации по каналу"""
    period_mapping = {
        "daily": ("-1 days", "day"),
        "week": ("-7 days", "week"),
        "month": ("-30 days", "month"),
        "year": ("-1 years", "year")
    }
    
    if period not in period_mapping:
        raise ValueError(f"Недопустимый период: {period}")
    
    interval, _ = period_mapping[period]
    sql = f"""
    SELECT id, post_id, likes, comments, shares, date, channel 
    FROM engagement_data 
    WHERE date >= datetime('now', ?)
    {"AND channel = ?" if channel else ""}
    ORDER BY date ASC
    """
    params = [interval]
    
    if channel:
        params.append(channel)
    
    return execute_query(sql, tuple(params))
