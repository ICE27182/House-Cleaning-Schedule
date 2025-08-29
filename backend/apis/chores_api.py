from flask import Blueprint, request, jsonify
from backend.models import chores

bp = Blueprint("chores_api", __name__)

@bp.route("/chores", methods=["GET"])
def get_chores():
    return jsonify(chores.get_all_chores())
