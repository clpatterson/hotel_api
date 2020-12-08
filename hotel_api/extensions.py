from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

api = Api(version="0.1", title="Asteroid Hotels API", doc="/docs")
db = SQLAlchemy()
bcrypt = Bcrypt()