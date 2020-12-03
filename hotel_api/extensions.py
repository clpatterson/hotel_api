from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

api = Api(version="0.1", title="Asteroid Hotels API", doc="/docs")
db = SQLAlchemy()