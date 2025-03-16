

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
    website.add_url_rule("/click-me", view_func=route_click_me)
    return website

def route_click_me():
    from os import listdir, getcwd
    from random import choice
    from flask import send_file
    pool = f"{getcwd()}/app/static/images/pool/"
    file_chosen = f"{pool}{choice(listdir("app/static/images/pool/"))}"
    print(f"Sending {file_chosen=}")
    return send_file(file_chosen)
