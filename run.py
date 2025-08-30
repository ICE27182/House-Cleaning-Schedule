

from backend.app import app
from backend.db import reset
reset()
print(str(app.url_map._rules_by_endpoint).replace("],", "],\n"))
app.run(host="0.0.0.0", debug=False, port=8088)

# from app import create_website, app, WeekYear, Record

# # app.compress_everything()

# website = create_website()

# from flask import redirect
# @website.route("/")
# def root_redirect():
#     weekyear = app.get_weekyear()
#     return redirect(f"/schedules/weekyear/{weekyear.week}-{weekyear.year}")


# # I shouldn't have used run for the final product tho
# # But it is just a small website, so it's probably fine
# website.run("0.0.0.0", 80)
# # website.run("::", 80)


