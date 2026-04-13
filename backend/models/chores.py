from typing import TypedDict
from duckdb import DuckDBPyConnection

class Chore(TypedDict):
    id: int
    name: str
    description: str | None
    frequency: str
    people_group: str
    assignee_count: int

def get_all_chores(conn: DuckDBPyConnection) -> list[Chore]:
    rows = conn.execute("SELECT id, name, description, frequency, people_group, assignee_count FROM chores").fetchall()
    return [Chore(id=row[0],
                    name=row[1],
                    description=row[2],
                    frequency=row[3],
                    people_group=row[4],
                    assignee_count=row[5]) for row in rows]
