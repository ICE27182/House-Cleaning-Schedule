from typing import Literal, override, TypedDict
from duckdb import DuckDBPyConnection
from datetime import date
class InvalidGroupError(Exception):
    @override
    def __init__(self, group: str, *args):
        super().__init__(f"Invalid group. Got {repr(group)}.")
    
class NameAlreadyExistsError(Exception):
    @override
    def __init__(self, name: str, *args):
        super().__init__(f"{name} has already existed.")

class NameNoFoundError(Exception):
    @override
    def __init__(self, name: str, *args):
        super().__init__(f"{name} does not exist.")

class Person(TypedDict):
    id: int
    name: str
    is_available: bool
    group: str
    joined_at_around: date | None
    left_at_around: date | None

def get_all_people(conn: DuckDBPyConnection) -> dict[str, dict[str, bool]]:
    rows = conn.execute("""SELECT 
                            name,
                            is_available,
                            main_gate,
                            stairs,
                            upstairs
                            FROM people""").fetchall()
    everyone, people_mg, people_s, people_u = {}, {}, {}, {}
    for name, is_available, main_gate, stairs, upstairs in rows:
        everyone[name] = is_available
        if main_gate:
            people_mg[name] = is_available
        if stairs:
            people_s[name] = is_available
        if upstairs:
            people_u[name] = is_available
    return {"everyone": everyone,
            "main_gate": people_mg,
            "stairs": people_s,
            "upstairs": people_u}
            
def get_people(
    conn: DuckDBPyConnection,
    group: Literal["everyone", "main_gate", "stairs", "upstairs"],
) -> dict[str, bool]:
    if group == "everyone":
        rows = conn.execute("SELECT name, is_available, FROM people").fetchall()
    elif group == "main_gate":
        rows = conn.execute("""SELECT 
                                name,
                                is_available,
                                FROM people
                                WHERE main_gate = true""").fetchall()
    elif group == "stairs":
        rows = conn.execute("""SELECT 
                                name,
                                is_available,
                                FROM people
                                WHERE stairs = true""").fetchall()
    elif group == "upstairs":
        rows = conn.execute("""SELECT 
                                name,
                                is_available,
                                FROM people
                                WHERE upstairs = true""").fetchall()
    else:
        raise InvalidGroupError(group)
    return dict(rows)

def get_group(main_gate: bool, stairs: bool, upstairs: bool) -> str | None:
    return {
        (False, False, False): "everyone",
        (True, False, False): "main_gate",
        (False, True, False): "stairs",        
        (False, False, True): "upstairs",
    }.get((main_gate, stairs, upstairs), None)

def get_person(conn: DuckDBPyConnection, name: str) -> Person:
    row = conn.execute(
        """SELECT 
            id, name, is_available,
            main_gate, stairs, upstairs,
            joined_at_around, left_at_around
           FROM people
           WHERE name = ?
        """,
        (name, )
    ).fetchone()
    if row is None:
        raise NameNoFoundError(name)
    (id, name, is_available,
     main_gate, stairs, upstairs,
     joined_at_around, left_at_around) = row
    return Person(
        id=id,
        name=name,
        is_available=is_available,
        group=get_group(main_gate, stairs, upstairs),
        joined_at_around=joined_at_around,
        left_at_around=left_at_around,
    )

def enable_person(conn_w: DuckDBPyConnection, name: str):
    conn_w.execute("""UPDATE people 
                      SET is_available=true 
                      WHERE name=?""", (name, ))

def disable_person(conn_w: DuckDBPyConnection, name: str):
    conn_w.execute("""UPDATE people 
                      SET is_available=false 
                      WHERE name=?""", (name, ))
    
def add_person(
    conn_w: DuckDBPyConnection, 
    name: str, 
    group: Literal["everyone", "main_gate", "stairs", "upstairs"],
) -> None:
    condition = {
        "everyone": (False, False, False), 
        "main_gate": (True, False, False), 
        "stairs": (False, True, False),
        "upstairs": (False, False, True), 
    }.get(group, None)
    if not condition:
        raise InvalidGroupError(group)
    name_exists = conn_w.execute("SELECT 1 FROM people WHERE name = ?",
                                 (name, )).fetchone()
    if name_exists:
        raise NameAlreadyExistsError(name)
    
    conn_w.execute(
        """INSERT INTO people(name, main_gate, stairs, upstairs)
        VALUES (?, ?, ?, ?)
        """,
        (name, *condition),
    )


# def remove_person(
#     conn_w: DuckDBPyConnection, 
#     name: str, 
#     group: Literal["everyone", "main_gate", "stairs", "upstairs"],
# ) -> bool:
#     conn = get_connection()
#     conn.execute("DELETE FROM people WHERE id=?", [person_id])