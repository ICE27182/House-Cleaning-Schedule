from flask import Blueprint, request, jsonify
from backend.models import people, auth, changelog
from backend.db import connect_r, connect_w

bp = Blueprint("people_api", __name__, url_prefix="/people")

@bp.route("/", methods=["GET"])
def get_people():
    person = request.args.get("person", None)
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
            return jsonify({"ok": False, "error": "availability is required."}), 401
        if person is None:
            return jsonify({"ok": False, "error": "person is required."}), 401
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

# @bp.route("/add/", methods=["POST"])
# def add_person():
#     data = request.json
#     people.add_person(data["name"])
#     return jsonify({"status": "ok"})

# @bp.route("/people/<int:person_id>", methods=["DELETE"])
# def delete_person(person_id):
#     people.remove_person(person_id)
#     return jsonify({"status": "ok"})