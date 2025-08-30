from flask import Flask, send_from_directory
from backend.apis import api

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="")

app.register_blueprint(api)
@app.route("/")
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index_page(path):
    return send_from_directory(app.static_folder, "index.html")
