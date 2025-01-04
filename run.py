

from app import create_app

app = create_app()

from flask import redirect
@app.route("/")
def root_redirect():
    return redirect("/cleaning_schedules")


# I shouldn't have used run for the final product tho
# But it is just a small website, so it's probably fine
app.run("0.0.0.0", 80)
# app.run("::", 80)
