# Saves every finished interview and coding round so progress can be shown over time.
# Uses SQLite from Python's standard library, so there is nothing new to install.

import os
import sqlite3
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                kind       TEXT    NOT NULL,
                label      TEXT    NOT NULL,
                score      INTEGER NOT NULL,
                verdict    TEXT    NOT NULL,
                created_at INTEGER NOT NULL
            )
            """
        )


def verdict_for(score):
    if score >= 75:
        return "Hire"
    if score >= 55:
        return "Borderline"
    return "Needs work"


def add_session(kind, label, score, verdict=None):
    score = max(0, min(100, int(round(score))))
    with _connect() as conn:
        conn.execute(
            "INSERT INTO sessions (kind, label, score, verdict, created_at) VALUES (?, ?, ?, ?, ?)",
            (kind, str(label)[:80], score, verdict or verdict_for(score), int(time.time())),
        )


def list_sessions(limit=200):
    """Oldest first, so the chart reads left to right."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, kind, label, score, verdict, created_at FROM sessions "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]