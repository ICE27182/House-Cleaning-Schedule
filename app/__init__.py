

from .weekyear import WeekYear
from .weighted_namelist import WeightedNameList
from .how_often import HowOften, OncePerNWeek, SpecificWeeks
from .chore import Chore

# from .constants import MORE_INFO_URL_PREFIX
# from .constants import  CLEANING_SCHEDULES_URL_PREFIX
# from .constants import  BUTTONS_URL_PREFIX
# from .more_info import more_info
# from .current import buttons
# from .cleaning_schedules import cleaning_schedules
# from .index import index

# from flask import Flask


# def create_app() -> Flask:
#     app = Flask(__name__)

#     app.register_blueprint(
#         more_info, 
#         url_prefix = CLEANING_SCHEDULES_URL_PREFIX + MORE_INFO_URL_PREFIX
#     )
#     app.register_blueprint(
#         buttons, 
#         url_prefix = CLEANING_SCHEDULES_URL_PREFIX + BUTTONS_URL_PREFIX
#     )
#     # The page you can see once you access the website
#     app.register_blueprint(
#         cleaning_schedules, 
#         url_prefix = CLEANING_SCHEDULES_URL_PREFIX
#     )
#     app.register_blueprint(index)

#     return app
