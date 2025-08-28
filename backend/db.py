from duckdb import connect
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
            session_cookie_token VARCHAR,
            -- Where
            main_gate BOOLEAN NOT NULL,
            staris BOOLEAN NOT NULL,
            upstaris BOOLEAN NOT NULL,
            - When
            joined_at_around TIMESTAMP,
            left_at_around TIMESTAMP,
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
        raise NotImplementedError
        conn.execute("INSERT OR IGNORE INTO people (name) VALUES ('Alice'), ('Bob'), ('Charlie');")
        conn.execute("""
            INSERT OR IGNORE INTO chores (name, description, frequency, people_group)
            VALUES 
            ('Dishes', 'Wash dishes after dinner', 'weekly', '[1,2,3]'),
            ('Trash', 'Take out trash', 'biweekly', '[1,2,3]');
        """)

if __name__ == "__main__":
    create_tables()
    fill_data()
    print("Database initialized with sample data.")