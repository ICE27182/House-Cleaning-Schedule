from flask import Blueprint, request, jsonify
from backend.models import people, auth
from backend.db import connect_r

bp = Blueprint("people_api", __name__, url_prefix="/people")

@bp.route("/", methods=["GET"])
def get_people():
    with connect_r() as conn_r:
        return jsonify(people.get_all_people(conn_r))

# @bp.route("/add/", methods=["POST"])
# def add_person():
#     data = request.json
#     people.add_person(data["name"])
#     return jsonify({"status": "ok"})

# @bp.route("/people/<int:person_id>", methods=["DELETE"])
# def delete_person(person_id):
#     people.remove_person(person_id)
#     return jsonify({"status": "ok"})