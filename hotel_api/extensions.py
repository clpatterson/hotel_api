from flask import Blueprint
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

api_bp = Blueprint(
    "api", __name__, url_prefix="/api/v0.1"
)  # Used to add url prefix to all routes
authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(
    api_bp,
    version="0.1",
    title="Asteroid Hotels API",
    description="Welcome to the Asteroid Hotels api documentation site!",
    doc="/docs",
    authorizations=authorizations,
)
db = SQLAlchemy()
bcrypt = Bcrypt()