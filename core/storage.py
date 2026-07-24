from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "guided_code.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                problem_id TEXT NOT NULL,
                code TEXT NOT NULL,
                status TEXT NOT NULL,
                passed INTEGER NOT NULL,
                total INTEGER NOT NULL,
                mistake_type TEXT NOT NULL,
                hint_level INTEGER NOT NULL DEFAULT 0,
                planning_steps INTEGER NOT NULL DEFAULT 0,
                independence TEXT NOT NULL DEFAULT 'Unrated',
                language TEXT NOT NULL DEFAULT 'python',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS mastery (
                username TEXT NOT NULL,
                tag TEXT NOT NULL,
                score REAL NOT NULL DEFAULT 0,
                attempts INTEGER NOT NULL DEFAULT 0,
                successes INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (username, tag)
            );

            CREATE TABLE IF NOT EXISTS guide_notes (
                username TEXT NOT NULL,
                problem_id TEXT NOT NULL,
                step_index INTEGER NOT NULL,
                note TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (username, problem_id, step_index)
            );

            CREATE TABLE IF NOT EXISTS drafts (
                username TEXT NOT NULL,
                problem_id TEXT NOT NULL,
                code TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (username, problem_id)
            );

            CREATE TABLE IF NOT EXISTS language_drafts (
                username TEXT NOT NULL,
                problem_id TEXT NOT NULL,
                language TEXT NOT NULL,
                code TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (username, problem_id, language)
            );
            """
        )
        attempt_columns = {
            str(row["name"])
            for row in conn.execute("PRAGMA table_info(attempts)").fetchall()
        }
        if "hint_level" not in attempt_columns:
            conn.execute(
                "ALTER TABLE attempts "
                "ADD COLUMN hint_level INTEGER NOT NULL DEFAULT 0"
            )
        if "planning_steps" not in attempt_columns:
            conn.execute(
                "ALTER TABLE attempts "
                "ADD COLUMN planning_steps INTEGER NOT NULL DEFAULT 0"
            )
        if "independence" not in attempt_columns:
            conn.execute(
                "ALTER TABLE attempts "
                "ADD COLUMN independence TEXT NOT NULL DEFAULT 'Unrated'"
            )
        if "language" not in attempt_columns:
            conn.execute(
                "ALTER TABLE attempts "
                "ADD COLUMN language TEXT NOT NULL DEFAULT 'python'"
            )
        conn.execute(
            """
            INSERT OR IGNORE INTO language_drafts
                (username, problem_id, language, code, updated_at)
            SELECT username, problem_id, 'python', code, updated_at
            FROM drafts
            """
        )


def save_attempt(
    username: str,
    problem_id: str,
    code: str,
    result: dict[str, Any],
    mistake_type: str,
    tags: list[str],
    hint_level: int = 0,
    planning_steps: int = 0,
    language: str = "python",
) -> str:
    passed = int(result.get("passed", 0))
    total = int(result.get("total", 0))
    ratio = passed / total if total else 0.0
    success = total > 0 and passed == total and result.get("status") == "completed"
    if not success:
        independence = "In progress"
    elif hint_level == 0:
        independence = "Independent"
    elif hint_level <= 2:
        independence = "Guided"
    else:
        independence = "Assisted"
    now = datetime.now(timezone.utc).isoformat()

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO attempts
            (
                username, problem_id, code, status, passed, total, mistake_type,
                hint_level, planning_steps, independence, language, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                problem_id,
                code,
                result.get("status", "unknown"),
                passed,
                total,
                mistake_type,
                max(0, int(hint_level)),
                max(0, int(planning_steps)),
                independence,
                language,
                now,
            ),
        )

        for tag in tags:
            row = conn.execute(
                "SELECT score, attempts, successes FROM mastery WHERE username = ? AND tag = ?",
                (username, tag),
            ).fetchone()
            old_score = float(row["score"]) if row else 0.0
            attempts = int(row["attempts"]) if row else 0
            successes = int(row["successes"]) if row else 0

            if success:
                new_score = old_score + (100.0 - old_score) * 0.22
            elif ratio > 0:
                target = ratio * 75.0
                new_score = old_score * 0.88 + target * 0.12
            else:
                new_score = max(0.0, old_score - 2.0)

            conn.execute(
                """
                INSERT INTO mastery (username, tag, score, attempts, successes)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(username, tag) DO UPDATE SET
                    score = excluded.score,
                    attempts = excluded.attempts,
                    successes = excluded.successes
                """,
                (username, tag, round(new_score, 2), attempts + 1, successes + int(success)),
            )
    return independence


def save_guide_note(username: str, problem_id: str, step_index: int, note: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO guide_notes (username, problem_id, step_index, note, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(username, problem_id, step_index) DO UPDATE SET
                note = excluded.note,
                updated_at = excluded.updated_at
            """,
            (username, problem_id, step_index, note, now),
        )


