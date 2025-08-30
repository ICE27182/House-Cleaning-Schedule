from flask import Blueprint, request, jsonify
from datetime import date

from ..models import schedules as schedules_model
from ..models import auth as auth_model

bp = Blueprint("schedules_api", __name__, url_prefix="/schedules")


@bp.route("/", methods=["GET"])
def query_schedule():
    """
    GET /schedules?year=YYYY&week=WW
    If year/week are omitted, use current ISO year/week.
    """
    year = request.args.get("year", type=int)
    week = request.args.get("week", type=int)

    if year is None or week is None:
        y, w, _ = date.today().isocalendar()
        if year is None:
            year = y
        if week is None:
            week = w

    try:
        schedule = schedules_model.get_schedule(year, week)
        due_days = schedules_model.get_due_str_for_chores(schedule.keys(), year, week)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    # except Exception as e:
    #     print(str(e))
    #     return jsonify({"ok": False, "error": "internal error"}), 500

    return jsonify({"ok": True, "year": year, "week": week, 
                    "schedule": schedule, "due_days": due_days})


@bp.route("/mark-done", methods=["POST"])
def mark_done():
    """
    POST JSON { "assignment_id": int, "assignee": "name" }
    Returns { ok: True } on success, { ok: False, error: ... } on failure.
    """
    data = request.get_json(silent=True) or {}
    assignment_id = data.get("assignment_id")
    assignee = data.get("assignee")

    if not isinstance(assignment_id, int) or not isinstance(assignee, str) or not assignee:
        return jsonify({"ok": False, "error": "assignment_id (int) and assignee (str) required"}), 400

    try:
        changed = schedules_model.mark_done(assignment_id, assignee)
    except Exception:
        return jsonify({"ok": False, "error": "internal error"}), 500

    if not changed:
        return jsonify({"ok": False, "error": "no change (assignment not found or already done)"}), 404

    return jsonify({"ok": True})


@bp.route("/mark-not-done", methods=["POST"])
def mark_not_done():
    """
    POST JSON { "assignment_id": int, "assignee": "name" }
    """
    data = request.get_json(silent=True) or {}
    assignment_id = data.get("assignment_id")
    assignee = data.get("assignee")

    if not isinstance(assignment_id, int) or not isinstance(assignee, str) or not assignee:
        return jsonify({"ok": False, "error": "assignment_id (int) and assignee (str) required"}), 400

    try:
        changed = schedules_model.mark_not_done(assignment_id, assignee)
    except Exception:
        return jsonify({"ok": False, "error": "internal error"}), 500

    if not changed:
        return jsonify({"ok": False, "error": "no change (assignment not found or already not-done)"}), 404

    return jsonify({"ok": True})


@bp.route("/reset", methods=["POST"])
def reset_schedules_from_now():
    """
    POST to remove schedules from the current week onward.
    Requires authentication via session_token cookie.
    """
    token = request.cookies.get("session_token")
    if not token:
        return jsonify({"ok": False, "error": "unauthenticated"}), 401

    person = auth_model.get_person(token)
    if not person:
        return jsonify({"ok": False, "error": "unauthenticated"}), 401

    try:
        schedules_model.remove_schedules_from_now()
    except Exception:
        return jsonify({"ok": False, "error": "internal error"}), 500

    return jsonify({"ok": True})
