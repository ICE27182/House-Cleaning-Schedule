from datetime import datetime, date, timezone
from typing import List, Tuple, Union
from duckdb import connect

from ..db import DB_FILE

TimeLike = datetime | date | str

def _to_iso(ts: TimeLike) -> str:
    if isinstance(ts, datetime):
        return ts.isoformat()
    if isinstance(ts, date):
        return datetime(ts.year, ts.month, ts.day).isoformat()
    return ts  # assume already an ISO string

def get_changelog(
        from_time: TimeLike, 
        to_time: TimeLike | None = None
) -> list[tuple[datetime, str]]:
    """
    Return list of (created_at: datetime, description: str) between from_time and to_time (inclusive).
    from_time / to_time may be datetime, date or ISO-format string. If to_time is None, use now (UTC).
    """
    if to_time is None:
        to_time = datetime.now(timezone.utc)

    from_iso = _to_iso(from_time)
    to_iso = _to_iso(to_time)

    with connect(DB_FILE, read_only=True) as conn:
        rows = conn.execute(
            """
            SELECT created_at, description
            FROM changelog
            WHERE created_at BETWEEN ? AND ?
            ORDER BY created_at DESC
            """,
            (from_iso, to_iso)
        ).fetchall()

    # Ensure created_at is a datetime object
    result: List[Tuple[datetime, str]] = []
    for created_at, desc in rows:
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        result.append((created_at, desc))
    return result

def add_changelog(description: str, time: TimeLike | None) -> None:
    """
    Insert a changelog entry.

    If `time` is None the database default timestamp (current_timestamp) is used.
    If `time` is provided (datetime/date/ISO string) it will be stored as the
    created_at value.
    """
    description = description.strip()
    if not description:
        raise ValueError("description must be a non-empty string")

    with connect(DB_FILE, read_only=False) as conn:
        if time is None:
            # Let DuckDB populate created_at using the table DEFAULT
            conn.execute(
                "INSERT INTO changelog (description) VALUES (?)",
                (description,),
            )
        else:
            created_iso = _to_iso(time)
            conn.execute(
                "INSERT INTO changelog (description, created_at) VALUES (?, ?)",
                (description, created_iso),
            )

