from __future__ import annotations

from .people import get_people
from .chores import get_all_chores, Chore
from duckdb import DuckDBPyConnection
from re import compile
from typing import Literal, override, ClassVar
from dataclasses import dataclass
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import date, timedelta
from random import seed, shuffle
from bisect import bisect_left
from operator import itemgetter

PERIODICALLY = compile(r"^Once per (?:(\d+) )?weeks?\s*(?:on ([a-zA-Z]+day) )?(?:with offset (\d+))?$")
SPECIFICALLY = compile(r"^Weeks (?:on ([A-Z][a-zA-Z]+day) )?in (\d{4}):((?: \d+)+)$")
MAX_WEEKS_FROM_NOW: int = 30 # Must be positive

class ChoreNoFoundError(Exception): pass

def get_due_str_for_chores(
    conn: DuckDBPyConnection, 
    chores: Iterable[str], 
    year: int, 
    week: int,
) -> dict[str, str]:
    """
    Retrieves the due dates for a list of chores and formats them 
    into a dictionary mapping chore names to the due dates.
    """
    results = {}
    for chore_name in chores:
        # Fetch the frequency string from the database for the given chore
        frequency_str = conn.execute(
            "SELECT frequency FROM chores WHERE name = ?",
            (chore_name, ),
        ).fetchone()
        if frequency_str is None:
            raise ValueError(f"Chore {repr(chore_name)} no found")
        frequency_str = frequency_str[0]
        # Create a Frequency object from the string
        frequency_obj = Frequency.from_str(frequency_str)
        # Get the formatted due date string and add it to the results
        due_str = frequency_obj.get_due_str(year, week)
        results[chore_name] = due_str
    return results

@dataclass(slots=True)
class Frequency(ABC):
    """
    Attributes:
        day (int): 0 if it can be any day in the week; 1 is Monday
            and 7 is Sunday.
    """
    DAY_NAME_MAPPING: ClassVar[tuple[str]] = (None, "Monday", "Tuesday",
                                              "Wednesday", "Thursday",
                                              "Friday", "Saturday",
                                              "Sunday")
    NAME_DAY_MAPPING: ClassVar[dict[str, int]] = {"Monday": 1, 
                                                  "Tuesday": 2,
                                                  "Wednesday": 3, 
                                                  "Thursday": 4,
                                                  "Friday": 5, 
                                                  "Saturday": 6,
                                                  "Sunday": 7}
    day: int
    def get_due_str(self, year: int, week: int) -> str:
        if self.day:
            due_date = date.fromisocalendar(year, week, self.day).strftime("%d/%m")
            day = Frequency.DAY_NAME_MAPPING[self.day]
            return f"Due {day} on {due_date}"
        else:
            return "Any day this week"
    
    @classmethod
    def from_str(cls, frequency: str) -> Frequency:
        matched = PERIODICALLY.match(frequency)
        if matched:
            interval = int(matched.group(1)) if matched.group(1) else 1
            day = Frequency.NAME_DAY_MAPPING.get(matched.group(2), 0)
            offset = int(matched.group(3)) if matched.group(3) else 0
            return FreqPeriodical(day, interval, offset)
        matched = SPECIFICALLY.match(frequency)
        if matched:
            day = Frequency.NAME_DAY_MAPPING.get(matched.group(1), 0)
            year = int(matched.group(2))
            week_no = set(map(int, matched.group(3).split()))
            return FreqSpecific(day, week_no, year)

    @abstractmethod
    def match(self, year: int, week: int) -> bool:
        raise NotImplementedError
    @abstractmethod
    def nth_turn(self, year: int, week: int) -> int:
        """
        Raises:
            ValueError: If the year-week combination is invalid
        """
        if not self.match(year, week): 
            raise ValueError(f"Invalid year week combination. Got {year=} and {week=}.")
    
