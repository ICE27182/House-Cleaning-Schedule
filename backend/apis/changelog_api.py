from flask import Blueprint, request, jsonify
from datetime import datetime, timezone, timedelta

from ..models import changelog as changelog_model

bp = Blueprint("changelog", __name__, url_prefix="/changelog")


def _normalize_iso(s: str) -> str:
    # Accept trailing "Z" as UTC
    return s.replace("Z", "+00:00") if s.endswith("Z") else s


@bp.route("/", methods=["GET"])
def list_changelog():
    """
    GET /changelog?from=<ISO>&to=<ISO>&limit=<n>
    - from: ISO datetime string (optional, defaults to 30 days ago)
    - to: ISO datetime string (optional, defaults to now UTC)
    - limit: integer (optional, will slice the results)

    Returns JSON: { ok: True, entries: [{ created_at: ISO, description: str }, ...] }
    """
    q_from: str | None = request.args.get("from")
    q_to: str | None = request.args.get("to")
    limit = request.args.get("limit", type=int)

    now_utc = datetime.now(timezone.utc)

    # defaults
    if q_to is None:
        q_to_iso = now_utc.isoformat()
    else:
        q_to_iso = _normalize_iso(q_to)

    if q_from is None:
        q_from_iso = (now_utc - timedelta(days=30)).isoformat()
    else:
        q_from_iso = _normalize_iso(q_from)

    # validate ISO strings
    try:
        # datetime.fromisoformat will raise on invalid formats; accept it as validation
        datetime.fromisoformat(q_from_iso)
        datetime.fromisoformat(q_to_iso)
    except Exception:
        return jsonify({"ok": False, "error": "invalid ISO datetime in query parameters"}), 400

    entries = changelog_model.get_changelog(q_from_iso, q_to_iso)

    # apply optional limit (entries are already ordered newest-first in model)
    if isinstance(limit, int) and limit > 0:
        entries = entries[:limit]

    out = []
    for created_at, desc in entries:
        if isinstance(created_at, datetime):
            created_str = created_at.isoformat()
        else:
            created_str = str(created_at)
        out.append({"created_at": created_str, "description": desc})

    return jsonify({"ok": True, "entries": out})
