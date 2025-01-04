

from .constants import CLEANING_SCHEDULES_URL_PREFIX
from .date_utils import get_today_weekyear, week_difference
from .type_utils import weekyear_to_date
from .database import record
from .current import current
from .constants import NUM_FUTURE_WEEKS_SCHEDULE

from datetime import date
from flask import Blueprint, redirect, render_template

cleaning_schedules = Blueprint("cleaning_schedules", __name__)

"""
Two Buttons on the cleaning schedule page used to nevigate through current
and future weeks
"""
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



"""
The main page
"""
@cleaning_schedules.route("/")
def route_cleaning_schedules():
    # When entering the main page, the page shows the schedule of the week
    # stored in `current`. `current` will reset every two minutes if no link is
    # clicked.
    week_year = current.get_weekyear()
    # Just in case someone navigated to a future week and did not go back
    # to the current week, and another person visit the website before 
    # `current` reset, they can see the week number in red so it is less likely
    # for them to mistake the schedule shown for the ongoing schedule
    if get_today_weekyear() != week_year:
        week_year = f"<span class=\"red\">{week_year}</span>"
    
    if (week_difference(weekyear_to_date(current.get_weekyear()), date.today())
        < 
        NUM_FUTURE_WEEKS_SCHEDULE):
        next_week = """
            <th class="right">
                <a href="/cleaning_schedules/next_week">Next Week</a>
            </th>
        """ 
    else:
        next_week = ""
    # `record` will write to the disk every time the page is reloaded
    record.write()
    return render_template(
        CLEANING_SCHEDULES_URL_PREFIX + "/cleaning_schedules.html",
        week_year = week_year,
        record_table = current.html_table(),
        next_week = next_week,
        num_future_weeks_schedule = NUM_FUTURE_WEEKS_SCHEDULE,
    )



"""
The part explaining why we cannot visit the website via a domain or without
connection to the house wifi
"""
@cleaning_schedules.route("/ip_and_domain")
def route_ip_and_domain():
    return render_template(
        CLEANING_SCHEDULES_URL_PREFIX + "/ip_and_domain.html",   
    )
