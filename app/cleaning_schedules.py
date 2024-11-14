


from .database import record
from .current import current

from flask import Blueprint, redirect, render_template

cleaning_schedules = Blueprint("cleaning_schedules", __name__)
CLEANING_SCHEDULES_URL_PREFIX = "/cleaning_schedules"

@cleaning_schedules.route("/current_week")
def route_cleaning_schedules_current_week():
    current.this_week()
    return redirect(CLEANING_SCHEDULES_URL_PREFIX)

@cleaning_schedules.route("/next_week")
def route_cleaning_schedules_next_week():
    current.next_week()
    return redirect(CLEANING_SCHEDULES_URL_PREFIX)




@cleaning_schedules.route("/")
def route_cleaning_schedules():
    record.write()
    return render_template(
        "/cleaning_schedules/cleaning_schedules.html",
        week_no = current.week_no,
        year = current.year,
        record_table = current.html_table()
    )
