

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
    app.record.save_to_json("record.json")
    print("record.json saved.")
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
    app.record.save_to_json("record.json")
    print("record.json saved.")
    return send_file("../record.json")


@schedules.route("/schedules/Access")
def route_access():
    return render_template("access.html")


@schedules.route("/schedules/admins-and-log")
def route_admin_and_log():
    return render_template("admins_and_log.html")

@schedules.route("/schedules/download/admins-log")
def route_download_admins_log():
    return send_file("../admins_log.txt")

# Two admin routes (I just realize you can use one for both 
# since they have the same number of arguments)
# But I'm too lazy to change it now

@schedules.route("/schedules/admin/<passkey>/set/<year>/<week>/<urlized_chore_name>/<name>/<status>", methods=["GET", "POST"])
def route_admin_set_confirmation(passkey: str, year: str, week: str, 
                                 urlized_chore_name: str, name: str, 
                                 status: str):
    admin_name = app.admins.validate_passkey(passkey)
    if admin_name is None:
        return "Forbidden: Invalid Passkey", 403
    chore_name = Chore.de_urlize_chore_name(urlized_chore_name)
    weekyear = WeekYear.from_str(f"{week} {year}")
    name = " ".join(name.split('-'))
    try:
        confirmation = app.confirm_admin_set(weekyear, chore_name, 
                                             name, status, past_tense=False)
    except ValueError as e:
        return str(e), 404
    confirmed = f"/schedules/admin/{passkey}/set/{year}/{week}/{urlized_chore_name}/{name}/{status}/confirmed"
    
    return render_template(
        "admin_confirmation.html",
        admin_name=admin_name,
        confirmation=confirmation,
        confirmed=confirmed,
    )

@schedules.route("/schedules/admin/<passkey>/set/<year>/<week>/<urlized_chore_name>/<name>/<status>/confirmed", methods=["GET", "POST"])
def route_admin_set_confirmed(passkey: str, year: str, week: str, 
                              urlized_chore_name: str, name: str, 
                              status: str):
    admin_name = app.admins.validate_passkey(passkey)
    if admin_name is None:
        return "Forbidden: Invalid Passkey", 403
    chore_name = Chore.de_urlize_chore_name(urlized_chore_name)
    weekyear = WeekYear.from_str(f"{week} {year}")
    name = " ".join(name.split('-'))
    try:
        log_message = app.confirm_admin_set(weekyear, chore_name, 
                                            name, status, past_tense=True)
    except ValueError as e:
        return str(e), 404
    app.execute_admin_set(weekyear, chore_name, name, status)
    app.admins.log(passkey, log_message)
    return redirect(f"/schedules/weekyear/{week}-{year}"), 200


@schedules.route("/schedules/admin/<passkey>/change/<year>/<week>/<urlized_chore_name>/<from_person>/<to_person>", methods=["GET", "POST"])
def route_admin_change_confirmation(passkey: str, year: str, week: str, 
                                    urlized_chore_name: str, 
                                    from_person: str, to_person: str):
    admin_name = app.admins.validate_passkey(passkey)
    if admin_name is None:
        return "Forbidden: Invalid Passkey", 403
    chore_name = Chore.de_urlize_chore_name(urlized_chore_name)
    weekyear = WeekYear.from_str(f"{week} {year}")
    from_name = " ".join(from_person.split('-'))
    to_name = " ".join(to_person.split('-'))
    try:
        confirmation = app.confirm_admin_change(weekyear, chore_name, 
                                                from_name, to_name, 
                                                past_tense=False)
    except ValueError as e:
        return str(e), 404
    confirmed = f"/schedules/admin/{passkey}/change/{year}/{week}/{urlized_chore_name}/{from_person}/{to_person}/confirmed"
    return render_template(
        "admin_confirmation.html",
        admin_name=admin_name,
        confirmation=confirmation,
        confirmed=confirmed,
    )

@schedules.route("/schedules/admin/<passkey>/change/<year>/<week>/<urlized_chore_name>/<from_person>/<to_person>/confirmed", methods=["GET", "POST"])
def route_admin_change_confirmed(passkey: str, year: str, week: str, 
                                 urlized_chore_name: str, 
                                 from_person: str, to_person: str):
    admin_name = app.admins.validate_passkey(passkey)
    if admin_name is None:
        return "Forbidden: Invalid Passkey", 403
    chore_name = Chore.de_urlize_chore_name(urlized_chore_name)
    weekyear = WeekYear.from_str(f"{week} {year}")
    from_name = " ".join(from_person.split('-'))
    to_name = " ".join(to_person.split('-'))
    try:
        log_message = app.confirm_admin_change(weekyear, chore_name, 
                                               from_name, to_name, 
                                               past_tense=True)
    except ValueError as e:
        return str(e), 404
    app.execute_admin_change(weekyear, chore_name, from_name, to_name)
    app.admins.log(passkey, log_message)
    return redirect(f"/schedules/weekyear/{week}-{year}")
    
