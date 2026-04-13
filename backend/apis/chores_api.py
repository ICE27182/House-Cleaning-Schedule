from flask import Blueprint, request, jsonify
from backend.models import chores
from backend.db import connect_r

bp = Blueprint("chores_api", __name__)

@bp.route("/chores", methods=["GET"])
def get_chores():
    with connect_r() as conn_r:
        return jsonify(chores.get_all_chores(conn_r))
