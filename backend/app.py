from flask import Flask
from backend.apis import api

app = Flask(__name__)

app.register_blueprint(api)
