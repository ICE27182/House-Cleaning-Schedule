from flask import request, jsonify
from functools import wraps

from backend.models import auth
from backend.db import connect_r, connect_w

def require_auth(write: bool = False):
    """
    Decorator for endpoints that require an authenticated user.

    Usage:
      @require_auth(write=True)   -> opens connect_w() and passes (conn, user) to view
      @require_auth()             -> opens connect_r() and passes (conn, user) to view

    The wrapped view must accept (conn, user, *args, **kwargs).
    On auth failure it returns a JSON 401 response.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            token = request.cookies.get("session_token")
            if not token:
                return jsonify({"ok": False, "error": "Unauthenticated"}), 401

            ctx = connect_w() if write else connect_r()
            with ctx as conn:
                user = auth.get_person(conn, token)
                if user is None:
                    return jsonify({"ok": False, "error": "Unauthenticated"}), 401
                return fn(conn, user, *args, **kwargs)
        return wrapper
    return decorator