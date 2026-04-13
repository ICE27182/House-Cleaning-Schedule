from backend.db import connect_w

with connect_w() as conn_w:
    print(conn_w.execute("SELECT id, name FROM chores").fetchall())
    print(conn_w.execute("SELECT * FROM assignments WHERE assignee='Askel' AND week=40 AND year=2025 and chore_id=3").fetchall())
    conn_w.execute("UPDATE assignments SET assignee='Minh' WHERE assignee='Askel' AND week=40 AND year=2025 and chore_id=3")