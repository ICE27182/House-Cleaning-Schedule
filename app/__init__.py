

from .weekyear import WeekYear
from .weighted_namelist import WeightedNameList
from .how_often import HowOften, OncePerNWeek, SpecificWeeks
from .chore import Chore
from .record import Record
from .app import app
from .schedules import schedules

# from .constants import MORE_INFO_URL_PREFIX
# from .constants import  CLEANING_SCHEDULES_URL_PREFIX
# from .constants import  BUTTONS_URL_PREFIX
# from .more_info import more_info
# from .current import buttons
# from .cleaning_schedules import cleaning_schedules
# from .index import index

from flask import Flask

# print("Compressing...")
# print(app.compress_everything())
# print("Done")

def create_website() -> Flask:
    website = Flask(__name__)
    website.register_blueprint(schedules)
    return website
