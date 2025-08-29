from duckdb import connect
from werkzeug.security import generate_password_hash
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "chores.db")

def create_tables():
    with connect(DB_FILE) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            -- Scheduling
            name TEXT UNIQUE NOT NULL,
            is_available BOOLEAN NOT NULL DEFAULT TRUE,
            -- Login
            password_hash VARCHAR,
            session_cookie_token VARCHAR DEAFULT NULL,
            -- Where
            main_gate BOOLEAN NOT NULL,
            staris BOOLEAN NOT NULL,
            upstaris BOOLEAN NOT NULL,
            - When
            joined_at_around TIMESTAMP,
            left_at_around TIMESTAMP DEFAULT NULL,
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS chores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            frequency TEXT NOT NULL,  -- "weekly", "biweekly:0", "weeks:[5,10,20]", "freq:4,offset:3"
            people_group TEXT NOT NULL -- JSON array of person_ids
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chore_id INTEGER NOT NULL REFERENCES chores(id),
            week INTEGER NOT NULL,
            year INTEGER NOT NULL,
            assignees TEXT NOT NULL, -- Doesnt reference table people for flexibility. How much larger can this db be, right
            UNIQUE(chore_id, week, year)
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS changelog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
        );
        """)
        

def fill_data():
    # TODO Convert good old json into queries
    with connect(DB_FILE) as conn:
        conn.execute("""INSERT INTO people VALUES
                        (0, ICE27182, false, ?, NULL, 
                         false, false, false, 
                         '1992-09-20 11:30:00.123456789', NULL)""",
                     generate_password_hash("P"))

if __name__ == "__main__":
    create_tables()
    fill_data()
    print("Database initialized with sample data.")