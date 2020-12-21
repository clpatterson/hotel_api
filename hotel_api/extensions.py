from flask import Blueprint, url_for
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


# Fix mixed content error when api is served from behind https proxy
# For context see: https://github.com/python-restx/flask-restx/issues/188
class PatchedApi(Api):
    @property
    def specs_url(self):
        return url_for(self.endpoint("specs"))


api_bp = Blueprint(
    "api", __name__, url_prefix="/api/v0.1"
)  # Used to add url prefix to all routes
authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}
description = (
    "Welcome to the Asteroid Hotels API! "
    "The API can be used to search for and book stays in fictitious hotels on asteroids. "
    "Checkout the code [here](https://github.com/clpatterson/hotel_api)."
)

api = PatchedApi(
    api_bp,
    version="0.1",
    title="Asteroid Hotels API",
    description=description,
    doc="/docs",
    authorizations=authorizations,
)
db = SQLAlchemy()
bcrypt = Bcrypt()
