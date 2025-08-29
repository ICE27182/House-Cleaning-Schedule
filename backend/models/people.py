from backend.db import conn_r, conn_w

def get_all_people() -> dict[str, dict[str, bool]]:
    with conn_r() as conn:
        rows = conn.execute("""SELECT 
                                name,
                                is_available,
                                main_gate,
                                staris,
                                upstaris 
                               FROM people""").fetchall()
    everyone, people_mg, people_s, people_u = {}, {}, {}, {}
    for name, is_available, main_gate, staris, upstaris in rows:
        everyone[name] = is_available
        if main_gate:
            people_mg[name] = is_available
        if staris:
            people_s[name] = is_available
        if upstaris:
            people_u[name] = is_available
    return {"everyone": everyone,
            "main_gate": people_mg,
            "stairs": people_s,
            "upstairs": people_u}
            
    


# def add_person(name):
#     conn = get_connection()
#     conn.execute("INSERT INTO people (name) VALUES (?)", [name])

# def remove_person(person_id):
#     conn = get_connection()
#     conn.execute("DELETE FROM people WHERE id=?", [person_id])