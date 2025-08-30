import duckdb
from werkzeug.security import generate_password_hash
import os
from json import load
from typing import Generator
from contextlib import contextmanager
from threading import RLock

DB_FILE = os.path.join(os.path.dirname(__file__), "chores.db")
lock = RLock()
active_conn = None
@contextmanager
def conn_r() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    global active_conn
    with lock:
        if active_conn:
            yield active_conn
        else:
            with duckdb.connect(DB_FILE, False) as conn:
                active_conn = conn
                yield conn
            active_conn = None

@contextmanager
def conn_w() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    global active_conn
    with lock:
        if active_conn:
            yield active_conn
        else:
            with duckdb.connect(DB_FILE, False) as conn:
                active_conn = conn
                yield conn
            active_conn = None


def create_tables() -> None:
    with conn_w() as conn:
        conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_people_id START 1")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_chores_id START 1")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_assignments_id START 1")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_changelog_id START 1")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY DEFAULT NEXTVAL('seq_people_id'),
            -- Scheduling
            name TEXT UNIQUE NOT NULL,
            is_available BOOLEAN NOT NULL DEFAULT true,
            -- Login
            password_hash VARCHAR,
            session_cookie_token VARCHAR DEFAULT NULL,
            -- Where
            main_gate BOOLEAN NOT NULL,
            stairs BOOLEAN NOT NULL,
            upstairs BOOLEAN NOT NULL,
            -- When
            joined_at_around TIMESTAMP,
            left_at_around TIMESTAMP DEFAULT NULL,
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS chores (
            id INTEGER PRIMARY KEY DEFAULT NEXTVAL('seq_chores_id'),
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            image_path TEXT,
            frequency TEXT NOT NULL,
            people_group TEXT NOT NULL,
            assignee_count INTEGER NOT NULL,
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY DEFAULT NEXTVAL('seq_assignments_id'),
            chore_id INTEGER NOT NULL REFERENCES chores(id),
            week INTEGER NOT NULL,
            year INTEGER NOT NULL,
            assignee TEXT NOT NULL, -- Doesnt reference table people for flexibility. How much larger can this db be, right
            status BOOLEAN NOT NULL DEFAULT false,
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS changelog (
            id INTEGER PRIMARY KEY DEFAULT NEXTVAL('seq_changelog_id'),
            description TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
        );
        """)
        
def fill_data() -> None:
    try:
        from backend.from_namelists import add_people
        add_people()
        print("PEOPLE ADDED")
    except (ModuleNotFoundError, ImportError) as e:
        print(f"NAME FALLBACK due to {e}")
        with conn_w() as conn:
            conn.execute("""INSERT INTO people VALUES
                            (0, 'ICE27182', false, ?, NULL, 
                            false, false, false, 
                            '1992-09-20 11:30:00.123456789', NULL)""",
                        (generate_password_hash("P"), ))
            conn.execute("""INSERT INTO changelog(description) VALUES
                        ('Initial log')""")
    add_chore("chores.json")
        
def reset() -> None:
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    create_tables()
    fill_data()

def add_chore(json_path: str) -> None:
    try:
        with open("chore_descriptions.json", 'r') as file:
            DESCRIPTION = load(file)
    except FileNotFoundError:
        DESCRIPTION = {"Kitchen Cleaning": "Here's the description",
                       "House Vacuuming": "Here's the description", 
                       "Basement Cleaning": "Here's the description",
                       "Glass Garbage": "Here's the description",
                       "Cardboard Garbage": "Here's the description",
                       "Organic Garbage": "Here's the description",
                       "Plastic Garbage":"Here's the description",
                       "Bathroom & Toilet - Stairs": "Here's the description",
                       "Bathroom & Toilet - Main Gate": "Here's the description",
                       "Bathroom & Toilet - Upstairs": "Here's the description"}
    with open(json_path, 'r') as json_file:
        chores = load(json_file)
    with conn_w() as conn:
        for chore in chores:
            name = chore["name"]
            if name.endswith("North"):
                name = "Bathroom & Toilet - Stairs"
            elif name.endswith("South"):
                name = "Bathroom & Toilet - Main Gate"
            elif name.endswith("Second Floor"):
                name = "Bathroom & Toilet - Upstairs"
            group = chore["namelist"]
            if group == "namelist.json":
                group = "everyone"
            elif group == "namelist_north.json":
                group = "stairs"
            elif group == "namelist_south.json":
                group = "main_gate"
            elif group == "namelist_second_floor.json":
                group = "upstairs"
            elif group not in {"everyone", "stairs", "main_gate", "upstairs"}:
                raise ValueError(f"Invalid group. Got {repr(group)}.")
            conn.execute("""INSERT INTO chores(name, description, image_path, frequency, people_group, assignee_count) VALUES (?, ?, ?, ?, ?, ?)""",
                         (name, DESCRIPTION[name], f"{name}.png", chore["how_often"], group, chore["num_of_people"]))
    