from flask import Blueprint, request, jsonify
from datetime import date, timedelta
from urllib.parse import unquote_plus

from backend.models import schedules, auth, changelog
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
        return jsonify({"year": last_week[0], "week": last_week[1]}
                       if last_week else None)
    

@bp.route("/mark-done", methods=["POST"])
def mark_done():
    """
    POST /mark-done?assignment_id=<int>
    Marks the assignment as done. `assignment_id` is provided as a URL query.
    Returns { ok: True } on success, { ok: False, error: ... } on failure.
    """
    assignment_id = request.args.get("assignment_id", type=int)
    if assignment_id is None:
        return jsonify({"ok": False, "error": "assignment_id (int) required as query parameter"}), 400

    with connect_w() as conn_w:
        changed = schedules.mark_done(conn_w, assignment_id)
    if not changed:
        return jsonify({"ok": False, "error": "no change (assignment not found or already done)"}), 404

    return jsonify({"ok": True})


@bp.route("/mark-not-done", methods=["POST"])
def mark_not_done():
    """
    POST /mark-not-done?assignment_id=<int>
    Marks the assignment as not done. `assignment_id` is provided as a URL query.
    """
    assignment_id = request.args.get("assignment_id", type=int)
    if assignment_id is None:
        return jsonify({"ok": False, "error": "assignment_id (int) required as query parameter"}), 400

    with connect_w() as conn_w:
        changed = schedules.mark_not_done(conn_w, assignment_id)
    if not changed:
        return jsonify({"ok": False, "error": "no change (assignment not found or already not-done)"}), 404

    return jsonify({"ok": True})


@bp.route("/reset-future-schedules", methods=["POST"])
def reset_future_schedules():
    """
    POST to remove schedules from the current week onward.
    Requires authentication via session_token cookie.
    """
    token = request.cookies.get("session_token")
    if not token:
        return jsonify({"ok": False, "error": "Unauthenticated"}), 401
    with connect_w() as conn_w:
        user = auth.get_person(conn_w, token)
        if user is None:
            return jsonify({"ok": False, "error": "Unauthenticated"}), 401
        else:
            _, username = user
        reason = request.args.get("reason", None)
        if reason:
            reason = f"because: \"{unquote_plus(reason)}\""
        else:
            reason = "for no reason"
        schedules.remove_future_schedules(conn_w)
        year, week, _ = (date.today() + timedelta(7)).isocalendar()
        changelog.add_changelog(
            conn_w,
            f"{username} has reset the schedule "
            f"from week {week}, {year} onward {reason}."
        )
    return jsonify({"ok": True})
