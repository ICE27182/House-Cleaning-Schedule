from flask import Blueprint, Flask

app = Flask(__name__)

public = Blueprint("public", __name__)

authentication = Blueprint("Authentication", __name__, url_prefix="/api/authentication")

@authentication.route("login", methods=["POST"])
def login():
    raise NotImplementedError
@authentication.route("logout", methods=["POST"])
def logout():
    raise NotImplementedError


"""
Public
GET /api/weeks/:year/:week → all chore cards for that week
POST /api/assignments/:id/mark ({person_id})
POST /api/assignments/:id/unmark ({person_id})

Edits (auth required)
POST /api/assignments/:id/swap ({from_id, to_id})
POST /api/assignments/:id/reassign ({assignee_ids[]})
POST /api/assignments/:id/postpone ({exec_date})
POST /api/assignments/:id/skip ({reason})
POST /api/assignments/:id/note ({note})

Admin
GET  /api/pools / POST /api/pools/:pool/people (add)
PATCH /api/pools/:pool/people/:id (disable/rename/recolor/reorder)
PATCH /api/chores/:id (name, frequency, num_people, pool, notes)
POST /api/generate ({from_week, weeks_ahead})
GET  /api/export.json
"""