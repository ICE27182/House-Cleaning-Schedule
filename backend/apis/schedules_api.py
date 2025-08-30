from flask import Blueprint, request, jsonify
from datetime import date

from backend.models import schedules, auth
from backend.db import connect_r, connect_w

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
        with connect_w() as conn_w:
            schedule = schedules.get_schedule(conn_w, year, week)
            due_days = schedules.get_due_str_for_chores(
                conn_w, schedule.keys(), year, week,
            )
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    # except Exception as e:
    #     print(str(e))
    #     return jsonify({"ok": False, "error": "internal error"}), 500

    return jsonify({"ok": True, "year": year, "week": week, 
                    "schedule": schedule, "due_days": due_days})

@bp.route("/max-weeks-from-now", methods=["GET"])
def query_max_weeks_from_now():
    return jsonify(schedules.MAX_WEEKS_FROM_NOW)

@bp.route("/next-week", methods=["GET"])
def next_week():
    year = request.args.get("year", type=int)
    week = request.args.get("week", type=int)
    if year is None or week is None:
        y, w, _ = date.today().isocalendar()
        if year is None:
            year = y
        if week is None:
            week = w
    with connect_r() as conn_r:
        next_week = schedules.next_week(conn_r, year, week)
        print(f"{week=}, {next_week=}")
        return jsonify({"year": next_week[0], "week": next_week[1]}
                       if next_week else None)

@bp.route("/last-week", methods=["GET"])
def last_week():
    year = request.args.get("year", type=int)
    week = request.args.get("week", type=int)
    if year is None or week is None:
        y, w, _ = date.today().isocalendar()
        if year is None:
            year = y
        if week is None:
            week = w
    with connect_r() as conn_r:
        last_week = schedules.last_week(conn_r, year, week)
        print(f"{week=}, {last_week=}")
        return jsonify({"year": last_week[0], "week": last_week[1]}
                       if last_week else None)
    

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
        with connect_w() as conn_w:
            changed = schedules.mark_done(conn_w, assignment_id, assignee)
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
        with connect_w() as conn_w:
            changed = schedules.mark_not_done(conn_w, assignment_id, assignee)
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
    with connect_w() as conn_w:
        person = auth.get_person(conn_w, token)
        if not person:
            return jsonify({"ok": False, "error": "unauthenticated"}), 401

        try:
            schedules.remove_schedules_from_now(conn_w)
        except Exception:
            return jsonify({"ok": False, "error": "internal error"}), 500

    return jsonify({"ok": True})
