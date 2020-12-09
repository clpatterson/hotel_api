from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(
    version="0.1",
    title="Asteroid Hotels API",
    doc="/docs",
    authorizations=authorizations,
)
db = SQLAlchemy()
bcrypt = Bcrypt()