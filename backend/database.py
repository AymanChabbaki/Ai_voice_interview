"""
PostgreSQL Database Layer – Smart Voice Interviewer
"""

import json
import logging
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, Generator, List, Optional
import os
from dotenv import load_dotenv

import bcrypt
import psycopg2
import psycopg2.extras
import psycopg2.pool
from psycopg2 import IntegrityError

logger = logging.getLogger("smart_interviewer.db")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()
# DATABASE_URL must be set before init_db() is called.
# Format: postgresql://user:password@host:5432/dbname
DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None

# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------

def _init_pool() -> None:
    """Create the thread-safe connection pool.  Called once inside init_db()."""
    global _pool
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Copy .env.example to .env and set DATABASE_URL."
        )
    pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
    _pool = psycopg2.pool.ThreadedConnectionPool(minconn=2, maxconn=pool_size, dsn=DATABASE_URL)
    logger.info("PostgreSQL pool ready (max=%d) → %s", pool_size, DATABASE_URL.split("@")[-1])


@contextmanager
def _get_conn() -> Generator:
    """Borrow a connection from the pool.
    Auto-commits on clean exit; auto-rollbacks and re-raises on exception.
    Always returns the connection to the pool.
    """
    if _pool is None:
        raise RuntimeError("Connection pool not initialised — call init_db() first")
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)


def _fetchone(conn, sql: str, params: tuple = ()) -> Optional[Dict]:
    """Execute *sql* and return a single row as a plain dict, or None."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None


def _fetchall(conn, sql: str, params: tuple = ()) -> List[Dict]:
    """Execute *sql* and return all rows as a list of plain dicts."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


def _execute(conn, sql: str, params: tuple = ()) -> int:
    """Execute *sql* and return rowcount."""
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create all tables (idempotent) and initialise the connection pool."""
    _init_pool()
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id               SERIAL PRIMARY KEY,
                    user_id          TEXT   UNIQUE NOT NULL,
                    username         TEXT   UNIQUE NOT NULL,
                    email            TEXT   UNIQUE NOT NULL,
                    password_hash    TEXT   NOT NULL,
                    name             TEXT   NOT NULL,
                    bio              TEXT,
                    experience_level TEXT   NOT NULL DEFAULT 'Beginner',
                    interests        TEXT,
                    created_at       TEXT   NOT NULL,
                    updated_at       TEXT   NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_stats (
                    id                  SERIAL  PRIMARY KEY,
                    user_id             TEXT    UNIQUE NOT NULL
                                        REFERENCES users(user_id) ON DELETE CASCADE,
                    interview_count     INTEGER NOT NULL DEFAULT 0,
                    total_score         REAL    NOT NULL DEFAULT 0.0,
                    current_streak      INTEGER NOT NULL DEFAULT 0,
                    best_streak         INTEGER NOT NULL DEFAULT 0,
                    last_interview_date TEXT,
                    achievements        TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS interview_history (
                    id              SERIAL  PRIMARY KEY,
                    user_id         TEXT    NOT NULL
                                    REFERENCES users(user_id) ON DELETE CASCADE,
                    session_id      TEXT    NOT NULL,
                    topic           TEXT    NOT NULL,
                    date            TEXT    NOT NULL,
                    pass_rate       REAL    NOT NULL,
                    average_score   REAL    NOT NULL,
                    questions_count INTEGER NOT NULL,
                    passed          INTEGER NOT NULL
                )
            """)
    logger.info("Database schema ready")

# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def create_user(username: str, email: str, password: str, name: str) -> Optional[Dict]:
    """Insert a new user + stats row.  Returns minimal user dict or None on conflict."""
    user_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    try:
        with _get_conn() as conn:
            _execute(
                conn,
                """
                INSERT INTO users (user_id, username, email, password_hash, name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, username, email, _hash_password(password), name, now, now),
            )
            _execute(
                conn,
                "INSERT INTO user_stats (user_id, achievements) VALUES (%s, %s)",
                (user_id, json.dumps([])),
            )
        logger.info("User created: %s", username)
        return {"user_id": user_id, "username": username, "email": email, "name": name}
    except IntegrityError:
        return None

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Return ``{"user_id": …}`` if credentials are valid, else ``None``."""
    with _get_conn() as conn:
        row = _fetchone(
            conn,
            "SELECT user_id, password_hash FROM users WHERE username = %s OR email = %s",
            (username, username),
        )
    if row and _verify_password(password, row["password_hash"]):
        return {"user_id": row["user_id"]}
    return None

def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Return full user data (joined with stats), password hash excluded."""
    with _get_conn() as conn:
        user  = _fetchone(conn, "SELECT * FROM users WHERE user_id = %s", (user_id,))
        if not user:
            return None
        stats = _fetchone(conn, "SELECT * FROM user_stats WHERE user_id = %s", (user_id,))

    data = dict(user)
    data.pop("password_hash", None)
    data["interests"] = json.loads(data.get("interests") or "[]")

    if stats:
        data.update(
            interview_count=stats["interview_count"],
            total_score=stats["total_score"],
            current_streak=stats["current_streak"],
            best_streak=stats["best_streak"],
            last_interview_date=stats["last_interview_date"],
            achievements=json.loads(stats.get("achievements") or "[]"),
        )
    return data

def update_user_profile(user_id: str, data: Dict) -> bool:
    """Update whitelisted profile fields.  Returns True if a row was modified."""
    allowed = {"name", "bio", "experience_level", "interests"}
    fields = {k: v for k, v in data.items() if k in allowed}
    if not fields:
        return False

    if "interests" in fields:
        fields["interests"] = json.dumps(fields["interests"])

    set_clause = ", ".join(f"{col} = %s" for col in fields)
    values = list(fields.values()) + [datetime.utcnow().isoformat(), user_id]

    with _get_conn() as conn:
        rows = _execute(
            conn,
            f"UPDATE users SET {set_clause}, updated_at = %s WHERE user_id = %s",
            tuple(values),
        )
    return rows > 0

# ---------------------------------------------------------------------------
# Interview history
# ---------------------------------------------------------------------------

def add_interview_history(user_id: str, entry: Dict) -> bool:
    """Append a session record.  Returns False if user does not exist."""
    with _get_conn() as conn:
        if not _fetchone(conn, "SELECT 1 FROM users WHERE user_id = %s", (user_id,)):
            return False
        _execute(
            conn,
            """
            INSERT INTO interview_history
                (user_id, session_id, topic, date, pass_rate, average_score, questions_count, passed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                entry["session_id"],
                entry["topic"],
                entry["date"],
                entry["pass_rate"],
                entry["average_score"],
                entry["questions_count"],
                entry["passed"],
            ),
        )
    return True

def get_interview_history(user_id: str, limit: int = 50) -> List[Dict]:
    """Return interview history ordered by most-recent first."""
    with _get_conn() as conn:
        return _fetchall(
            conn,
            "SELECT * FROM interview_history WHERE user_id = %s ORDER BY date DESC LIMIT %s",
            (user_id, limit),
        )

# ---------------------------------------------------------------------------
# Stats & achievements
# ---------------------------------------------------------------------------

_ACHIEVEMENTS = [
    # (id,               count_threshold, rate_threshold, streak_threshold, title,                   description)
    ("first_interview",  1,               None,           None,             "🎉 Getting Started",   "Completed your first interview!"),
    ("ten_interviews",   10,              None,           None,             "🏆 Dedicated Learner", "Completed 10 interviews!"),
    ("fifty_interviews", 50,              None,           None,             "💎 Master Learner",    "Completed 50 interviews!"),
    ("perfect_score",    None,            100.0,          None,             "⭐ Perfect!",           "Achieved 100% pass rate!"),
    ("five_day_streak",  None,            None,           5,                "🔥 On Fire!",           "5-day streak!"),
]

def update_user_stats(user_id: str, stats_update: Dict) -> Optional[List[Dict]]:
    """Increment counters, recalculate streak, award new achievements.
    Returns the list of newly-earned achievements (may be empty), or None if
    the user does not exist.
    The entire read-modify-write is done in a single connection for atomicity.
    """
    with _get_conn() as conn:
        cur = _fetchone(conn, "SELECT * FROM user_stats WHERE user_id = %s", (user_id,))
        if not cur:
            return None

        achievements: List[str] = json.loads(cur.get("achievements") or "[]")
        new_achievements: List[Dict] = []

        count = cur["interview_count"] + 1
        total = cur["total_score"] + stats_update.get("pass_rate", 0)

        # Streak
        today = datetime.utcnow().date()
        last_str = cur.get("last_interview_date")
        if last_str:
            last = datetime.fromisoformat(last_str).date()
            diff = (today - last).days
            if diff == 0:
                streak = cur["current_streak"]
            elif diff == 1:
                streak = cur["current_streak"] + 1
            else:
                streak = 1
        else:
            streak = 1

        best = max(cur["best_streak"], streak)

        # Award achievements
        for aid, cnt_t, rate_t, streak_t, title, desc in _ACHIEVEMENTS:
            if aid in achievements:
                continue
            if cnt_t    is not None and count  != cnt_t:
                continue
            if rate_t   is not None and stats_update.get("pass_rate", 0) < rate_t:
                continue
            if streak_t is not None and streak != streak_t:
                continue
            achievements.append(aid)
            new_achievements.append({"id": aid, "title": title, "description": desc})

        _execute(
            conn,
            """
            UPDATE user_stats
            SET interview_count = %s, total_score = %s, current_streak = %s,
                best_streak = %s, last_interview_date = %s, achievements = %s
            WHERE user_id = %s
            """,
            (count, total, streak, best, today.isoformat(), json.dumps(achievements), user_id),
        )

    logger.debug("Stats updated | user=%s count=%d streak=%d", user_id, count, streak)
    return new_achievements

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully.")

