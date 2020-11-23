# Flask
DEBUG = True

SERVER_NAME = "localhost.localdomain:8000"
SECRET_KEY = "insecurekeyfordev"

# SQLAlchemy
db_uri = "postgresql://hotel_api:devpassword@postgres:5432/hotel_api"
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = False
