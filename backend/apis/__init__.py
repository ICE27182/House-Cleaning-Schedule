
from flask import Blueprint
from . import auth_api, changelog_api, chores_api, people_api, schedules_api

api = Blueprint("api", __name__, url_prefix="/api")
api.register_blueprint(auth_api.bp)
api.register_blueprint(changelog_api.bp)
api.register_blueprint(chores_api.bp)
api.register_blueprint(people_api.bp)
api.register_blueprint(schedules_api.bp)

__all__ = ["api"]
 