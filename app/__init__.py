

from .weekyear import WeekYear
from .weighted_namelist import WeightedNameList
from .how_often import HowOften, OncePerNWeek, SpecificWeeks
from .chore import Chore
from .record import Record
from .app import app
from .schedules import schedules

from flask import Flask

def create_website() -> Flask:
    website = Flask(__name__)
    website.register_blueprint(schedules)
    return website
