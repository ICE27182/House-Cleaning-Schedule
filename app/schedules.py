

from .chore import Chore
from .app import app
from .weekyear import WeekYear


from flask import Blueprint, render_template, send_file, redirect
from os import getcwd
from os.path import dirname, exists

schedules = Blueprint("schedules", __name__)

@schedules.route("/schedules/weekyear/<weekyear_str>", methods=["GET", "POST"])
def route_schedules(weekyear_str:str):
    week, year = weekyear_str.split("-")
    weekyear = WeekYear(week=int(week), year=int(year))
    
    # title color, app.get_weekyear()
    
    table = app.get_table_for_weekyear(weekyear)
    if table is None:
        return "Forbidden", 403

    return render_template(
        "schedules.html",
        week_year=app.get_weekyear_title(weekyear),
        last_week_button=app.get_last_week_button(weekyear),
        current_week_button=app.get_current_week_button(),
        next_week_button=app.get_next_week_button(weekyear),
        main_table=app.get_table_for_weekyear(weekyear),
    )

@schedules.route("/schedules/update-record/<which>", methods=["GET", "POST"])
def route_update_record(which: str):
    """
    which: week-year-urlized(chore_name)--name
    """
    chore_info, person_name = which.split("--")
    chore_info= chore_info.split("-")
    week, year = chore_info[:2]
    chore_name = Chore.de_urlize_chore_name("-".join(chore_info[2:]))
    weekyear = WeekYear(int(week), int(year))
    person_name = " ".join(person_name.split('-'))
    app.record.flip_status(weekyear, chore_name, person_name)
    return redirect(app.get_link_to_this_weekyear())



@schedules.route("/schedules/more-info/<urlized_chore_name>", 
                 methods=["GET", "POST"])
def route_more_info(urlized_chore_name: str):
    app.ensure_more_info_html_exists(urlized_chore_name)
    chore_name = Chore.de_urlize_chore_name(urlized_chore_name)
    app.get_more_info_table(chore_name)
    return render_template(
        f"more_info/{urlized_chore_name}.html",
        task_name=chore_name,
        more_info_table=app.get_more_info_table(chore_name),
    )

@schedules.route("/schedules/download/everything", methods=["GET"])
def route_download_everything():
    arhive_path = f"{dirname(getcwd())}/archive.zip"
    if not exists(arhive_path):
        print(app.compress_everything())
    return send_file(arhive_path)

@schedules.route("/schedules/download/record.json", methods=["GET"])
def route_download_record_json():
    return send_file("../record.json")
