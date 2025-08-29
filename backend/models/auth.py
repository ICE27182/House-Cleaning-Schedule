from duckdb import connect
import secrets
from werkzeug.security import check_password_hash, generate_password_hash
from ..db import DB_FILE

def get_token(name: str, password: str) -> str | None:
    """
    Returns the existing token or a newly generated token, which will be 
    stored. Returns None if the credentials are invalid.
    """
    with connect(DB_FILE) as conn:
        row = conn.execute(
            "SELECT id, password_hash, session_cookie_token FROM people WHERE name = ?",
            (name,),
        ).fetchone()

        if not row:
            return None

        user_id, pw_hash, token = row
        if not pw_hash or not check_password_hash(pw_hash, password):
            return None
        
        if not token:
            token = secrets.token_urlsafe(32)
            conn.execute(
                "UPDATE people SET session_cookie_token = ? WHERE id = ?",
                (token, user_id),
            )
        return token

def remove_token(token: str) -> None:
    """Remove the session cookie token if possible. 
    The function does nothing if the token does not exist."""
    with connect(DB_FILE) as conn:
        conn.execute(
            "UPDATE people SET session_cookie_token = NULL WHERE session_cookie_token = ?",
            (token,),
        )

def change_password(token: str, new_pw: str) -> bool:
    with connect(DB_FILE) as conn:
        row = conn.execute(
            "SELECT id FROM people WHERE session_cookie_token = ?",
            (token,),
        ).fetchone()

        if not row:
            return False

        user_id, = row

        new_hash = generate_password_hash(new_pw)
        conn.execute(
            "UPDATE people SET password_hash = ? WHERE id = ?",
            (new_hash, user_id),
        )
        return True

def get_person(token: str) -> None | tuple[int, str]:
    with connect(DB_FILE, read_only=True) as conn:
        row = conn.execute(
            "SELECT id, name FROM people WHERE session_cookie_token = ?",
            (token,),
        ).fetchone()
    return row
