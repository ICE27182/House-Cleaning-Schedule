from typing import Literal
from duckdb import DuckDBPyConnection


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
        raise ValueError(f"Invalid group. Got {repr(group)}.")
    return dict(rows)



# def add_person(name):
#     conn = get_connection()
#     conn.execute("INSERT INTO people (name) VALUES (?)", [name])

# def remove_person(person_id):
#     conn = get_connection()
#     conn.execute("DELETE FROM people WHERE id=?", [person_id])