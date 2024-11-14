
from .more_info import more_info, MORE_INFO_URL_PREFIX
from .buttons import buttons, BUTTONS_URL_PREFIX
from .cleaning_schedules import cleaning_schedules, CLEANING_SCHEDULES_URL_PREFIX

from flask import Flask

def create_app() -> Flask:
    app = Flask(__name__)

    app.register_blueprint(more_info, url_prefix = MORE_INFO_URL_PREFIX)
    app.register_blueprint(cleaning_schedules, url_prfix = CLEANING_SCHEDULES_URL_PREFIX)
    app.register_blueprint(buttons, url_prefix = BUTTONS_URL_PREFIX)

    return app
