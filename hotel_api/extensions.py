from flask import url_for
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

# Fix mixed content error when api is served from behind https proxy
# For context see: https://github.com/python-restx/flask-restx/issues/188
class PatchedApi(Api):
    @property
    def specs_url(self):
        return url_for(self.endpoint("specs"))


api = PatchedApi(version="0.1", title="Asteroid Hotels API", doc="/docs")
db = SQLAlchemy()