@dataclass(slots=True)
class FreqPeriodical(Frequency):
    """
    Attributes:
        interval (int): Positive Integer. Once per `interval` week(s)
        offset (int): E.g. if the interval is 2, then if the offset is 0, 
            it would be week 2, 4, 6, etc, and if the offset is 1,
            it would be week 1, 3, 5, etc.
    """
    interval: int
    offset: int = 0
    @override
    def match(self, year, week):
        return (date.fromisocalendar(year, week, 1).toordinal() // 7 
                + self.offset) % self.interval == 0
    @override
    def nth_turn(self, year, week):
        days_from_beginning = date.fromisocalendar(year, week, 1).toordinal()
        n, invalid_year_week = divmod(days_from_beginning // 7 + self.offset, self.interval)
        if invalid_year_week:
            raise ValueError("Invalid year week combination."
                             f"Got {year=} and {week=}.")
        return n

@dataclass(slots=True)
class FreqSpecific(Frequency):
    week_no: Iterable[int]
    year: int
    @override
    def match(self, year, week):
        return year == self.year and week in self.week_no
    
    @override
    def nth_turn(self, year, week):
        week_no = sorted(self.week_no)
        n = bisect_left(week_no, week)
        if n >= len(week_no) or n != week_no[n]:
            raise ValueError("Invalid year week combination."
                             f"Got {year=} and {week=}.")
        return n    
    
    
def pick_assignees(conn: DuckDBPyConnection, year: int, week: int, chore: Chore) -> list[str] | None:
    group = [name 
             for name, is_available in get_people(conn, chore["people_group"]).items()
             if is_available]
    freq = Frequency.from_str(chore["frequency"])
    seed(hash(chore["name"]))
    shuffle(group)
    try:
        n = freq.nth_turn(year, week) * chore["assignee_count"] % len(group)
        return [group[i % len(group)] for i in range(n, n+chore["assignee_count"])]
    except ValueError:
        return None


def generate(conn: DuckDBPyConnection, year: int, week: int) -> dict[str, list[str]]:
    chores = get_all_chores(conn)
    out = {}
    for chore in chores:
        assignees = pick_assignees(conn, year, week, chore)
        if assignees:
            out[chore["name"]] = assignees
    return out

def get_schedule(
    conn_w: DuckDBPyConnection,
    year: int, 
    week: int,
) -> dict[str, dict[int, tuple[str, bool]]]:
    """Return a dictionary of assignments. Update database on demand.

    Raises:
        ValueError: If schedules at too many weeks ahead are queried.
    """
    CHORE_NAME_GETTER = itemgetter(0)
    def read_schedule(conn: DuckDBPyConnection) -> dict:
        """Might be empty. Possible if not generated yet or it is an empty week"""
        rows = conn.execute("""SELECT chores.name,
                                      assignments.id,
                                      assignments.assignee,
                                      assignments.status,
                               FROM assignments JOIN chores ON (assignments.chore_id = chores.id)
                               WHERE assignments.year = ? AND assignments.week = ?
                            """, (year, week)).fetchall()
        chore_names = set(map(CHORE_NAME_GETTER, rows))
        out = {chore_name: {} for chore_name in chore_names}
        for chore_name, id, assignee, status in rows:
            out[chore_name][id] = (assignee, status)
        return out
    if (date.fromisocalendar(year, week, 1) - date.today()).days // 7 > MAX_WEEKS_FROM_NOW:
        raise ValueError(f"Only schedules {MAX_WEEKS_FROM_NOW} weeks ahead can be queried.")
    # Though it might be read-only, but having conn_w and conn_r 
    # combined can be problematic due to check-then-act
    
    schedule = read_schedule(conn_w)
    if schedule:
        return schedule
    else:
        generation = generate(conn_w, year, week)
        if generation:
            for chore_name, assignees in generation.items():
                row = conn_w.execute("SELECT id FROM chores WHERE name = ?", (chore_name, )).fetchone()                
                if row is None:
                    raise ChoreNoFoundError(
                        f"Chore {repr(chore_name)} no found."
                        "This happens possibly because a chore is removed "
                        "during this function call. "
                        "If that is the case, a second call is unlikely "
                        "to encounter the same issue.")
                chore_id = row[0]
                for assignee in assignees:
                    conn_w.execute(
                        """INSERT INTO assignments(chore_id, week, year, assignee) 
                           VALUES (?, ?, ?, ?)""",
                        (chore_id, week, year, assignee),
                    )
            return read_schedule(conn_w)
        else:
            # It is an empty week
            return {}

def mark_done(
    conn_w: DuckDBPyConnection,
    assignment_id: int,
    assignee: str,
) -> bool:
    """
    Returns:
        bool: True if successful; False if nothing has changed.
    """
    conn_w.execute(
        """UPDATE assignments 
           SET status = true 
           WHERE id = ? 
            AND assignee = ?""",
        (assignment_id, assignee),
    )
    row = conn_w.execute(
        """SELECT 1 FROM assignments 
           WHERE id = ? AND assignee = ? AND status = true""",
        (assignment_id, assignee),
    ).fetchone()
    return row is not None

def mark_not_done(
    conn_w: DuckDBPyConnection, 
    assignment_id: int, 
    assignee: str,
) -> bool:
    """
    Returns:
        bool: True if successful; False if nothing has changed.
    """
    conn_w.execute("""UPDATE assignments 
                    SET status = false 
                    WHERE id = ? 
                        AND assignee = ?""", (assignment_id, assignee))
    row = conn_w.execute("""SELECT 1 
                            FROM assignments 
                            WHERE id = ? 
                                AND assignee = ? 
                                AND status = false""", (assignment_id, assignee)).fetchone()
    return row is not None

def remove_schedules_from_now(conn_w: DuckDBPyConnection) -> None:
    """Remove all schedules in the currect and coming weeks.
    Useful when someone left while they are still assigned for chores."""
    today = date.today()
    year, week, _ = today.isocalendar()
    # Delete any assignment in a later year, or same year with week >= current week
    conn_w.execute(
        "DELETE FROM assignments WHERE (year > ?) OR (year = ? AND week >= ?)",
        (year, year, week),
    )

def next_week(conn: DuckDBPyConnection, year: int, week: int) -> tuple[int, int] | None:
    """
    Find the next relevant week given a year/week.

    Behavior:
    - If the provided year/week is before the current ISO week:
        Search forward from the provided week up to the current week (inclusive)
        and return the first week that has at least one assignment in the DB.
        If none found, return the current week.
    - If the provided year/week is the current week or a future week:
        Search forward from the next week and return the first week that has at
        least one assignment, up to MAX_WEEKS_FROM_NOW ahead. If no such week
        exists within the allowed window, return None.

    Returns (year, week) or None when beyond MAX_WEEKS_FROM_NOW for future searches.
    """
    def next_yw(y: int, w: int) -> tuple[int, int]:
        d = date.fromisocalendar(y, w, 1) + timedelta(days=7)
        ny, nw, _ = d.isocalendar()
        return ny, nw

    today = date.today()
    cur_y, cur_w, _ = today.isocalendar()

    # helper to check DB for any assignment in the week
    def has_assignment(y: int, w: int) -> bool:
        row = conn.execute(
            "SELECT 1 FROM assignments WHERE year = ? AND week = ? LIMIT 1",
            (y, w),
        ).fetchone()
        return row is not None

    # If the requested week is in the past (strictly before current)
    if (year, week) < (cur_y, cur_w):
        y, w = year, week
        # search forward up to current week inclusive
        while (y, w) <= (cur_y, cur_w):
            if has_assignment(y, w):
                return (y, w)
            if (y, w) == (cur_y, cur_w):
                break
            y, w = next_yw(y, w)
        # none found — return current week
        return (cur_y, cur_w)

    # current or future: search forward starting from next week up to MAX_WEEKS_FROM_NOW
    y, w = next_yw(year, week)
    while True:
        # compute weeks ahead relative to today
        weeks_ahead = (date.fromisocalendar(y, w, 1) - today).days // 7
        if weeks_ahead > MAX_WEEKS_FROM_NOW:
            return None
        return (y, w)


def last_week(conn: DuckDBPyConnection, year: int, week: int) -> tuple[int, int] | None:
    """
    Find the last relevant week given a year/week.

    Behavior:
    - If the provided year/week is after the current ISO week:
        Search backward from the provided week down to the current week (inclusive)
        and return the first week (closest to the provided week going backwards)
        that has at least one assignment in the DB. If none found, return the current week.
    - If the provided year/week is the current week or a past week:
        Search backward from the previous week and return the first week that has at
        least one assignment, up to MAX_WEEKS_FROM_NOW weeks in the past. If no such
        week exists within the allowed window, return None.

    Returns (year, week) or None when beyond MAX_WEEKS_FROM_NOW for past searches.
    """
    def earliest_yw(conn: DuckDBPyConnection) -> tuple[int, int]:
        row = conn.execute(
            """SELECT year, week
                FROM assignments
                ORDER BY year ASC, week ASC
                LIMIT 1""").fetchone()
        if row is None: # No assignment at all
            return tuple(date.today().isocalendar()[:2])
        else:
            return (row[0], row[1])
    def prev_yw(y: int, w: int) -> tuple[int, int]:
        d = date.fromisocalendar(y, w, 1) - timedelta(days=7)
        py, pw, _ = d.isocalendar()
        return py, pw

    today = date.today()
    cur_y, cur_w, _ = today.isocalendar()

    def has_assignment(y: int, w: int) -> bool:
        row = conn.execute(
            "SELECT 1 FROM assignments WHERE year = ? AND week = ? LIMIT 1",
            (y, w),
        ).fetchone()
        return row is not None

    # If the requested week is in the future (strictly after current)
    if (year, week) > (cur_y, cur_w):
        return prev_yw(year, week)

    # current or past: search backward starting from previous week up to MAX_WEEKS_FROM_NOW weeks ago
    y, w = prev_yw(year, week)
    earliest = earliest_yw(conn)
    while (y, w) >= earliest:
        if has_assignment(y, w):
            return (y, w)
        y, w = prev_yw(y, w)
    return None
    
def _test():
    raise NotImplementedError
    chore = get_all_chores()[6]
    print(chore)
    freq = Frequency.from_str(chore["frequency"])
    group = [name 
             for name, is_available in get_people(chore["people_group"]).items()
             if is_available]
    freq = Frequency.from_str(chore["frequency"])
    seed(hash(chore["name"]))
    shuffle(group)
    print(group)
    for week in range(1, 53):
        print(week, generate(2025, week))
