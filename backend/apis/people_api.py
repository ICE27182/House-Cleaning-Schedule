from flask import Blueprint, request, jsonify
from backend.models import people, auth, changelog
from backend.db import connect_r, connect_w
from urllib.parse import unquote_plus

bp = Blueprint("people_api", __name__, url_prefix="/people")

@bp.route("/", methods=["GET"])
def get_people():
    # accept percent-encoded queries (e.g. spaces as %20 or +)
    person = request.args.get("person", None)
    group = request.args.get("group", None)
    if person is not None:
        person = unquote_plus(person)
    if group is not None:
        group = unquote_plus(group)

    with connect_r() as conn_r:
        if person is None:
            return jsonify(people.get_all_people(conn_r))
        else:
            return jsonify(people.get_person(conn_r, person))

@bp.route("/set-availability", methods=["POST"])
def set_availability():
    token = request.cookies.get("session_token")
    if not token:
        return jsonify({"ok": False, "error": "Unauthenticated"}), 401
    with connect_w() as conn_w:
        user = auth.get_person(conn_w, token)
        if user is None:
            return jsonify({"ok": False, "error": "Unauthenticated"}), 401
        else:
            _, username = user
        data = request.get_json(silent=True) or {}
        availability = data.get("availability", None)
        person = data.get("person", None)
        if availability is None:
            return jsonify({"ok": False, "error": "availability is required."}), 400
        if person is None:
            return jsonify({"ok": False, "error": "person is required."}), 400
        if availability:
            people.enable_person(conn_w, person)
        else:
            people.disable_person(conn_w, person)
        changelog.add_changelog(
            conn_w, 
            f"{username} changed {person} to "
            f"{"" if availability else "un"}available.",
        )
    return jsonify({"ok": True})

@bp.route("/remove", methods=["DELETE"])
def remove_person():
    token = request.cookies.get("session_token")
    if not token:
        return jsonify({"ok": False, "error": "Unauthenticated"}), 401
    with connect_w() as conn_w:
        user = auth.get_person(conn_w, token)
        if user is None:
            return jsonify({"ok": False, "error": "Unauthenticated"}), 401
        else:
            _, username = user
        data = request.get_json(silent=True) or {}
        person = data.get("person", None)
        if person is None:
            return jsonify({"ok": False, "error": "person is required."}), 400
        people.remove_person(conn_w, person)
        changelog.add_changelog(
            conn_w, 
            f"{username} removed {person}.",
        )
    return jsonify({"ok": True})

@bp.route("/add/", methods=["POST"])
def add_person():
    token = request.cookies.get("session_token")
    if not token:
        return jsonify({"ok": False, "error": "Unauthenticated"}), 401
    with connect_w() as conn_w:
        user = auth.get_person(conn_w, token)
        if user is None:
            return jsonify({"ok": False, "error": "Unauthenticated"}), 401
        else:
            _, username = user
        data = request.get_json(silent=True) or {}
        person = data.get("person", None)
        group = data.get("group", None)
        if person is None:
            return jsonify({"ok": False, "error": "person is required."}), 400
        if group is None:
            return jsonify({"ok": False, "error": "group is required."}), 400
        try:
            people.add_person(conn_w, person, group)
        except people.NameAlreadyExistsError as e:
            return jsonify({"ok": False, "error": str(e)}), 409
        except people.InvalidGroupError as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        changelog.add_changelog(conn_w, f"{username} has added {person}.")
    return jsonify({"ok": True})
