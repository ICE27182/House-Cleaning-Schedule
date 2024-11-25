

from .url_prefixes import CLEANING_SCHEDULES_URL_PREFIX
from .date_utils import todays_week_year
from .database import record
from .current import current

from flask import Blueprint, redirect, render_template

cleaning_schedules = Blueprint("cleaning_schedules", __name__)


@cleaning_schedules.route("/current_week")
def route_cleaning_schedules_current_week():
    current.reset_to_current_week()
    current.reset_timer(120)
    return redirect(CLEANING_SCHEDULES_URL_PREFIX)

@cleaning_schedules.route("/next_week")
def route_cleaning_schedules_next_week():
    current.next_week()
    current.reset_timer(120)
    return redirect(CLEANING_SCHEDULES_URL_PREFIX)




@cleaning_schedules.route("/")
def route_cleaning_schedules():
    week_year = current.week_year()
    if todays_week_year() != week_year:
        week_year = f"<span class=\"red\">{week_year}</span>"
    record.write()
    return render_template(
        CLEANING_SCHEDULES_URL_PREFIX + "/cleaning_schedules.html",
        week_year = week_year,
        record_table = current.html_table(current.week_year())
    )



@cleaning_schedules.route("/ip_and_domain")
def route_ip_and_domain():
    return render_template(
        CLEANING_SCHEDULES_URL_PREFIX + "/ip_and_domain.html",   
    )
