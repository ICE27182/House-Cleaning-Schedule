

from app import create_website, app, WeekYear
app._weekyear = WeekYear(16, 2025)
website = create_website()

from flask import redirect
@website.route("/")
def root_redirect():
    weekyear = app.get_weekyear()
    return redirect(f"/schedules/weekyear/{weekyear.week}-{weekyear.year}")


# I shouldn't have used run for the final product tho
# But it is just a small website, so it's probably fine
website.run("0.0.0.0", 80)
# website.run("::", 80)
