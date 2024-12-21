from app import create_app
from app import record

# When "Next Week" is pressed, future week will be generated and stored in
# records. However, any modification of future week record does not make sense
# and even though it is blank, it will simply waste memory and disk space.
# Therefore, future data will be deleted every time the program starts
# 
# As for why I store future week data in record, I am lazy. It can be optimized
record.strip_future_data(threshold=2)

app = create_app()

from flask import redirect
@app.route("/")
def root_redirect():
    return redirect("/cleaning_schedules")


# I shouldn't have used run for the final product tho
# But it is just a small website, so it's probably fine
app.run("0.0.0.0", 80)
