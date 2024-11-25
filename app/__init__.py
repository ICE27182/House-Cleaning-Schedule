
from .more_info import more_info, MORE_INFO_URL_PREFIX
from .current import buttons, BUTTONS_URL_PREFIX
from .cleaning_schedules import cleaning_schedules, CLEANING_SCHEDULES_URL_PREFIX
from .index import index
# record is imported here so I can strip unnecessary future data in run.py
from .database import record

from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)

    app.register_blueprint(more_info, url_prefix = CLEANING_SCHEDULES_URL_PREFIX + MORE_INFO_URL_PREFIX)
    app.register_blueprint(buttons, url_prefix = CLEANING_SCHEDULES_URL_PREFIX + BUTTONS_URL_PREFIX)
    # The page you can see once you access the website
    app.register_blueprint(cleaning_schedules, url_prefix = CLEANING_SCHEDULES_URL_PREFIX)
    app.register_blueprint(index)

    return app
