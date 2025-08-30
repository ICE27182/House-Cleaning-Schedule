from flask import Blueprint, request, jsonify, make_response

from backend.db import connect_w, connect_r
from backend.models import auth

from ..db import DB_FILE

bp = Blueprint("auth_api", __name__, url_prefix="/auth")


@bp.route("/login", methods=["POST"])
def login():
    """
    POST JSON { "name": "...", "password": "..." }
    Sets a httpOnly cookie "session_token" on success.
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    password = data.get("password")

    if not name or not password:
        return jsonify({"ok": False, "error": "missing credentials"}), 400
    
    with connect_w() as conn_w:
        token = auth.get_token(conn_w, name, password)
    if token is None:
        return jsonify({"ok": False, "error": "invalid credentials"}), 401

    resp = make_response(jsonify({"ok": True, "name": name}))
    resp.set_cookie("session_token", token, httponly=True, samesite="Lax")
    return resp


@bp.route("/logout", methods=["POST"])
def logout():
    """
    POST to logout. Will clear server-side token and cookie if present.
    Accepts token from cookie or JSON { "session_token": "..." } 
    for flexibility.
    """
    token = (request.cookies.get("session_token")
             or (request.get_json(silent=True) or {}).get("session_token"))
    
    with connect_w() as conn_w:
        auth.remove_token(conn_w, token)

    resp = make_response(jsonify({"ok": True}))
    resp.set_cookie("session_token", "", expires=0)
    return resp


@bp.route("/change-password", methods=["POST"])
def change_password():
    """
    POST JSON:
      { "new_password": "..." }

    Requirements:
      - Must be authenticated via session_token cookie.
      - new_password must be non-empty.

    Returns { ok: True } on success.
    """
    token = request.cookies.get("session_token")
    if not token:
        return jsonify({"ok": False, "error": "unauthenticated"}), 401

    data = request.get_json(silent=True) or {}
    new_pw = data.get("new_password")
    if not new_pw or not isinstance(new_pw, str):
        return jsonify({"ok": False, "error": "new_password required"}), 400
    
    with connect_w() as conn_w:
        password_changed = auth.change_password(conn_w, token, new_pw)

    if password_changed:
        return jsonify({"ok": True})
    else:
        return jsonify({"ok": False, "error": "unauthenticated"}), 401


@bp.route("/me", methods=["GET"])
def whoami():
    """
    Return basic user info for the current session token (from cookie).
    """
    token = request.cookies.get("session_token")
    if not token:
        return jsonify({"ok": False, "error": "unauthenticated"}), 401

    with connect_r() as conn_r:
        person = auth.get_person(conn_r, token)
        
    if person:
        return jsonify({"ok": True, "id": person[0], "name": person[1]})
    else:
        return jsonify({"ok": False, "error": "unauthenticated"}), 401