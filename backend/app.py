from flask import Flask
from backend.apis import chores_api, people_api, schedules_api

app = Flask(__name__)

app.register_blueprint(chores_api.bp)
app.register_blueprint(people_api.bp)
app.register_blueprint(schedules_api.bp)
