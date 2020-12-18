import os


class Config(object):
    DEBUG = False
    TESTING = False
    SERVER_NAME = "localhost.localdomain:8000"
    SECRET_KEY = "insecurekeyfordev"
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://hotel_api:devpassword@postgres:5432/hotel_api"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_EXPIRE_HOURS = 0
    TOKEN_EXPIRE_MINUTES = 15


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "{0}_test".format(Config.SQLALCHEMY_DATABASE_URI)
    TOKEN_EXPIRE_HOURS = 0
    TOKEN_EXPIRE_MINUTES = 0


class ProductionConfig(Config):
    SERVER_NAME = os.environ.get("SERVER_NAME", None)
    SECRET_KEY = os.environ.get("SECRET_KEY", None)
    POSTGRES_USER = os.environ.get("POSTGRES_USER", None)
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", None)
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", None)
    db_uri = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/hotel_api"
    SQLALCHEMY_DATABASE_URI = db_uri
    TOKEN_EXPIRE_HOURS = 1
    TOKEN_EXPIRE_MINUTES = 0


config = {
    "development": DevelopmentConfig(),
    "testing": TestingConfig(),
    "production": ProductionConfig(),
}