def load_guide_notes(username: str, problem_id: str) -> dict[int, str]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT step_index, note FROM guide_notes WHERE username = ? AND problem_id = ?",
            (username, problem_id),
        ).fetchall()
    return {int(row["step_index"]): str(row["note"]) for row in rows}


def save_draft(
    username: str,
    problem_id: str,
    code: str,
    language: str = "python",
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO language_drafts
                (username, problem_id, language, code, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(username, problem_id, language) DO UPDATE SET
                code = excluded.code,
                updated_at = excluded.updated_at
            """,
            (username, problem_id, language, code, now),
        )


def load_draft(
    username: str,
    problem_id: str,
    language: str = "python",
) -> str | None:
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT code
            FROM language_drafts
            WHERE username = ? AND problem_id = ? AND language = ?
            """,
            (username, problem_id, language),
        ).fetchone()
    return str(row["code"]) if row else None


def get_dashboard(username: str) -> dict[str, Any]:
    review_cutoff = (
        datetime.now(timezone.utc) - timedelta(days=3)
    ).isoformat()
    with _connect() as conn:
        totals = conn.execute(
            """
            SELECT
                COUNT(*) AS attempts,
                COUNT(DISTINCT problem_id) AS attempted_problems,
                COUNT(DISTINCT CASE WHEN passed = total AND total > 0 AND status = 'completed' THEN problem_id END) AS solved,
                COUNT(DISTINCT CASE
                    WHEN passed = total
                    AND total > 0
                    AND status = 'completed'
                    AND independence = 'Independent'
                    THEN problem_id
                END) AS independent_solves
            FROM attempts
            WHERE username = ?
            """,
            (username,),
        ).fetchone()
        mastery_rows = conn.execute(
            """
            SELECT tag, score, attempts, successes
            FROM mastery
            WHERE username = ?
            ORDER BY score ASC, attempts DESC, tag ASC
            """,
            (username,),
        ).fetchall()
        recent_rows = conn.execute(
            """
            SELECT
                problem_id, status, passed, total, mistake_type,
                hint_level, planning_steps, independence, language, created_at
            FROM attempts
            WHERE username = ?
            ORDER BY id DESC
            LIMIT 8
            """,
            (username,),
        ).fetchall()
        solved_rows = conn.execute(
            """
            SELECT DISTINCT problem_id
            FROM attempts
            WHERE username = ? AND passed = total AND total > 0 AND status = 'completed'
            """,
            (username,),
        ).fetchall()
        mistake_rows = conn.execute(
            """
            SELECT mistake_type, COUNT(*) AS count
            FROM attempts
            WHERE username = ? AND mistake_type != 'Correct'
            GROUP BY mistake_type
            ORDER BY count DESC
            LIMIT 5
            """,
            (username,),
        ).fetchall()
        review_rows = conn.execute(
            """
            SELECT
                problem_id,
                MAX(created_at) AS last_practiced,
                MAX(
                    CASE
                        WHEN passed = total
                        AND total > 0
                        AND status = 'completed'
                        THEN created_at
                    END
                ) AS last_solved
            FROM attempts
            WHERE username = ?
            GROUP BY problem_id
            HAVING last_solved IS NOT NULL
                AND MAX(created_at) <= ?
            ORDER BY last_practiced ASC
            LIMIT 6
            """,
            (username, review_cutoff),
        ).fetchall()

    return {
        "attempts": int(totals["attempts"] or 0),
        "attempted_problems": int(totals["attempted_problems"] or 0),
        "solved": int(totals["solved"] or 0),
        "independent_solves": int(totals["independent_solves"] or 0),
        "mastery": [dict(row) for row in mastery_rows],
        "recent": [dict(row) for row in recent_rows],
        "mistakes": [dict(row) for row in mistake_rows],
        "review_due": [dict(row) for row in review_rows],
        "solved_ids": [str(row["problem_id"]) for row in solved_rows],
    }


def export_progress(username: str) -> str:
    dashboard = get_dashboard(username)
    dashboard["username"] = username
    dashboard["exported_at"] = datetime.now(timezone.utc).isoformat()
    return json.dumps(dashboard, indent=2)
